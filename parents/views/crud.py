# parent/views.py

from django.contrib.auth.hashers import make_password
from rest_framework import generics
from rest_framework.response import Response

from parents.models import Parent
from parents.serializers.crud import ParentSerializer, ParentSerializerForList
from user.models import CustomUser


class ParentCreateView(generics.CreateAPIView):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer

    def create(self, request, *args, **kwargs):
        data = request.data

        if CustomUser.objects.filter(username=data.get("username")).exists():
            return Response({"error": "Username mavjud"}, status=400)

        user = CustomUser.objects.create(
            username=data.get("username"),
            name=data.get("name"),
            surname=data.get("surname"),
            father_name=data.get("father_name"),
            birth_date=data.get("born_date"),
            phone=data.get("phone"),
            password=make_password("12345678"),
            branch_id=data.get("location"),
        )

        parent = Parent.objects.create(user=user)

        return Response(ParentSerializer(parent).data, status=201)


class ParentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        parent = self.get_object()
        user = parent.user
        data = request.data

        for field in ["name", "surname", "phone", "father_name"]:
            if field in data:
                setattr(user, field, data[field])

        if "birth_date" in data:
            user.birth_date = data["birth_date"]

        if "username" in data:
            user.username = data["username"]

        user.save()
        return Response(ParentSerializer(parent).data)

    def destroy(self, request, *args, **kwargs):
        parent = self.get_object()
        parent.children.clear()
        parent.user.is_active = False
        parent.user.save()
        return Response({"message": "Parent deleted"}, status=204)


class ParentListView(generics.ListAPIView):
    serializer_class = ParentSerializerForList

    def get_queryset(self):
        branch_id = self.kwargs["branch_id"]
        deleted = self.request.query_params.get("deleted", "false") == "true"

        return Parent.objects.filter(
            user__branch_id=branch_id,
            user__is_active=not deleted
        ).order_by("-id")
