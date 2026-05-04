from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from website_sources.models import News, Category, Admission, ContactMessage, CareerApplication, JobPosition
from website_sources.serializers import NewsListSerializer, PublicNewsSerializer, CategorySerializer, \
    AdmissionSerializer, AdmissionCreateSerializer, ContactMessageSerializer, ContactCreateSerializer, \
    CareerApplicationSerializer, JobPositionSerializer, TalentPoolSerializer


def apply_news_filters(qs, params):
    """
    Barcha news filterlari bir joyda.

    Query params:
      branch       — ?branch=1                  (branch ID)
      published    — ?published=true/false       (chiqarilgan / qoralama)
      category     — ?category=Announcements     (nomi bo'yicha, icontains)
      category_id  — ?category_id=3              (kategoriya ID)
      search       — ?search=olimpiada           (title + description ichida)
      date_from    — ?date_from=2026-01-01       (shu sanadan keyin)
      date_to      — ?date_to=2026-12-31         (shu sanagacha)
      ordering     — ?ordering=-created_at       (- belgisi teskari tartib)
                      mavjud: created_at, date, views, title
      created_by   — ?created_by=5               (admin: kim yaratgan, user ID)
    """
    branch_id = params.get('branch')
    published = params.get('published')
    category = params.get('category')
    category_id = params.get('category_id')
    search = params.get('search')
    date_from = params.get('date_from')
    date_to = params.get('date_to')
    ordering = params.get('ordering', '-created_at')
    created_by = params.get('created_by')

    if branch_id:
        qs = qs.filter(branch_id=branch_id)

    if published is not None:
        if published.lower() == 'true':
            qs = qs.filter(published=True)
        elif published.lower() == 'false':
            qs = qs.filter(published=False)

    if category_id:
        qs = qs.filter(category_id=category_id)
    elif category:
        qs = qs.filter(category__name__icontains=category)

    if search:
        from django.db.models import Q
        qs = qs.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        ).distinct()

    if date_from:
        parsed = parse_date(date_from)
        if parsed:
            qs = qs.filter(date__gte=parsed)

    if date_to:
        parsed = parse_date(date_to)
        if parsed:
            qs = qs.filter(date__lte=parsed)

    if created_by:
        qs = qs.filter(created_by_id=created_by)

    allowed = {'created_at', '-created_at', 'date', '-date', 'views', '-views', 'title', '-title'}
    if ordering in allowed:
        qs = qs.order_by(ordering)

    return qs


# ─── ADMIN VIEWS ──────────────────────────────────────────────────────────────

class NewsListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/news/    — barcha yangiliklar (admin)
    POST /api/news/    — yangilik yaratish (admin)

    Filterlar:
      ?branch=1
      ?published=true | false
      ?category=Events           (nomi bo'yicha)
      ?category_id=3             (ID bo'yicha)
      ?search=matnsoxta          (title + desc ichida)
      ?date_from=2026-01-01
      ?date_to=2026-12-31
      ?ordering=-views           (eng ko'p ko'rilgan birinchi)
      ?created_by=5              (muayyan admin tomonidan yaratilganlar)
    """
    serializer_class = NewsListSerializer

    def get_queryset(self):
        qs = News.objects.select_related('category', 'branch', 'created_by')
        return apply_news_filters(qs, self.request.query_params)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class NewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/news/:id/
    PUT    /api/news/:id/
    DELETE /api/news/:id/
    """
    queryset = News.objects.select_related('category', 'branch', 'created_by')
    serializer_class = NewsListSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Deleted successfully"},
            status=status.HTTP_200_OK
        )


class NewsTogglePublishView(APIView):
    """
    PATCH /api/news/:id/toggle-publish/
    """

    def patch(self, request, pk):
        news = get_object_or_404(News, pk=pk)
        news.published = not news.published
        news.save(update_fields=['published'])
        return Response({
            'success': True,
            'message': 'News publish status updated',
            'data': {'id': news.id, 'published': news.published}
        })


# ─── IMAGE UPLOAD ─────────────────────────────────────────────────────────────

class ImageUploadView(APIView):
    """
    POST /api/upload/image/
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'success': False, 'message': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
        if file.content_type not in allowed_types:
            return Response(
                {'success': False, 'message': 'File type not allowed. Use: JPG, PNG, WebP, GIF'},
                status=status.HTTP_400_BAD_REQUEST
            )

        max_size = 5 * 1024 * 1024  # 5MB
        if file.size > max_size:
            return Response(
                {'success': False, 'message': 'File size exceeds 5MB limit'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.core.files.storage import default_storage
        import time
        filename = f"uploads/images/{int(time.time())}-{file.name}"
        saved_path = default_storage.save(filename, file)
        file_url = request.build_absolute_uri(default_storage.url(saved_path))

        return Response({
            'success': True,
            'message': 'Image uploaded successfully',
            'url': file_url
        })


# ─── PUBLIC VIEWS ─────────────────────────────────────────────────────────────

class PublicNewsListView(generics.ListAPIView):
    """
    GET /api/public/news/    — faqat published=True yangiliklar

    Filterlar:
      ?branch=1
      ?category=Events
      ?category_id=2
      ?search=yangilik
      ?date_from=2026-01-01
      ?date_to=2026-12-31
      ?ordering=-views        (trending — eng ko'p o'qilganlar birinchi)
      ?ordering=-date         (eng yangilari birinchi, default)
    """
    serializer_class = PublicNewsSerializer

    def get_queryset(self):
        qs = News.objects.filter(published=True).select_related('category', 'branch')
        return apply_news_filters(qs, self.request.query_params)


class PublicNewsDetailView(APIView):
    """
    GET /api/public/news/:id/
    GET /api/public/news/slug/:slug/
    """

    def get(self, request, pk=None, slug=None):
        if pk:
            news = get_object_or_404(News, pk=pk, published=True)
        else:
            news = get_object_or_404(News, slug=slug, published=True)

        News.objects.filter(pk=news.pk).update(views=news.views + 1)
        news.refresh_from_db()

        serializer = PublicNewsSerializer(news, context={'request': request})
        return Response({'success': True, 'data': serializer.data})


# ─── CATEGORIES ───────────────────────────────────────────────────────────────


class CategoryListView(generics.ListAPIView):
    """
    GET /api/categories/

    Filterlar:
      ?branch=1    — faqat shu branchda yangilik bo'lgan kategoriyalar
    """
    serializer_class = CategorySerializer

    def get_queryset(self):
        qs = Category.objects.all()
        branch_id = self.request.query_params.get('branch')
        if branch_id:
            qs = qs.filter(news__branch_id=branch_id, news__published=True).distinct()
        return qs


class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/admin/categories/   — barcha kategoriyalar (admin)
    POST /api/admin/categories/   — yangi kategoriya yaratish (admin)

    POST body:
      { "name": "Achievements", "branch": 1 }

    Filterlar (GET):
      ?branch=1    — shu branchga tegishli kategoriyalar
      ?search=ann  — nomi bo'yicha qidiruv
    """
    serializer_class = CategorySerializer

    def get_queryset(self):
        qs = Category.objects.all()
        branch_id = self.request.query_params.get('branch')
        search = self.request.query_params.get('search')
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/admin/categories/:id/   — bitta kategoriya
    PUT    /api/admin/categories/:id/   — yangilash
    PATCH  /api/admin/categories/:id/   — qisman yangilash
    DELETE /api/admin/categories/:id/   — o'chirish

    ESLATMA: Kategoriyani o'chirishda unga bog'liq
    yangiliklardagi category maydoni NULL ga o'tadi
    (News modelida on_delete=SET_NULL).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Deleted successfully"},
            status=status.HTTP_200_OK
        )


def apply_admission_filters(qs, params):
    """
    Query params:
      branch       — ?branch=1
      status       — ?status=pending | contacted | enrolled | rejected
      search       — ?search=Ali       (ism yoki telefon raqami bo'yicha)
      grade        — ?grade=Grade 5    (sinf bo'yicha)
      date_from    — ?date_from=2026-01-01
      date_to      — ?date_to=2026-12-31
      ordering     — ?ordering=-created_at | created_at
    """
    branch_id = params.get('branch')
    status_f = params.get('status')
    search = params.get('search')
    grade = params.get('grade')
    date_from = params.get('date_from')
    date_to = params.get('date_to')
    ordering = params.get('ordering', '-created_at')

    if branch_id:
        qs = qs.filter(branch_id=branch_id)

    if status_f:
        qs = qs.filter(status=status_f)

    if grade:
        qs = qs.filter(grade__icontains=grade)

    if search:
        from django.db.models import Q
        qs = qs.filter(
            Q(student_name__icontains=search) | Q(phone__icontains=search)
        ).distinct()

    if date_from:
        parsed = parse_date(date_from)
        if parsed:
            qs = qs.filter(created_at__date__gte=parsed)

    if date_to:
        parsed = parse_date(date_to)
        if parsed:
            qs = qs.filter(created_at__date__lte=parsed)

    allowed = {'created_at', '-created_at'}
    if ordering in allowed:
        qs = qs.order_by(ordering)

    return qs


class PublicAdmissionCreateView(APIView):
    """
    POST /api/admissions/   — public, auth talab etilmaydi
    """

    def post(self, request):
        serializer = AdmissionCreateSerializer(data=request.data)
        if serializer.is_valid():
            admission = serializer.save()
            return Response({
                'success': True,
                'message': 'Application submitted successfully. Our admissions team will contact you within 24 hours.',
                'applicationId': admission.application_id
            }, status=status.HTTP_201_CREATED)
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class AdminAdmissionListView(generics.ListAPIView):
    """
    GET /api/admin/admissions/

    Filterlar:
      ?branch=1
      ?status=pending | contacted | enrolled | rejected
      ?search=Ali              (ism yoki telefon)
      ?grade=Grade 5
      ?date_from=2026-01-01
      ?date_to=2026-12-31
      ?ordering=-created_at
    """
    serializer_class = AdmissionSerializer

    def get_queryset(self):
        qs = Admission.objects.select_related('branch')
        return apply_admission_filters(qs, self.request.query_params)


class AdminAdmissionDetailView(generics.RetrieveAPIView):
    """
    GET /api/admin/admissions/:id/
    """
    queryset = Admission.objects.select_related('branch')
    serializer_class = AdmissionSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Deleted successfully"},
            status=status.HTTP_200_OK
        )


class AdminAdmissionStatusView(APIView):
    """
    PATCH /api/admin/admissions/:id/status/
    Body: { "status": "contacted", "notes": "..." }
    """

    def patch(self, request, pk):
        admission = get_object_or_404(Admission, pk=pk)
        new_status = request.data.get('status')
        valid_statuses = ['pending', 'contacted', 'enrolled', 'rejected']
        if new_status not in valid_statuses:
            return Response(
                {'success': False, 'message': f'Status must be one of: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        admission.status = new_status
        notes = request.data.get('notes')
        if notes:
            admission.notes = notes
        admission.save(update_fields=['status', 'notes'] if notes else ['status'])
        serializer = AdmissionSerializer(admission)
        return Response({'success': True, 'data': serializer.data})


def apply_contact_filters(qs, params):
    """
    Query params:
      branch     — ?branch=1
      status     — ?status=unread | read | replied
      search     — ?search=Ali           (ism yoki email bo'yicha)
      date_from  — ?date_from=2026-01-01
      date_to    — ?date_to=2026-12-31
      ordering   — ?ordering=-created_at | created_at
    """
    branch_id = params.get('branch')
    status_f = params.get('status')
    search = params.get('search')
    date_from = params.get('date_from')
    date_to = params.get('date_to')
    ordering = params.get('ordering', '-created_at')

    if branch_id:
        qs = qs.filter(branch_id=branch_id)

    if status_f:
        qs = qs.filter(status=status_f)

    if search:
        from django.db.models import Q
        qs = qs.filter(
            Q(name__icontains=search) | Q(email__icontains=search)
        ).distinct()

    if date_from:
        parsed = parse_date(date_from)
        if parsed:
            qs = qs.filter(created_at__date__gte=parsed)

    if date_to:
        parsed = parse_date(date_to)
        if parsed:
            qs = qs.filter(created_at__date__lte=parsed)

    allowed = {'created_at', '-created_at'}
    if ordering in allowed:
        qs = qs.order_by(ordering)

    return qs


class PublicContactCreateView(APIView):
    """
    POST /api/contact/   — public
    """

    def post(self, request):
        serializer = ContactCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Your message has been sent successfully. We will contact you soon.'
            }, status=status.HTTP_201_CREATED)
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class AdminContactListView(generics.ListAPIView):
    """
    GET /api/admin/contacts/

    Filterlar:
      ?branch=1
      ?status=unread | read | replied
      ?search=Ali              (ism yoki email)
      ?date_from=2026-01-01
      ?date_to=2026-12-31
      ?ordering=-created_at
    """
    serializer_class = ContactMessageSerializer

    def get_queryset(self):
        qs = ContactMessage.objects.select_related('branch')
        return apply_contact_filters(qs, self.request.query_params)


class AdminContactStatusView(APIView):
    """
    PATCH /api/admin/contacts/:id/status/
    Body: { "status": "read" }
    """

    def patch(self, request, pk):
        contact = get_object_or_404(ContactMessage, pk=pk)
        new_status = request.data.get('status')
        valid_statuses = ['unread', 'read', 'replied']
        if new_status not in valid_statuses:
            return Response(
                {'success': False, 'message': f'Status must be one of: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        contact.status = new_status
        contact.save(update_fields=['status'])
        serializer = ContactMessageSerializer(contact)
        return Response({'success': True, 'data': serializer.data})


def apply_position_filters(qs, params):
    """
    Query params:
      branch          — ?branch=1
      type            — ?type=Academic | Non-Academic
      is_active       — ?is_active=true | false
      search          — ?search=teacher       (title + description)
      employment_type — ?employment_type=Full-time
      deadline_from   — ?deadline_from=2026-01-01
      deadline_to     — ?deadline_to=2026-12-31
      ordering        — ?ordering=-posted_date | posted_date | deadline
    """
    branch_id = params.get('branch')
    type_f = params.get('type')
    is_active = params.get('is_active')
    search = params.get('search')
    employment_type = params.get('employment_type')
    deadline_from = params.get('deadline_from')
    deadline_to = params.get('deadline_to')
    ordering = params.get('ordering', '-posted_date')

    if branch_id:
        qs = qs.filter(branch_id=branch_id)

    if type_f:
        qs = qs.filter(type=type_f)

    if is_active is not None:
        qs = qs.filter(is_active=(is_active.lower() == 'true'))

    if employment_type:
        qs = qs.filter(employment_type__icontains=employment_type)

    if search:
        from django.db.models import Q
        qs = qs.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        ).distinct()

    if deadline_from:
        parsed = parse_date(deadline_from)
        if parsed:
            qs = qs.filter(deadline__gte=parsed)

    if deadline_to:
        parsed = parse_date(deadline_to)
        if parsed:
            qs = qs.filter(deadline__lte=parsed)

    allowed = {'posted_date', '-posted_date', 'deadline', '-deadline', 'title', '-title'}
    if ordering in allowed:
        qs = qs.order_by(ordering)

    return qs


def apply_application_filters(qs, params):
    """
    Query params:
      branch     — ?branch=1
      status     — ?status=pending | reviewing | shortlisted | rejected | hired
      position   — ?position=3        (position ID)
      search     — ?search=Ali        (ism yoki email)
      date_from  — ?date_from=2026-01-01
      date_to    — ?date_to=2026-12-31
      ordering   — ?ordering=-created_at
    """
    branch_id = params.get('branch')
    status_f = params.get('status')
    position = params.get('position')
    search = params.get('search')
    date_from = params.get('date_from')
    date_to = params.get('date_to')
    ordering = params.get('ordering', '-created_at')

    if branch_id:
        qs = qs.filter(branch_id=branch_id)

    if status_f:
        qs = qs.filter(status=status_f)

    if position:
        qs = qs.filter(position_id=position)

    if search:
        from django.db.models import Q
        qs = qs.filter(
            Q(name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search)
        ).distinct()

    if date_from:
        parsed = parse_date(date_from)
        if parsed:
            qs = qs.filter(created_at__date__gte=parsed)

    if date_to:
        parsed = parse_date(date_to)
        if parsed:
            qs = qs.filter(created_at__date__lte=parsed)

    allowed = {'created_at', '-created_at'}
    if ordering in allowed:
        qs = qs.order_by(ordering)

    return qs


# ─── JOB POSITIONS ────────────────────────────────────────────────────────────

class PublicJobPositionListView(generics.ListAPIView):
    """
    GET /api/careers/positions/   — public, faqat active

    Filterlar:
      ?branch=1
      ?type=Academic | Non-Academic
      ?employment_type=Full-time
      ?search=teacher
      ?deadline_from=2026-01-01
      ?deadline_to=2026-12-31
      ?ordering=-posted_date | deadline
    """
    serializer_class = JobPositionSerializer

    def get_queryset(self):
        qs = JobPosition.objects.filter(is_active=True).select_related('branch')
        return apply_position_filters(qs, self.request.query_params)


class AdminJobPositionListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/admin/careers/positions/
    POST /api/admin/careers/positions/

    Filterlar (GET):
      ?branch=1
      ?type=Academic | Non-Academic
      ?is_active=true | false
      ?employment_type=Full-time
      ?search=teacher
      ?deadline_from, ?deadline_to
      ?ordering=-posted_date
    """
    serializer_class = JobPositionSerializer

    def get_queryset(self):
        qs = JobPosition.objects.select_related('branch')
        return apply_position_filters(qs, self.request.query_params)


class AdminJobPositionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/admin/careers/positions/:id/
    PUT    /api/admin/careers/positions/:id/
    DELETE /api/admin/careers/positions/:id/
    """
    queryset = JobPosition.objects.select_related('branch')
    serializer_class = JobPositionSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Deleted successfully"},
            status=status.HTTP_200_OK
        )


# ─── CV SUBMIT ────────────────────────────────────────────────────────────────

class PublicCareerApplyView(APIView):
    """
    POST /api/careers/apply/
    """

    def post(self, request):
        serializer = CareerApplicationSerializer(data=request.data)
        if serializer.is_valid():
            application = serializer.save()
            return Response({
                'success': True,
                'message': 'Your application has been submitted successfully',
                'applicationId': application.application_id
            }, status=status.HTTP_201_CREATED)
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


# ─── TALENT POOL ──────────────────────────────────────────────────────────────

class PublicTalentPoolView(APIView):
    """
    POST /api/careers/talent-pool/
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = TalentPoolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Thank you! Your profile has been added to our talent pool.'
            }, status=status.HTTP_201_CREATED)
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


# ─── ADMIN APPLICATIONS ───────────────────────────────────────────────────────

class AdminCareerApplicationListView(generics.ListAPIView):
    """
    GET /api/admin/careers/applications/

    Filterlar:
      ?branch=1
      ?status=pending | reviewing | shortlisted | rejected | hired
      ?position=3              (position ID)
      ?search=Ali              (ism, email yoki telefon)
      ?date_from=2026-01-01
      ?date_to=2026-12-31
      ?ordering=-created_at
    """
    serializer_class = CareerApplicationSerializer

    def get_queryset(self):
        qs = CareerApplication.objects.select_related('position', 'branch')
        return apply_application_filters(qs, self.request.query_params)


class AdminStatsView(APIView):
    """
    GET /api/admin/stats/

    Filterlar:
      ?branch=1   — faqat shu branch statistikasi
    """

    def get(self, request):
        branch_id = request.query_params.get('branch')

        def bf(qs):
            """branch filter"""
            return qs.filter(branch_id=branch_id) if branch_id else qs

        news_qs = bf(News.objects.all())
        admissions_qs = bf(Admission.objects.all())
        contacts_qs = bf(ContactMessage.objects.all())
        applications_qs = bf(CareerApplication.objects.all())
        positions_qs = bf(JobPosition.objects.all())

        data = {
            'news': {
                'total': news_qs.count(),
                'published': news_qs.filter(published=True).count(),
                'drafts': news_qs.filter(published=False).count(),
            },
            'admissions': {
                'total': admissions_qs.count(),
                'pending': admissions_qs.filter(status='pending').count(),
                'contacted': admissions_qs.filter(status='contacted').count(),
                'enrolled': admissions_qs.filter(status='enrolled').count(),
                'rejected': admissions_qs.filter(status='rejected').count(),
            },
            'contacts': {
                'total': contacts_qs.count(),
                'unread': contacts_qs.filter(status='unread').count(),
                'read': contacts_qs.filter(status='read').count(),
                'replied': contacts_qs.filter(status='replied').count(),
            },
            'careers': {
                'applications': applications_qs.count(),
                'pending': applications_qs.filter(status='pending').count(),
                'shortlisted': applications_qs.filter(status='shortlisted').count(),
                'hired': applications_qs.filter(status='hired').count(),
                'positions': positions_qs.filter(is_active=True).count(),
            },
        }

        return Response({'success': True, 'data': data})
