from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from website_sources.cms_serializers import (
    ComponentDefinitionSerializer,
    DynamicFormSerializer,
    GlobalSettingSerializer,
    MediaAssetSerializer,
    MenuSerializer,
    PageRenderSerializer,
    PageSectionSerializer,
    PageSerializer,
    ReusableBlockSerializer,
    ThemeSettingSerializer,
    TranslationSerializer,
    NewsSerializer,
    AdmissionSerializer,
    ContactMessageSerializer,
    get_request_permissions,
    get_request_role,
    is_visible,
)
from website_sources.models import (
    ComponentDefinition,
    Translation,
    DynamicForm,
    GlobalSetting,
    MediaAsset,
    Menu,
    Page,
    PageSection,
    ReusableBlock,
    ThemeSetting,
    Translation,
    News,
    Admission,
    ContactMessage,
)


class AdminTranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    permission_classes = [IsAdminUser]


class AdminNewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.select_related('category', 'branch', 'created_by')
    serializer_class = NewsSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AdminAdmissionViewSet(viewsets.ModelViewSet):
    queryset = Admission.objects.select_related('branch')
    serializer_class = AdmissionSerializer
    permission_classes = [IsAdminUser]


class AdminContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.select_related('branch')
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAdminUser]


class AdminComponentDefinitionViewSet(viewsets.ModelViewSet):
    queryset = ComponentDefinition.objects.all()
    serializer_class = ComponentDefinitionSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'key'


class AdminThemeSettingViewSet(viewsets.ModelViewSet):
    queryset = ThemeSetting.objects.select_related('branch')
    serializer_class = ThemeSettingSerializer
    permission_classes = [IsAdminUser]


class AdminMenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.select_related('branch')
    serializer_class = MenuSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'key'


class AdminReusableBlockViewSet(viewsets.ModelViewSet):
    queryset = ReusableBlock.objects.select_related('branch')
    serializer_class = ReusableBlockSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'key'


class AdminPageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.select_related('theme', 'navigation', 'footer', 'branch', 'created_by').prefetch_related(
        'sections__component',
    )
    serializer_class = PageSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], url_path='render')
    def render_preview(self, request, pk=None):
        page = self.get_object()
        serializer = PageRenderSerializer(
            page,
            context={
                'request': request,
                'role': get_request_role(request),
                'permissions': get_request_permissions(request),
            },
        )
        return Response(serializer.data)


class AdminPageSectionViewSet(viewsets.ModelViewSet):
    queryset = PageSection.objects.select_related('page', 'component', 'parent')
    serializer_class = PageSectionSerializer
    permission_classes = [IsAdminUser]


class AdminDynamicFormViewSet(viewsets.ModelViewSet):
    queryset = DynamicForm.objects.select_related('branch')
    serializer_class = DynamicFormSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'key'


class AdminMediaAssetViewSet(viewsets.ModelViewSet):
    queryset = MediaAsset.objects.select_related('branch')
    serializer_class = MediaAssetSerializer
    permission_classes = [IsAdminUser]


class AdminGlobalSettingViewSet(viewsets.ModelViewSet):
    queryset = GlobalSetting.objects.select_related('branch')
    serializer_class = GlobalSettingSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'key'


class PageRenderView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        locale = request.query_params.get('locale', 'uz')
        branch = request.query_params.get('branch')
        role = get_request_role(request)
        permissions = get_request_permissions(request)

        pages = Page.objects.filter(slug=slug, locale=locale, status='published').select_related(
            'theme',
            'navigation',
            'footer',
            'branch',
        ).prefetch_related('sections__component', 'sections__children__component')

        if branch:
            pages = pages.filter(Q(branch_id=branch) | Q(branch__isnull=True))

        page = pages.order_by('-branch_id', '-version').first()
        if not page:
            return Response({'detail': 'Page not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not is_visible(page.permissions, role, permissions):
            return Response({'detail': 'Page is not available for this user.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PageRenderSerializer(
            page,
            context={
                'request': request,
                'role': role,
                'permissions': permissions,
            },
        )
        response = Response(serializer.data)
        ttl = (page.cache or {}).get('ttlSeconds', 60)
        response['Cache-Control'] = f'public, max-age={ttl}, stale-while-revalidate=300'
        response['ETag'] = f'W/"cms-page-{page.pk}-{page.version}-{page.updated_at.timestamp()}"'
        response['X-CMS-Version'] = str(page.version)
        if page.branch_id:
            response['X-Branch-ID'] = str(page.branch_id)
        return response


class CurrentThemeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        branch = request.query_params.get('branch')
        qs = ThemeSetting.objects.filter(is_default=True)
        if branch:
            qs = qs.filter(Q(branch_id=branch) | Q(branch__isnull=True))
        else:
            qs = qs.filter(branch__isnull=True)
        theme = qs.order_by('-branch_id').first()
        if not theme:
            return Response({}, status=status.HTTP_200_OK)
        return Response({'mode': theme.mode, **(theme.tokens or {})})


class NavigationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, key):
        branch = request.query_params.get('branch')
        menus = Menu.objects.filter(key=key, is_active=True)
        if branch:
            menus = menus.filter(Q(branch_id=branch) | Q(branch__isnull=True))
        else:
            menus = menus.filter(branch__isnull=True)
        menu = get_object_or_404(menus.order_by('-branch_id'))
        return Response({'key': menu.key, 'items': menu.items})


class ReusableBlockView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, key):
        branch = request.query_params.get('branch')
        blocks = ReusableBlock.objects.filter(key=key, is_active=True)
        if branch:
            blocks = blocks.filter(Q(branch_id=branch) | Q(branch__isnull=True))
        else:
            blocks = blocks.filter(branch__isnull=True)
        block = get_object_or_404(blocks.order_by('-branch_id'))
        return Response({'key': block.key, 'sections': block.sections})


class DynamicFormSubmitView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, key):
        branch = request.query_params.get('branch')
        forms = DynamicForm.objects.filter(key=key, is_active=True)
        if branch:
            forms = forms.filter(Q(branch_id=branch) | Q(branch__isnull=True))
        else:
            forms = forms.filter(branch__isnull=True)
        form = get_object_or_404(forms.order_by('-branch_id'))
        return Response(
            {
                'success': True,
                'message': form.success_message or 'Form submitted successfully.',
                'data': request.data,
            },
            status=status.HTTP_202_ACCEPTED,
        )
class PublicGlobalSettingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, key):
        branch = request.query_params.get('branch')
        settings = GlobalSetting.objects.filter(key=key)
        if branch:
            settings = settings.filter(Q(branch_id=branch) | Q(branch__isnull=True))
        else:
            settings = settings.filter(branch__isnull=True)
        
        setting = settings.order_by('-branch_id').first()
        if not setting:
            return Response({'key': key, 'value': {}})
        return Response({'key': setting.key, 'value': setting.value})
