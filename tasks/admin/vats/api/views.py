from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from tasks.admin.vats.services.process import VatsProcess
from students.models import CallLog
from tasks.admin.vats import settings


class CallAPIView(APIView):

    async def post(self, request):
        user = request.data.get("user")
        phone = request.data.get("phone")

        student_id = request.data.get("student_id")
        comment = request.data.get("comment")
        category = request.data.get("category")

        vats = VatsProcess()
        result = await vats.call(user, phone)

        callid = result.get("callid")

        call = CallLog.objects.create(
            vats_call_id=callid,
            vats_phone=phone,
            vats_user=user,
            student_id=student_id,
            comment=comment,
            category=category,
            status="not_answered"
        )

        return Response({
            "callid": callid,
            "id": call.id
        })


class VatsWebhookAPIView(APIView):

    def post(self, request):
        data = request.data

        # 🔐 SECURITY
        if data.get("crm_token") != settings.VATS_CRM_TOKEN:
            return Response({"error": "unauthorized"}, status=403)

        if data.get("cmd") == "history":

            callid = data.get("callid")

            try:
                call = CallLog.objects.get(vats_call_id=callid)
            except CallLog.DoesNotExist:
                return Response({"error": "not found"}, status=404)

            call.vats_status = data.get("status")
            call.vats_duration = data.get("duration")
            call.vats_wait = data.get("wait")
            call.vats_phone = data.get("phone")
            call.vats_user = data.get("user")
            call.vats_type = data.get("type")
            call.audio_url = data.get("link")
            settings.save_audio(call)
            start = data.get("start")
            if start:
                call.vats_start = datetime.strptime(start, "%Y%m%dT%H%M%SZ")

            # status mapping
            if data.get("status") == "Success":
                call.status = "answered"
            else:
                call.status = "not_answered"

            call.save()

        return Response({"ok": True})
