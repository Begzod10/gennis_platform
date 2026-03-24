
from django.db.models import F, Sum, Subquery
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
    Competition, CompetitionResult,
)
from .serializers import (
    PartyListSerializer, PartyDetailSerializer,
    PartyMemberSerializer, PartyMemberWriteSerializer,
    PartyTaskSerializer, PartyTaskGradeSerializer,
    CompetitionSerializer, CompetitionResultSerializer,
    StudentSelectSerializer, GroupSelectSerializer,
)



def _branch_id(request):

    raw = request.query_params.get('branch_id') or request.data.get('branch_id')
    if raw is not None:
        try:
            return int(raw)
        except (TypeError, ValueError):
            pass
    return None


def _distribute_ball_to_members(party_id: int, delta: int) -> None:

    if delta == 0:
        return
    PartyMember.objects.filter(
        party_id=party_id, is_active=True
    ).update(ball=F('ball') + delta)


def _recalc_party_ball(party_id: int) -> None:

    total = (
        PartyTaskGrade.objects
        .filter(party_id=party_id)
        .aggregate(t=Sum('ball'))['t'] or 0
    )
    Party.objects.filter(pk=party_id).update(ball=total)


class StudentSelectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentSelectSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['user__name', 'user__surname']
    filterset_class = StudentFilter

    def get_queryset(self):
        qs = Student.objects.select_related('user')
        bid = _branch_id(self.request)
        if bid:
            qs = qs.filter(user__branch__id=bid)
        return qs

    @extend_schema(
        summary="Student select options",
        description="Frontend `<Select>` uchun `[{id, label, born_date}]`. ?branch_id= filtr.",
        parameters=[
            OpenApiParameter('branch_id', OpenApiTypes.INT, description="Filial ID"),
            OpenApiParameter('party', OpenApiTypes.INT, description="Shu partiyada yo'q studentlar"),
        ],
        responses={200: StudentSelectSerializer(many=True)},
        tags=['select-options'],
    )
    @action(detail=False, methods=['get'], url_path='select')
    def select(self, request):
        qs = self.filter_queryset(self.get_queryset())
        party_id = request.query_params.get('party')
        if party_id:
            already_in = PartyMember.objects.filter(
                party_id=party_id
            ).values('student_id')
            qs = qs.exclude(id__in=Subquery(already_in))
        return Response(StudentSelectSerializer(qs, many=True).data)




class GroupSelectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupSelectSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'color_name']
    filterset_fields = ['branch']

    def get_queryset(self):
        qs = Group.objects.select_related('class_number', 'color')
        bid = _branch_id(self.request)
        if bid:
            qs = qs.filter(branch_id=bid)
        return qs

    @extend_schema(
        summary="Guruh select options",
        description=(
            "Frontend `<Select>` uchun `[{id, label}]`.\n\n"
            "**label:** `group.name` bo'sh → `class_number + color_name`. ?branch_id= filtr."
        ),
        parameters=[
            OpenApiParameter('branch_id', OpenApiTypes.INT, description="Filial ID"),
        ],
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
        description="?branch_id= filtr. `display_name`, `members_count`, `wins_count`, `tasks_count`, `groups_count`.",
        parameters=[OpenApiParameter('branch_id', OpenApiTypes.INT, description="Filial ID")],
        responses={200: PartyListSerializer(many=True)},
        tags=['parties'],
    ),
    create=extend_schema(
        summary="Yangi partiya yaratish",
        description="`students`, `groups` — ID massivlari. `branch_id` — query-param yoki body.",
        request=PartyDetailSerializer,
        responses={201: PartyDetailSerializer},
        examples=[
            OpenApiExample(
                "Misol",
                value={
                    "name": "Burgut partiyasi",
                    "color": "#10b981",
                    "desc": "Kuchli partiya",
                    "branch_id": 1,
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
        qs = Party.objects.prefetch_related(
            'students',
            'groups',
            'memberships__student__user',
            'tasks',
            'competition_results',
        )
        bid = _branch_id(self.request)
        if bid:
            qs = qs.filter(branch_id=bid)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return PartyListSerializer
        return PartyDetailSerializer

    def perform_create(self, serializer):
        bid = _branch_id(self.request)
        kwargs = {}
        if bid:
            kwargs['branch_id'] = bid
        serializer.save(**kwargs)

    @extend_schema(
        summary="Partiya select options",
        description="?branch_id= filtr. `[{label, value, color}]`.",
        parameters=[OpenApiParameter('branch_id', OpenApiTypes.INT, description="Filial ID")],
        responses={200: OpenApiTypes.OBJECT},
        tags=['parties'],
    )
    @action(detail=False, methods=['get'], url_path='select-options')
    def select_options(self, request):
        qs = Party.objects.values('id', 'name', 'color')
        bid = _branch_id(request)
        if bid:
            qs = qs.filter(branch_id=bid)
        return Response([
            {'label': p['name'], 'value': p['id'], 'color': p['color']}
            for p in qs
        ])

    @extend_schema(
        summary="Reyting — ball bo'yicha tartiblangan",
        parameters=[OpenApiParameter('branch_id', OpenApiTypes.INT, description="Filial ID")],
        responses={200: PartyListSerializer(many=True)},
        tags=['parties'],
    )
    @action(detail=False, methods=['get'], url_path='rating')
    def rating(self, request):
        """get_queryset branch filterni o'z ichiga oladi."""
        qs = self.get_queryset().order_by('-ball')
        return Response(PartyListSerializer(qs, many=True).data)

    @extend_schema(
        summary="Partiyaga studentlar qo'shish",
        description="O(K): 2× IN-query + bitta bulk_create + bitta M2M INSERT.",
        request={'application/json': {'type': 'object', 'properties': {
            'student_ids': {'type': 'array', 'items': {'type': 'integer'}},
        }, 'required': ['student_ids']}},
        responses={200: OpenApiResponse(description="{'added': [...], 'skipped': [...]}")},
        tags=['parties'],
    )
    @action(detail=True, methods=['post'], url_path='add-students')
    def add_students(self, request, pk=None):

        party = self.get_object()
        student_ids: list[int] = list(request.data.get('student_ids', []))
        if not student_ids:
            return Response({'added': [], 'skipped': []})

        valid_ids: set[int] = set(
            Student.objects.filter(id__in=student_ids).values_list('id', flat=True)
        )
        already: set[int] = set(
            PartyMember.objects.filter(
                party=party, student_id__in=student_ids
            ).values_list('student_id', flat=True)
        )

        to_add  = valid_ids - already
        skipped = set(student_ids) - valid_ids

        if to_add:
            PartyMember.objects.bulk_create(
                [PartyMember(party=party, student_id=sid, is_active=True) for sid in to_add],
                ignore_conflicts=True,
            )
            party.students.add(*to_add)

        return Response({'added': list(to_add), 'skipped': list(skipped)})

    @extend_schema(
        summary="Partiyadan studentlarni chiqarish",
        request={'application/json': {'type': 'object', 'properties': {
            'student_ids': {'type': 'array', 'items': {'type': 'integer'}},
        }, 'required': ['student_ids']}},
        responses={200: OpenApiResponse(description="{'removed': [1,2]}")},
        tags=['parties'],
    )
    @action(detail=True, methods=['post'], url_path='remove-students')
    def remove_students(self, request, pk=None):
        """O(K) — bitta M2M DELETE + bitta UPDATE."""
        party = self.get_object()
        student_ids: list[int] = request.data.get('student_ids', [])
        if not student_ids:
            return Response({'removed': []})
        party.students.remove(*student_ids)
        PartyMember.objects.filter(
            party=party, student_id__in=student_ids
        ).update(is_active=False)
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
        """O(G) — .set() DELETE + INSERT."""
        party = self.get_object()
        group_ids: list[int] = request.data.get('group_ids', [])
        party.groups.set(group_ids)
        return Response({'groups': group_ids})

    @extend_schema(
        summary="A'zo balini o'zgartirish (+N / -N)",
        description="`delta` musbat yoki manfiy.",
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
        except PartyMember.DoesNotExist:
            return Response({'error': "A'zo topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        member.ball = max(0, member.ball + delta)
        member.save(update_fields=['ball'])
        return Response(PartyMemberSerializer(member).data)




@extend_schema_view(
    list=extend_schema(
        summary="Barcha a'zolar ro'yxati",
        parameters=[
            OpenApiParameter('branch_id', OpenApiTypes.INT, description="Filial ID"),
            OpenApiParameter('party', OpenApiTypes.INT, description="Partiya ID"),
            OpenApiParameter('student', OpenApiTypes.INT, description="Student ID"),
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['party', 'student']

    def get_queryset(self):
        qs = PartyMember.objects.select_related(
            'party',
            'student__user',
            'student__class_number',
        )
        bid = _branch_id(self.request)
        if bid:
            qs = qs.filter(party__branch_id=bid)
        return qs

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return PartyMemberWriteSerializer
        return PartyMemberSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        objs = serializer.save()
        return Response(
            PartyMemberSerializer(objs, many=True).data,
            status=status.HTTP_201_CREATED,
        )

@extend_schema_view(
    list=extend_schema(
        summary="Topshiriqlar ro'yxati",
        description="`parties_info` — partiyalar + grade ballari. ?branch_id= filtr.",
        parameters=[OpenApiParameter('branch_id', OpenApiTypes.INT, description="Filial ID")],
        tags=['party-tasks'],
    ),
    create=extend_schema(
        summary="Yangi topshiriq yaratish",
        examples=[
            OpenApiExample("Misol", value={
                "name": "Matematika musobaqa",
                "ball": 100,
                "deadline": "2025-06-01",
                "branch_id": 1,
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

    serializer_class = PartyTaskSerializer

    def get_queryset(self):
        qs = PartyTask.objects.prefetch_related(
            'parties',
            'grades__party',
        )
        bid = _branch_id(self.request)
        if bid:
            qs = qs.filter(parties__branch_id=bid).distinct()
        return qs

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
        new_ball = request.data.get('ball')

        if party_id is None or new_ball is None:
            return Response({'error': 'party va ball majburiy'}, status=400)

        party_id = int(party_id)
        new_ball = int(new_ball)

        if not Party.objects.filter(pk=party_id).exists():
            return Response({'error': 'Partiya topilmadi'}, status=404)

        row = PartyTaskGrade.objects.filter(
            task=task, party_id=party_id
        ).values('ball').first()
        old_ball = row['ball'] if row else 0

        grade_obj, created = PartyTaskGrade.objects.update_or_create(
            task=task, party_id=party_id,
            defaults={'ball': new_ball},
        )

        _distribute_ball_to_members(party_id, new_ball - old_ball)
        _recalc_party_ball(party_id)

        code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(PartyTaskGradeSerializer(grade_obj).data, status=code)

    @extend_schema(
        summary="Barcha partiyalarga bir vaqtda ball berish",
        description=(
            "O(K): bitta prefetch → existing grade-lar, keyin K× update_or_create "
            "+ K× F()-expr UPDATE (distribute) + K× SUM (recalc)."
        ),
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
        grades_data: list[dict] = request.data.get('grades', [])
        if not grades_data:
            return Response([])

        party_ids = []
        for g in grades_data:
            try:
                party_ids.append(int(g['party']))
            except (KeyError, TypeError, ValueError):
                pass

        existing_map: dict[int, int] = {
            row['party_id']: row['ball']
            for row in PartyTaskGrade.objects.filter(
                task=task, party_id__in=party_ids
            ).values('party_id', 'ball')
        }

        results = []
        parties_to_recalc: set[int] = set()

        for g in grades_data:
            try:
                party_id = int(g['party'])
                new_ball = int(g['ball'])
            except (KeyError, TypeError, ValueError):
                continue

            old_ball = existing_map.get(party_id, 0)

            grade_obj, _ = PartyTaskGrade.objects.update_or_create(
                task=task, party_id=party_id,
                defaults={'ball': new_ball},
            )
            results.append(PartyTaskGradeSerializer(grade_obj).data)

            _distribute_ball_to_members(party_id, new_ball - old_ball)
            parties_to_recalc.add(party_id)

        for pid in parties_to_recalc:
            _recalc_party_ball(pid)

        return Response(results)



@extend_schema_view(
    list=extend_schema(
        summary="Musobaqa turlari",
        parameters=[OpenApiParameter('branch_id', OpenApiTypes.INT, description="Filial ID")],
        tags=['competitions'],
    ),
    create=extend_schema(summary="Yangi musobaqa turi", tags=['competitions']),
    retrieve=extend_schema(summary="Musobaqa batafsil", tags=['competitions']),
    update=extend_schema(summary="Musobaqani yangilash", tags=['competitions']),
    partial_update=extend_schema(summary="Musobaqani qisman yangilash", tags=['competitions']),
    destroy=extend_schema(summary="Musobaqani o'chirish", tags=['competitions']),
)
class CompetitionViewSet(viewsets.ModelViewSet):
    serializer_class = CompetitionSerializer

    def get_queryset(self):
        qs = Competition.objects.prefetch_related('results__party')
        bid = _branch_id(self.request)
        if bid:

            qs = qs.filter(results__party__branch_id=bid).distinct()
        return qs



@extend_schema_view(
    list=extend_schema(
        summary="Musobaqa natijalari",
        parameters=[
            OpenApiParameter('branch_id', OpenApiTypes.INT, description="Filial ID"),
            OpenApiParameter('competition', OpenApiTypes.INT, description="Musobaqa ID"),
            OpenApiParameter('quarter', OpenApiTypes.STR, description="1-chorak | 2-chorak | 3-chorak | 4-chorak"),
        ],
        tags=['competition-results'],
    ),
    create=extend_schema(
        summary="Natija qo'shish (mode: add | replace)",
        description="`branch_id` — query-param yoki body.",
        tags=['competition-results'],
    ),
    retrieve=extend_schema(summary="Natija batafsil", tags=['competition-results']),
    update=extend_schema(summary="Natijani yangilash", tags=['competition-results']),
    partial_update=extend_schema(summary="Natijani qisman yangilash", tags=['competition-results']),
    destroy=extend_schema(summary="Natijani o'chirish", tags=['competition-results']),
)
class CompetitionResultViewSet(viewsets.ModelViewSet):

    serializer_class = CompetitionResultSerializer

    def get_queryset(self):
        qs = CompetitionResult.objects.select_related('party', 'competition')
        bid = _branch_id(self.request)
        if bid:
            qs = qs.filter(party__branch_id=bid)
        comp_id = self.request.query_params.get('competition')
        quarter = self.request.query_params.get('quarter')
        if comp_id:
            qs = qs.filter(competition_id=comp_id)
        if quarter:
            qs = qs.filter(quarter=quarter)
        return qs


    @staticmethod
    def _update_winner(competition_id: int, quarter: str) -> None:

        base = CompetitionResult.objects.filter(
            competition_id=competition_id, quarter=quarter
        )
        top = (
            base.values('party_id')
            .annotate(total=Sum('ball'))
            .order_by('-total')
            .first()
        )
        base.update(is_winner=False)
        if top:
            base.filter(party_id=top['party_id']).update(is_winner=True)

    def create(self, request, *args, **kwargs):

        comp_id  = request.data.get('competition')
        party_id = request.data.get('party')
        quarter  = request.data.get('quarter')
        new_ball = int(request.data.get('ball', 0))
        note     = request.data.get('note', '')
        mode     = request.data.get('mode', 'add')

        try:
            Party.objects.get(pk=party_id)
        except Party.DoesNotExist:
            return Response({'error': 'Partiya topilmadi'}, status=404)

        party_id = int(party_id)

        existing = CompetitionResult.objects.filter(
            competition_id=comp_id,
            party_id=party_id,
            quarter=quarter,
        ).first()

        if existing:
            old_ball   = existing.ball
            final_ball = old_ball + new_ball if mode == 'add' else new_ball
            existing.ball = final_ball
            if note:
                existing.note = note
            existing.save(update_fields=['ball', 'note'])

            _distribute_ball_to_members(party_id, final_ball - old_ball)
            self._update_winner(comp_id, quarter)
            return Response(
                CompetitionResultSerializer(existing).data,
                status=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        _distribute_ball_to_members(party_id, new_ball)
        self._update_winner(comp_id, quarter)
        return Response(
            CompetitionResultSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Chorak bo'yicha umumiy reyting",
        parameters=[
            OpenApiParameter('branch_id', OpenApiTypes.INT, description="Filial ID"),
            OpenApiParameter('quarter', OpenApiTypes.STR, description="Ixtiyoriy chorak filteri"),
        ],
        responses={200: OpenApiTypes.OBJECT},
        tags=['competition-results'],
    )
    @action(detail=False, methods=['get'], url_path='quarter-summary')
    def quarter_summary(self, request):

        qs = self.get_queryset()
        summary = (
            qs.values('party_id', 'party__name', 'party__color', 'quarter')
            .annotate(total=Sum('ball'))
            .order_by('quarter', '-total')
        )
        return Response(list(summary))