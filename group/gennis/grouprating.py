# views.py
from django.db.models.functions import Coalesce
from django.db.models import Avg, Count, Q, Value, FloatField
from django.db.models import Avg, Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from group.models import GroupRating, Group
from group.serializers import GroupRatingSerializer, GroupRatingCreateSerializer, GroupWithRatingSerializer


class GroupRatingListCreateView(APIView):

    def get(self, request):
        queryset = GroupRating.objects.select_related(
            'group', 'teacher__user', 'branch'
        ).all()

        # --- FILTERS ---
        branch_id = request.query_params.get('branch_id')
        group_id = request.query_params.get('group_id')
        teacher_id = request.query_params.get('teacher_id')
        rating = request.query_params.get('rating')
        color = request.query_params.get('color')
        date_from = request.query_params.get('date_from')  # YYYY-MM-DD
        date_to = request.query_params.get('date_to')  # YYYY-MM-DD
        date = request.query_params.get('date')  # aniq bir sana

        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        if rating:
            queryset = queryset.filter(rating=rating)
        if color:
            queryset = queryset.filter(color=color)
        if date:
            queryset = queryset.filter(date=date)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        serializer = GroupRatingSerializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        })

    def post(self, request):
        serializer = GroupRatingCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                GroupRatingSerializer(instance).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupRatingDetailView(APIView):

    def get_object(self, pk):
        return get_object_or_404(GroupRating, pk=pk)

    def get(self, request, pk):
        instance = self.get_object(pk)
        serializer = GroupRatingSerializer(instance)
        return Response(serializer.data)

    def put(self, request, pk):
        instance = self.get_object(pk)
        serializer = GroupRatingCreateSerializer(instance, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(GroupRatingSerializer(instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        instance = self.get_object(pk)
        serializer = GroupRatingCreateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(GroupRatingSerializer(instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        instance = self.get_object(pk)
        instance.delete()
        return Response(
            {"detail": "Muvaffaqiyatli o'chirildi."},
            status=200
        )


class GroupWithRatingListView(APIView):

    def get(self, request):
        branch_id = request.query_params.get('branch_id')
        teacher_id = request.query_params.get('teacher_id')
        status = request.query_params.get('status')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        min_avg_rating = request.query_params.get('min_avg_rating')
        color = request.query_params.get('color')

        groups = Group.objects.filter(deleted=False).prefetch_related('ratings')

        if branch_id:
            groups = groups.filter(branch_id=branch_id)
        if teacher_id:
            groups = groups.filter(teacher__id=teacher_id)
        if status is not None:
            groups = groups.filter(status=status.lower() == 'true')

        # Q filter — annotatsiya uchun
        rating_q = Q()
        if date_from:
            rating_q &= Q(ratings__date__gte=date_from)
        if date_to:
            rating_q &= Q(ratings__date__lte=date_to)
        if color:
            rating_q &= Q(ratings__color=color)

        groups = groups.annotate(
            avg_rating=Coalesce(
                Avg('ratings__rating', filter=rating_q),
                Value(0.0),
                output_field=FloatField()
            ),
            total_ratings=Count('ratings__id', filter=rating_q),
        ).order_by('-avg_rating')

        if min_avg_rating:
            groups = groups.filter(avg_rating__gte=float(min_avg_rating))

        serializer = GroupWithRatingSerializer(groups, many=True)
        return Response({
            "count": groups.count(),
            "results": serializer.data,
        })
