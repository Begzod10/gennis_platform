import calendar

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Calendar.models import Years, Month, Day, TypeDay
from Calendar.serializers import DaySerializer, TypeDaySerializer
from permissions.functions.CheckUserPermissions import check_user_permissions
from user.functions.functions import check_auth


class CalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, current_year, next_year):
        list_days = {'calendar': []}
        for year in range(current_year, next_year + 1):
            year_data = Years.objects.filter(year=year).first()
            if not year_data:
                year_data = Years.objects.create(year=year)

            for month in range(1, 13):
                if (year == current_year and month not in [1, 2, 3, 4, 5, 6, 7, 8]) or (
                        year == next_year and month not in [9, 10, 11, 12]):
                    month_data = Month.objects.filter(month_number=month, years=year_data).first()
                    if not month_data:
                        month_name = calendar.month_name[month]
                        month_data = Month.objects.create(
                            month_number=month,
                            years=year_data,
                            month_name=month_name
                        )

                    days_list = Day.objects.filter(month=month_data, year=year_data)
                    days_serialized = DaySerializer(days_list, many=True).data
                    if not days_serialized:
                        cal = calendar.monthcalendar(year, month)
                        days_list = []
                        for week in cal:
                            for day in week:
                                if day != 0:
                                    day_str = str(day)
                                    weeks_id = calendar.weekday(year, month, day)
                                    day_name = calendar.day_name[weeks_id]
                                    type_day_instance = TypeDay.objects.get(
                                        type='Dam' if day_name == 'Sunday' else 'Ish kuni')
                                    day_object = Day.objects.get_or_create(
                                        day_number=day_str,
                                        month=month_data,
                                        year=year_data,
                                        defaults={'day_name': day_name, 'type_id': type_day_instance}
                                    )[0]
                                    days_list.append(day_object)

                        days_serialized = DaySerializer(days_list, many=True).data

                    types = []
                    for day in days_serialized:
                        day_type = day['type_id']['type']
                        day_color = day['type_id']['color']

                        type_exists = False
                        for type_obj in types:
                            if type_obj['type'] == day_type and type_obj['color'] == day_color:
                                type_obj['days'].append(day)
                                type_exists = True
                                break
                        if not type_exists:
                            types.append({
                                'type': day_type,
                                'color': day_color,
                                'days': [day]
                            })

                    month_obj = {
                        'month_number': month_data.month_number,
                        'month_name': month_data.month_name,
                        'days': days_serialized,
                        'types': types
                    }
                    list_days['calendar'].append({
                        'year': year_data.year,
                        'months': [month_obj]
                    })

        return Response(list_days, status=status.HTTP_200_OK)


class TypeDayListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = TypeDay.objects.all()
    serializer_class = TypeDaySerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['Calendar_typeday']
        permissions = check_user_permissions(user, table_names)

        queryset = TypeDay.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = TypeDaySerializer(queryset, many=True)
        return Response({'typeday': serializer.data, 'permissions': permissions})


class TypeDayDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = TypeDay.objects.all()
    serializer_class = TypeDaySerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['Calendar_typeday']
        permissions = check_user_permissions(user, table_names)
        room_images = self.get_object()
        room_images_data = self.get_serializer(room_images).data
        return Response({'typeday': room_images_data, 'permissions': permissions})
