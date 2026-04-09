import asyncio
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from django.views import View
import json
from django.http import JsonResponse
from asgiref.sync import sync_to_async
from tasks.admin.vats.services.process import VatsProcess
from students.models import CallLog
from tasks.admin.vats import settings


class CallAsyncView(View):

    async def post(self, request):
        try:
            body = json.loads(request.body)
        except:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        user = body.get("user")
        phone = body.get("phone")
        student_id = body.get("student_id")
        comment = body.get("comment")
        category = body.get("category")

        vats = VatsProcess()

        # ✅ async VATS call
        result = await vats.call(user, phone)

        callid = result.get("callid")

        # ❗ ORM ni async qilish
        call = await sync_to_async(CallLog.objects.create)(
            vats_call_id=callid,
            vats_phone=phone,
            vats_user=user,
            student_id=student_id,
            comment=comment,
            category=category,
            status="not_answered"
        )

        return JsonResponse({
            "callid": callid,
            "id": call.id
        })


class VatsWebhookAsyncView(View):

    async def post(self, request):
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # 🔐 token check
        if data.get("crm_token") != settings.VATS_CRM_TOKEN:
            return JsonResponse({"error": "unauthorized"}, status=403)

        if data.get("cmd") == "history":

            callid = data.get("callid")

            try:
                call = await sync_to_async(CallLog.objects.get)(vats_call_id=callid)
            except CallLog.DoesNotExist:
                return JsonResponse({"error": "not found"}, status=404)

            call.vats_status = data.get("status")
            call.vats_duration = data.get("duration")
            call.vats_wait = data.get("wait")
            call.vats_phone = data.get("phone")
            call.vats_user = data.get("user")
            call.vats_type = data.get("type")
            call.audio_url = data.get("link")

            start = data.get("start")
            if start:
                call.vats_start = datetime.strptime(start, "%Y%m%dT%H%M%SZ")

            if data.get("status") == "Success":
                call.status = "answered"
            else:
                call.status = "not_answered"

            # ❗ save ham async
            await sync_to_async(call.save)()

        return JsonResponse({"ok": True})
