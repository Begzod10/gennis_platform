import pprint

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
from vats.vats_process import VatsProcess, wait_until_call_finished
from lead.models import Lead, LeadCall
from lead.serializers import LeadSerializer, LeadCallSerializer
from lead.utils import calculate_leadcall_status_stats
from rest_framework.decorators import api_view
from rest_framework.response import Response
import asyncio
from asgiref.sync import sync_to_async
from datetime import datetime
from django.core.files.base import ContentFile


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
                username=lead.name + lead.surname + lead.phone,
                name=lead.name,
                surname=lead.surname,
                branch_id=lead.branch_id,
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


@api_view(['POST'])
def lead_call_ring(request):
    async def make_call():
        vats = VatsProcess()

        get_lead = await sync_to_async(Lead.objects.filter(pk=request.data['lead_id']).first)()

        call_response = await vats.call_client('tis_sergeli', "993656845")
        callid = call_response.get('callid')

        final_info = await wait_until_call_finished(vats, callid)
        pprint.pprint(final_info)
        if final_info['status'] == 'success':
            url = final_info['record']

            response = requests.get(url)
            audio_file_field = None

            if response.status_code == 200:
                file_name = f"call_record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                audio_file_field = ContentFile(response.content, name=file_name)
                print("File downloaded and ready to save")
            else:
                print("Failed to download. Status code:", response.status_code)
            lead_call = await sync_to_async(LeadCall.objects.create)(
                lead=get_lead,
                comment=request.data['comment'] if 'comment' in request.data else '',
                audio_file=audio_file_field,
                other_infos=final_info
            )
            serialized = LeadCallSerializer(lead_call)
            return {
                "call_result": final_info,
                "lead": serialized.data,
                "success": True
            }
        else:
            return {
                "call_result": final_info,
                "success": False
            }

    result = asyncio.run(make_call())
    return Response({"data": result}, status=status.HTTP_200_OK)
