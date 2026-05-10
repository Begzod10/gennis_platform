from rest_framework import serializers

from website_sources.models import (
    ComponentDefinition,
    DynamicForm,
    GlobalSetting,
    MediaAsset,
    Menu,
    News,
    Admission,
    ContactMessage,
    Page,
    PageSection,
    ReusableBlock,
    ThemeSetting,
    Translation,
)


ROLE_GROUP_MAP = {
    'admin': {'admin', 'administrator', 'manager', 'director'},
    'teacher': {'teacher', 'teachers', 'ustoz'},
    'student': {'student', 'students', 'oquvchi'},
}


def get_request_role(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return 'guest'
    if user.is_superuser or user.is_staff:
        return 'admin'

    group_names = {group.name.lower() for group in user.groups.all()}
    for role, names in ROLE_GROUP_MAP.items():
        if group_names.intersection(names):
            return role
    return 'student'


def get_request_permissions(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return set()
    return set(user.get_all_permissions())


def is_visible(rule, role, permissions):
    if not rule:
        return True

    roles = rule.get('roles') or []
    if roles and role not in roles:
        return False

    required_permissions = rule.get('permissions') or []
    if required_permissions and not set(required_permissions).issubset(permissions):
        return False

    audience = rule.get('audience')
    if audience == 'authenticated' and role == 'guest':
        return False
    if audience == 'staff' and role not in {'admin', 'teacher'}:
        return False

    return True


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'slug']


class AdmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admission
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'application_id']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'
        read_only_fields = ['created_at']


class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ['id', 'key', 'uz', 'ru', 'en', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ComponentDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentDefinition
        fields = [
            'id',
            'key',
            'name',
            'description',
            'props_schema',
            'default_props',
            'allowed_roles',
            'is_layout',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class ThemeSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeSetting
        fields = [
            'id',
            'name',
            'mode',
            'tokens',
            'branch',
            'is_default',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'key', 'name', 'items', 'branch', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ReusableBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReusableBlock
        fields = ['id', 'key', 'name', 'sections', 'branch', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PageSectionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    component_key = serializers.CharField(source='component.key', read_only=True)

    class Meta:
        model = PageSection
        fields = [
            'id',
            'page',
            'component',
            'component_key',
            'parent',
            'section_id',
            'props',
            'layout',
            'visibility',
            'responsive',
            'sort_order',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class PageSerializer(serializers.ModelSerializer):
    sections = PageSectionSerializer(many=True, required=False)

    class Meta:
        model = Page
        fields = [
            'id',
            'slug',
            'title',
            'locale',
            'status',
            'seo',
            'permissions',
            'cache',
            'theme',
            'navigation',
            'footer',
            'branch',
            'version',
            'sections',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        sections_data = validated_data.pop('sections', None)
        
        # Update page fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if sections_data is not None:
            # Handle sections CRUD
            keep_section_ids = []
            for section_data in sections_data:
                section_id = section_data.get('id')
                if section_id:
                    # Update existing section
                    section_item = PageSection.objects.get(id=section_id, page=instance)
                    for attr, value in section_data.items():
                        setattr(section_item, attr, value)
                    section_item.save()
                    keep_section_ids.append(section_item.id)
                else:
                    # Create new section
                    new_section = PageSection.objects.create(page=instance, **section_data)
                    keep_section_ids.append(new_section.id)
            
            # Delete removed sections
            instance.sections.exclude(id__in=keep_section_ids).delete()
            
        return instance


class DynamicFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicForm
        fields = [
            'id',
            'key',
            'title',
            'fields',
            'submit_endpoint',
            'success_message',
            'branch',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class MediaAssetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = ['id', 'file', 'url', 'alt', 'metadata', 'branch', 'created_at']
        read_only_fields = ['created_at']

    def get_url(self, obj):
        request = self.context.get('request')
        if not obj.file:
            return None
        url = obj.file.url
        return request.build_absolute_uri(url) if request else url


class GlobalSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSetting
        fields = ['id', 'key', 'value', 'branch', 'updated_at']
        read_only_fields = ['updated_at']


class PageRenderSerializer(serializers.ModelSerializer):
    theme = serializers.SerializerMethodField()
    navigation = serializers.SerializerMethodField()
    footer = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()
    reusableBlocks = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            'slug',
            'title',
            'version',
            'locale',
            'seo',
            'theme',
            'navigation',
            'footer',
            'sections',
            'reusableBlocks',
            'permissions',
            'cache',
        ]

    def _role(self):
        return self.context.get('role') or get_request_role(self.context.get('request'))

    def _permissions(self):
        return self.context.get('permissions') or get_request_permissions(self.context.get('request'))

    def _serialize_section(self, section):
        role = self._role()
        permissions = self._permissions()

        if not section.is_active or not section.component.is_active:
            return None

        if not is_visible(section.visibility, role, permissions):
            return None

        allowed_roles = section.component.allowed_roles or []
        if allowed_roles and role not in allowed_roles:
            return None

        children = []
        for child in section.children.all():
            child_payload = self._serialize_section(child)
            if child_payload:
                children.append(child_payload)

        payload = {
            'id': section.section_id or str(section.pk),
            'type': section.component.key,
            'props': {
                **(section.component.default_props or {}),
                **(section.props or {}),
            },
        }

        if children:
            payload['children'] = children
        if section.layout:
            payload['layout'] = section.layout
        if section.visibility:
            payload['visibility'] = section.visibility
        if section.responsive:
            payload['responsive'] = section.responsive

        return payload

    def get_theme(self, obj):
        theme = obj.theme
        if not theme:
            theme = ThemeSetting.objects.filter(
                is_default=True,
                branch=obj.branch,
            ).first() or ThemeSetting.objects.filter(is_default=True, branch__isnull=True).first()

        if not theme:
            return None

        return {
            'mode': theme.mode,
            **(theme.tokens or {}),
        }

    def get_navigation(self, obj):
        if not obj.navigation or not obj.navigation.is_active:
            return None
        return obj.navigation.items

    def get_footer(self, obj):
        if not obj.footer or not obj.footer.is_active:
            return None
        return obj.footer.sections

    def get_sections(self, obj):
        roots = obj.sections.filter(parent__isnull=True).select_related('component').prefetch_related(
            'children__component',
            'children__children__component',
        )
        sections = []
        for section in roots:
            payload = self._serialize_section(section)
            if payload:
                sections.append(payload)
        return sections

    def get_reusableBlocks(self, obj):
        qs = ReusableBlock.objects.filter(is_active=True, branch__isnull=True)
        blocks = {block.key: block.sections for block in qs}

        if obj.branch_id:
            branch_blocks = ReusableBlock.objects.filter(
                is_active=True,
                branch_id=obj.branch_id,
            )
            for block in branch_blocks:
                blocks[block.key] = block.sections
        return blocks
