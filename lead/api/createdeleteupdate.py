from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lead.models import Lead, LeadCall
from lead.serializers import LeadSerializer, LeadCallSerializer
from lead.utils import calculate_leadcall_status_stats


class LeadCreateView(generics.CreateAPIView):
    # permission_classes = [IsAuthenticated]

    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class LeadUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class LeadDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True
        lead_cals = LeadCall.objects.filter(lead=instance).all()
        for lead_cal in lead_cals:
            lead_cal.deleted = True
            lead_cal.save()
        instance.save()
        stats = calculate_leadcall_status_stats(requests=request)

        return Response({'message': "deleted", **stats}, status=status.HTTP_200_OK)


class LeadCallCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = LeadCall.objects.all()
    serializer_class = LeadCallSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead_call = serializer.save()
        stats = calculate_leadcall_status_stats(requests=request)
        data = request.data

        if (data["status"]):
            from user.models import CustomUser
            lead = Lead.objects.filter(pk=data['lead']).first()
            user_create = CustomUser.objects.create(
                username=lead.name+lead.surname + lead.phone,
                name=lead.name,
                surname=lead.surname,
                branch_id=data['branch'],
            )
            user_create.set_password('12345678')
            from students.models import Student
            student = Student.objects.create(
                user=user_create
            )

        return Response({
            "data": self.get_serializer(lead_call).data,
            **stats
        }, status=status.HTTP_200_OK)


class LeadCallUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = LeadCall.objects.all()
    serializer_class = LeadCallSerializer


class LeadCallDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = LeadCall.objects.all()
    serializer_class = LeadCallSerializer
