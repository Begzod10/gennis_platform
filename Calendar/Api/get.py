import calendar

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from Calendar.models import Years, Month, Day, TypeDay
from Calendar.serializers import TypeDaySerializer
from permissions.functions.CheckUserPermissions import check_user_permissions
from user.functions.functions import check_auth


class CalendarView(APIView):

    def get(self, request, current_year, next_year):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['Calendar_month', 'Calendar_years', 'Calendar_day', 'Calendar_typeday']
        permissions = check_user_permissions(user, table_names)
        list_days = {
            'permissions': permissions,
            'calendar': []
        }
        for year in range(current_year, next_year + 1):
            for month in range(1, 13):
                if (year == current_year and month not in [1, 2, 3, 4, 5, 6, 7, 8]) or (
                        year == next_year and month not in [9, 10, 11, 12]):
                    month_name = calendar.month_name[month]
                    object_days = {
                        'month_number': month,
                        'month_name': month_name,
                        'days': [],
                        'year': year
                    }
                    cal = calendar.monthcalendar(year, month)
                    for week in cal:
                        for day in week:
                            day_str = str(day) if day != 0 else "  "
                            if day != 0:
                                if 1 <= day <= calendar.monthrange(year, month)[1]:
                                    weeks_id = calendar.weekday(year, month, day)
                                    day_name = calendar.day_name[weeks_id]
                                day_object = {
                                    'day_number': day_str,
                                    'day_name': day_name
                                }
                                object_days['days'].append(day_object)
                    list_days['calendar'].append(object_days)

        for year_data in list_days['calendar']:
            year_obj, created = Years.objects.get_or_create(year=year_data['year'])
            for month_data in list_days['calendar']:
                if month_data['year'] == year_data['year']:
                    month_obj, created = Month.objects.get_or_create(
                        month_number=month_data['month_number'],
                        years=year_obj,
                        defaults={'month_name': month_data['month_name']}
                    )
                    for day_data in month_data['days']:
                        type_day_instance = TypeDay.objects.get(id=1 if day_data['day_name'] == 'Sunday' else 2)
                        Day.objects.get_or_create(
                            day_number=day_data['day_number'],
                            month=month_obj,
                            year=year_obj,
                            defaults={'day_name': day_data['day_name'], 'type_id': type_day_instance}
                        )

        return Response(list_days, status=status.HTTP_200_OK)


class TypeDayListView(generics.ListAPIView):
    queryset = TypeDay.objects.all()
    serializer_class = TypeDaySerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['Calendar_typeday']
        permissions = check_user_permissions(user, table_names)

        queryset = TypeDay.objects.all()
        serializer = TypeDaySerializer(queryset, many=True)
        return Response({'typeday': serializer.data, 'permissions': permissions})


class TypeDayDetailView(generics.RetrieveAPIView):
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
