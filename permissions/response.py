from datetime import date


class CustomResponseMixin:
    def get_custom_message(self, request):

        app_name = request.resolver_match.app_names[0]
        method = request.method

        if method == 'GET':
            return f"{app_name}dan maʼlumotlari muvaffaqiyatli olindi."
        elif method == 'POST':
            return f" {app_name} muvaffaqiyatli yaratildi."
        elif method == 'PUT':
            return f"{app_name}  maʼlumotlari muvaffaqiyatli yangilandi."
        elif method == 'DELETE':
            return f"{app_name}  maʼlumotlari muvaffaqiyatli o'chirildi."
        else:
            return f"{app_name}  amal muvaffaqiyatli yakunlandi."

    def finalize_response(self, request, response, *args, **kwargs):

        response = super().finalize_response(request, response, *args, **kwargs)

        if 200 <= response.status_code < 300:
            custom_message = self.get_custom_message(request)
            if isinstance(response.data, dict):
                response.data['msg'] = custom_message

        return response


class QueryParamFilterMixin:
    filter_mappings = {}

    def filter_queryset(self, queryset):
        for param, field in self.filter_mappings.items():
            value = self.request.query_params.get(param, None)
            if value is not None:
                if isinstance(value, str) and '-' in value:
                    age_range = value.split('-')
                    if len(age_range) == 2:
                        try:
                            age_from = int(age_range[0])
                            age_to = int(age_range[1])
                            today = date.today()
                            birth_date_from = date(today.year - age_to, today.month, today.day)
                            birth_date_to = date(today.year - age_from, today.month, today.day)
                            queryset = queryset.filter(**{
                                f'{field}__range': (birth_date_from, birth_date_to)
                            })
                        except ValueError:
                            pass
                elif isinstance(value, str) and value.startswith('[') and value.endswith(']'):
                    value_list = value.strip('[]').split(',')
                    value_list = [v.strip() for v in value_list]
                    lookup = {f"{field}__in": value_list}
                    queryset = queryset.filter(**lookup)
                else:
                    queryset = queryset.filter(**{field: value})
        return queryset
