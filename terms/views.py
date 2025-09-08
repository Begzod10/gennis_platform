from rest_framework import generics, views, response, status

from classes.models import ClassNumber
from group.models import Group
from .serializers import TestCreateUpdateSerializer, Test, TermSerializer, Term


class CreateTest(generics.CreateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestCreateUpdateSerializer


class UpdateTest(generics.UpdateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestCreateUpdateSerializer


class ListTerm(generics.ListAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer


class ListTest(views.APIView):
    def get(self, request, *args, **kwargs):
        term = kwargs.get('term')
        branch = kwargs.get('branch')

        result = []

        class_numbers = ClassNumber.objects.filter(branch=branch).all()

        for class_number in class_numbers:
            class_data = {"title": f"{class_number.number}th grade", "id": class_number.id,"type":"class_number", "children": []}

            groups = Group.objects.filter(class_number=class_number, deleted=False, branch=branch).all()

            for group in groups:
                group_data = {"title": group.name if group.name else str(
                    group.class_number.number) + " " + group.class_number.class_types.name, "type":"group","id": group.id,
                              "children": []}

                subjects = group.class_number.subjects.all()
                for subject in subjects:
                    tests = Test.objects.filter(group=group, subject=subject, term=term)

                    table_data = [{"id": test.id, "name": test.name, "weight": test.weight, "date": test.date} for test
                                  in tests]

                    group_data["children"].append({"title": subject.name, "id": subject.id, "type":"subject","tableData": table_data})

                if group_data["children"]:
                    class_data["children"].append(group_data)

            if class_data["children"]:
                result.append(class_data)

        return response.Response(result, status=status.HTTP_200_OK)
