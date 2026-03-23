from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiExample, OpenApiResponse,
)
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from group.models import Group
from students.models import Student
from .filters import StudentFilter
from .models import (
    Party, PartyMember, PartyTask, PartyTaskGrade,
    Competition, CompetitionResult, )
from .serializers import (
    PartyListSerializer, PartyDetailSerializer,
    PartyMemberSerializer, PartyMemberWriteSerializer,
    PartyTaskSerializer, PartyTaskGradeSerializer,
    CompetitionSerializer, CompetitionResultSerializer,
    StudentSelectSerializer, GroupSelectSerializer,
)


class StudentSelectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSelectSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['user__name', 'user__surname']
    filterset_class = StudentFilter

    @extend_schema(
        summary="Student select options",
        description="Frontend `<Select>` uchun `[{id, label, born_date}]` qaytaradi.",
        responses={200: StudentSelectSerializer(many=True)},
        tags=['select-options'],
    )
    @action(detail=False, methods=['get'], url_path='select')
    def select(self, request):
        qs = self.filter_queryset(self.get_queryset())
        return Response(StudentSelectSerializer(qs, many=True).data)


class GroupSelectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSelectSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'color_name']
    filterset_fields = ['branch']

    @extend_schema(
        summary="Guruh select options",
        description=(
                "Frontend `<Select>` uchun `[{id, label}]` qaytaradi.\n\n"
                "**label logikasi:** `group.name` bo'sh bo'lsa → `class_number + color_name`"
        ),
        responses={200: GroupSelectSerializer(many=True)},
        tags=['select-options'],
    )
    @action(detail=False, methods=['get'], url_path='select')
    def select(self, request):
        qs = self.filter_queryset(self.get_queryset())
        return Response(GroupSelectSerializer(qs, many=True).data)


@extend_schema_view(
    list=extend_schema(
        summary="Partiyalar ro'yxati",
        description="Har bir partiyada `display_name`, `members_count`, `wins_count`, `tasks_count`, `groups_count` bo'ladi.",
        responses={200: PartyListSerializer(many=True)},
        tags=['parties'],
    ),
    create=extend_schema(
        summary="Yangi partiya yaratish",
        description="`students` va `groups` — ID lar massivi.",
        request=PartyDetailSerializer,
        responses={201: PartyDetailSerializer},
        examples=[
            OpenApiExample(
                "Misol",
                value={
                    "name": "Burgut partiyasi",
                    "color": "#10b981",
                    "desc": "Kuchli partiya",
                    "students": [1, 2, 3],
                    "groups": [5, 6],
                },
                request_only=True,
            ),
        ],
        tags=['parties'],
    ),
    retrieve=extend_schema(
        summary="Partiya batafsil (memberships + groups)",
        responses={200: PartyDetailSerializer},
        tags=['parties'],
    ),
    update=extend_schema(
        summary="Partiyani to'liq yangilash (PUT)",
        request=PartyDetailSerializer,
        responses={200: PartyDetailSerializer},
        tags=['parties'],
    ),
    partial_update=extend_schema(
        summary="Partiyani qisman yangilash (PATCH)",
        request=PartyDetailSerializer,
        responses={200: PartyDetailSerializer},
        tags=['parties'],
    ),
    destroy=extend_schema(
        summary="Partiyani o'chirish",
        responses={204: None},
        tags=['parties'],
    ),
)
class PartyViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        return (
            Party.objects
            .prefetch_related('students', 'groups', 'memberships__student', 'tasks', 'competition_results')
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return PartyListSerializer
        return PartyDetailSerializer

    @extend_schema(
        summary="Partiya select options",
        description="Topshiriq modal va musobaqa modali uchun `[{label, value, color}]`.",
        responses={200: OpenApiTypes.OBJECT},
        tags=['parties'],
    )
    @action(detail=False, methods=['get'], url_path='select-options')
    def select_options(self, request):
        data = Party.objects.values('id', 'name', 'color')
        return Response([
            {'label': p['name'], 'value': p['id'], 'color': p['color']}
            for p in data
        ])

    @extend_schema(
        summary="Reyting sahifasi — ball bo'yicha tartiblangan",
        responses={200: PartyListSerializer(many=True)},
        tags=['parties'],
    )
    @action(detail=False, methods=['get'], url_path='rating')
    def rating(self, request):
        qs = Party.objects.order_by('-ball').prefetch_related('students', 'groups', 'competition_results', 'tasks')
        return Response(PartyListSerializer(qs, many=True).data)

    @extend_schema(
        summary="Partiyaga studentlar qo'shish",
        request={'application/json': {'type': 'object', 'properties': {
            'student_ids': {'type': 'array', 'items': {'type': 'integer'}},
        }, 'required': ['student_ids']}},
        responses={200: OpenApiResponse(description="{'added': [1,2,3]}")},
        tags=['parties'],
    )
    @action(detail=True, methods=['post'], url_path='add-students')
    def add_students(self, request, pk=None):
        party = self.get_object()
        student_ids = request.data.get('student_ids', [])

        added = []
        for sid in student_ids:
            try:
                student = Student.objects.get(id=sid)
                member, created = PartyMember.objects.get_or_create(
                    party=party, student=student,
                    defaults={'is_active': True},
                )
                party.students.add(student)
                added.append(sid)
            except Student.DoesNotExist:
                pass

        return Response({'added': added})

    @extend_schema(
        summary="Partiyadan studentni chiqarish",
        request={'application/json': {'type': 'object', 'properties': {
            'student_ids': {'type': 'array', 'items': {'type': 'integer'}},
        }, 'required': ['student_ids']}},
        responses={200: OpenApiResponse(description="{'removed': [1,2]}")},
        tags=['parties'],
    )
    @action(detail=True, methods=['post'], url_path='remove-students')
    def remove_students(self, request, pk=None):
        party = self.get_object()
        student_ids = request.data.get('student_ids', [])
        party.students.remove(*student_ids)
        PartyMember.objects.filter(party=party, student_id__in=student_ids).update(is_active=False)
        return Response({'removed': student_ids})

    @extend_schema(
        summary="Partiyaga guruhlar qo'shish / almashtirish",
        request={'application/json': {'type': 'object', 'properties': {
            'group_ids': {'type': 'array', 'items': {'type': 'integer'}},
        }, 'required': ['group_ids']}},
        responses={200: OpenApiResponse(description="{'groups': [5,6]}")},
        tags=['parties'],
    )
    @action(detail=True, methods=['post'], url_path='set-groups')
    def set_groups(self, request, pk=None):
        party = self.get_object()
        group_ids = request.data.get('group_ids', [])
        party.groups.set(group_ids)
        return Response({'groups': group_ids})

    @extend_schema(
        summary="A'zo balini o'zgartirish (+10 / -10)",
        description="`delta` musbat yoki manfiy bo'ladi.",
        request={'application/json': {'type': 'object', 'properties': {
            'member_id': {'type': 'integer'},
            'delta': {'type': 'integer', 'example': 10},
        }, 'required': ['member_id', 'delta']}},
        responses={200: PartyMemberSerializer},
        tags=['parties'],
    )
    @action(detail=True, methods=['post'], url_path='adjust-ball')
    def adjust_ball(self, request, pk=None):
        party = self.get_object()
        member_id = request.data.get('member_id')
        delta = int(request.data.get('delta', 0))
        try:
            member = PartyMember.objects.get(id=member_id, party=party)
            member.ball = max(0, member.ball + delta)
            member.save(update_fields=['ball'])
            return Response(PartyMemberSerializer(member).data)
        except PartyMember.DoesNotExist:
            return Response({'error': "A'zo topilmadi"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    list=extend_schema(
        summary="Barcha a'zolar ro'yxati",
        parameters=[
            OpenApiParameter('party', OpenApiTypes.INT, description="Partiya ID bo'yicha filter"),
            OpenApiParameter('student', OpenApiTypes.INT, description="Student ID bo'yicha filter"),
        ],
        tags=['members'],
    ),
    create=extend_schema(summary="Yangi a'zo qo'shish", tags=['members']),
    retrieve=extend_schema(summary="A'zo ma'lumotlari", tags=['members']),
    update=extend_schema(summary="A'zoni yangilash", tags=['members']),
    partial_update=extend_schema(summary="A'zoni qisman yangilash", tags=['members']),
    destroy=extend_schema(summary="A'zoni o'chirish", tags=['members']),
)
class PartyMemberViewSet(viewsets.ModelViewSet):
    queryset = PartyMember.objects.select_related('party', 'student').all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return PartyMemberWriteSerializer
        return PartyMemberSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        party_id = self.request.query_params.get('party')
        student_id = self.request.query_params.get('student')
        if party_id:
            qs = qs.filter(party_id=party_id)
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs


@extend_schema_view(
    list=extend_schema(
        summary="Topshiriqlar ro'yxati",
        description="`parties_info` — biriktirilgan partiyalar, `grades` — baholash natijalari.",
        tags=['party-tasks'],
    ),
    create=extend_schema(
        summary="Yangi topshiriq yaratish",
        examples=[
            OpenApiExample("Misol", value={
                "name": "Matematika musobaqa",
                "ball": 100,
                "deadline": "2025-06-01",
                "parties": [1, 2, 3],
            }, request_only=True),
        ],
        tags=['party-tasks'],
    ),
    retrieve=extend_schema(summary="Topshiriq batafsil", tags=['party-tasks']),
    update=extend_schema(summary="Topshiriqni yangilash", tags=['party-tasks']),
    partial_update=extend_schema(summary="Topshiriqni qisman yangilash", tags=['party-tasks']),
    destroy=extend_schema(summary="Topshiriqni o'chirish", tags=['party-tasks']),
)
class PartyTaskViewSet(viewsets.ModelViewSet):
    queryset = PartyTask.objects.all().prefetch_related('parties', 'grades')
    serializer_class = PartyTaskSerializer

    @extend_schema(
        summary="Bitta partiyaga ball berish",
        request={'application/json': {'type': 'object', 'properties': {
            'party': {'type': 'integer'},
            'ball': {'type': 'integer'},
        }, 'required': ['party', 'ball']}},
        responses={200: PartyTaskGradeSerializer, 201: PartyTaskGradeSerializer},
        tags=['party-tasks'],
    )
    @action(detail=True, methods=['post'], url_path='grade')
    def grade(self, request, pk=None):
        task = self.get_object()
        party_id = request.data.get('party')
        ball = request.data.get('ball')
        if party_id is None or ball is None:
            return Response({'error': 'party va ball majburiy'}, status=400)
        try:
            party = Party.objects.get(id=party_id)
        except Party.DoesNotExist:
            return Response({'error': 'Partiya topilmadi'}, status=404)
        grade, created = PartyTaskGrade.objects.update_or_create(
            task=task, party=party, defaults={'ball': int(ball)}
        )
        self._recalc_party_ball(party)
        code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(PartyTaskGradeSerializer(grade).data, status=code)

    @extend_schema(
        summary="Barcha partiyalarga bir vaqtda ball berish (Saqlash tugmasi)",
        request={'application/json': {'type': 'object', 'properties': {
            'grades': {'type': 'array', 'items': {'type': 'object', 'properties': {
                'party': {'type': 'integer'},
                'ball': {'type': 'integer'},
            }}},
        }}},
        responses={200: PartyTaskGradeSerializer(many=True)},
        examples=[
            OpenApiExample("Misol", value={
                "grades": [{"party": 1, "ball": 85}, {"party": 2, "ball": 70}]
            }, request_only=True),
        ],
        tags=['party-tasks'],
    )
    @action(detail=True, methods=['post'], url_path='bulk-grade')
    def bulk_grade(self, request, pk=None):
        task = self.get_object()
        grades_data = request.data.get('grades', [])
        results = []
        parties_to_recalc = set()
        for g in grades_data:
            try:
                party = Party.objects.get(id=g['party'])
                grade, _ = PartyTaskGrade.objects.update_or_create(
                    task=task, party=party, defaults={'ball': int(g['ball'])}
                )
                results.append(PartyTaskGradeSerializer(grade).data)
                parties_to_recalc.add(party)
            except (Party.DoesNotExist, KeyError, ValueError):
                pass
        for party in parties_to_recalc:
            self._recalc_party_ball(party)
        return Response(results)

    def _recalc_party_ball(self, party):
        total = PartyTaskGrade.objects.filter(party=party).aggregate(t=Sum('ball'))['t'] or 0
        party.ball = total
        party.save(update_fields=['ball'])


@extend_schema_view(
    list=extend_schema(summary="Musobaqa turlari", tags=['competitions']),
    create=extend_schema(summary="Yangi musobaqa turi", tags=['competitions']),
    retrieve=extend_schema(summary="Musobaqa batafsil", tags=['competitions']),
    update=extend_schema(summary="Musobaqani yangilash", tags=['competitions']),
    partial_update=extend_schema(summary="Musobaqani qisman yangilash", tags=['competitions']),
    destroy=extend_schema(summary="Musobaqani o'chirish", tags=['competitions']),
)
class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all().prefetch_related('results')
    serializer_class = CompetitionSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Musobaqa natijalari",
        parameters=[
            OpenApiParameter('competition', OpenApiTypes.INT, description="Musobaqa ID"),
            OpenApiParameter('quarter', OpenApiTypes.STR, description="1-chorak | 2-chorak | 3-chorak | 4-chorak"),
        ],
        tags=['competition-results'],
    ),
    create=extend_schema(
        summary="Natija qo'shish (mode: add | replace)",
        tags=['competition-results'],
    ),
    retrieve=extend_schema(summary="Natija batafsil", tags=['competition-results']),
    update=extend_schema(summary="Natijani yangilash", tags=['competition-results']),
    partial_update=extend_schema(summary="Natijani qisman yangilash", tags=['competition-results']),
    destroy=extend_schema(summary="Natijani o'chirish", tags=['competition-results']),
)
class CompetitionResultViewSet(viewsets.ModelViewSet):
    queryset = CompetitionResult.objects.all()
    serializer_class = CompetitionResultSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        comp_id = self.request.query_params.get('competition')
        quarter = self.request.query_params.get('quarter')
        if comp_id:
            qs = qs.filter(competition_id=comp_id)
        if quarter:
            qs = qs.filter(quarter=quarter)
        return qs

    def create(self, request, *args, **kwargs):
        comp_id = request.data.get('competition')
        party_id = request.data.get('party')
        quarter = request.data.get('quarter')
        ball = int(request.data.get('ball', 0))
        note = request.data.get('note', '')
        mode = request.data.get('mode', 'add')

        existing = CompetitionResult.objects.filter(
            competition_id=comp_id, party_id=party_id, quarter=quarter
        ).first()

        if existing:
            existing.ball = existing.ball + ball if mode == 'add' else ball
            if note:
                existing.note = note
            existing.save()
            self._update_winner(comp_id, quarter)
            return Response(CompetitionResultSerializer(existing).data, status=200)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self._update_winner(comp_id, quarter)
        return Response(serializer.data, status=201)

    def _update_winner(self, competition_id, quarter):
        totals = (
            CompetitionResult.objects
            .filter(competition_id=competition_id, quarter=quarter)
            .values('party_id')
            .annotate(total=Sum('ball'))
            .order_by('-total')
        )
        CompetitionResult.objects.filter(
            competition_id=competition_id, quarter=quarter
        ).update(is_winner=False)
        if totals:
            CompetitionResult.objects.filter(
                competition_id=competition_id, quarter=quarter,
                party_id=totals[0]['party_id'],
            ).update(is_winner=True)

    @extend_schema(
        summary="Chorak bo'yicha umumiy reyting",
        parameters=[
            OpenApiParameter('quarter', OpenApiTypes.STR, description="Ixtiyoriy chorak filteri"),
        ],
        responses={200: OpenApiTypes.OBJECT},
        tags=['competition-results'],
    )
    @action(detail=False, methods=['get'], url_path='quarter-summary')
    def quarter_summary(self, request):
        quarter = request.query_params.get('quarter')
        qs = CompetitionResult.objects.all()
        if quarter:
            qs = qs.filter(quarter=quarter)
        summary = (
            qs.values('party_id', 'party__name', 'party__color', 'quarter')
            .annotate(total=Sum('ball'))
            .order_by('quarter', '-total')
        )
        return Response(list(summary))
