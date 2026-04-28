from drf_spectacular.generators import SchemaGenerator

class OnlyPartiesSchemaGenerator(SchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)

        allowed_prefix = "/api/surveys/"

        filtered_paths = {
            path: path_item
            for path, path_item in schema["paths"].items()
            if path.startswith(allowed_prefix)
        }

        schema["paths"] = filtered_paths
        return schema