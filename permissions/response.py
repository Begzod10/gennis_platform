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
                if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
                    value_list = value.strip('[]').split(',')
                    value_list = [v.strip() for v in value_list]
                    lookup = {f"{field}__in": value_list}
                    queryset = queryset.filter(**lookup)
                else:
                    lookup = {field: value}
                    queryset = queryset.filter(**lookup)
        return queryset
