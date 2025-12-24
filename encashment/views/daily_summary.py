from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from encashment.models import DailySummary
from encashment.serializers.daily_summary import DailySummarySerializer


class DailySummaryListView(ListAPIView):
    serializer_class = DailySummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DailySummary.objects.select_related('branch')

        branch_id = self.request.query_params.get('branch_id')
        date = self.request.query_params.get('date')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)

        if date:
            queryset = queryset.filter(date=date)

        if year and month:
            queryset = queryset.filter(
                date__year=year,
                date__month=month
            )
        elif year:
            queryset = queryset.filter(date__year=year)

        return queryset.order_by('-date')
