import asyncio
import json
from datetime import datetime
from django.utils.timezone import now
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import models
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from students.models import Student, CallLog, CallStatistic
from tasks.admin.vats.client import VatsCRMClient
from tasks.admin.vats.utils import wait_until_call_finished, poll_call_status_task


@method_decorator(csrf_exempt, name='dispatch')
class CallAsyncView(View):

    async def post(self, request):
        try:
            body = json.loads(request.body)
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        user = body.get("user")
        phone = body.get("phone")
        student_id = body.get("student_id")
        branch_id = body.get("student")
        comment = body.get("comment", "")
        category = body.get("category", "lead")

        if not user or not phone:
            return JsonResponse({"error": "user va phone majburiy"}, status=400)

        client = VatsCRMClient()

        # VATS ga qo'ng'iroq
        result = await client.make_call(user, phone)
        callid = result.get("callid")

        if not callid:
            return JsonResponse({
                "error": "VATS dan callid kelmadi",
                "vats_response": result
            }, status=400)

        # CallLog yaratish
        call = await sync_to_async(CallLog.objects.create)(
            vats_call_id=callid,
            vats_phone=phone,
            vats_user=user,
            vats_type="out",
            student_id=student_id,
            comment=comment,
            category=category,
            status="not_answered",
            branch_id=branch_id
        )

        # Polling background da boshlash
        asyncio.create_task(
            wait_until_call_finished(
                client=client,
                callid=callid,
                call_log_id=call.id
            )
        )

        return JsonResponse({
            "ok": True,
            "callid": callid,
            "call_log_id": call.id,
            "ws_url": f"ws://0.0.0.0:8000//ws/call/{callid}/"
        })
# @method_decorator(csrf_exempt, name='dispatch')
# class CallAsyncView(View):
#     async def post(self, request):
#         try:
#             body = json.loads(request.body)
#         except Exception:
#             return JsonResponse({"error": "Invalid JSON"}, status=400)
#
#         user = body.get("user")
#         phone = body.get("phone")
#         student_id = body.get("student_id")
#         branch_id = body.get("student")
#         comment = body.get("comment", "")
#         category = body.get("category", "lead")
#
#         if not user or not phone:
#             return JsonResponse({"error": "user va phone majburiy"}, status=400)
#
#         client = VatsCRMClient()
#
#         # VATS ga qo'ng'iroq
#         result = await client.make_call(user, phone)
#         callid = result.get("callid")
#
#         if not callid:
#             return JsonResponse({
#                 "error": "VATS dan callid kelmadi",
#                 "vats_response": result
#             }, status=400)
#
#         # CallLog yaratish
#         call = await sync_to_async(CallLog.objects.create)(
#             vats_call_id=callid,
#             vats_phone=phone,
#             vats_user=user,
#             vats_type="out",
#             student_id=student_id,
#             comment=comment,
#             category=category,
#             status="not_answered",
#             branch_id=branch_id
#         )
#
#         # ❌ ESKI KOD - O'CHIRISH KERAK:
#         # asyncio.create_task(
#         #     wait_until_call_finished(...)
#         # )
#
#         # ✅ YANGI KOD - CELERY TASK ISHGA TUSHIRISH:
#         poll_call_status_task.delay(
#             callid=callid,
#             call_log_id=call.id
#         )
#
#         return JsonResponse({
#             "ok": True,
#             "callid": callid,
#             "call_log_id": call.id,
#             "ws_url": f"ws://0.0.0.0:8000/ws/call/{callid}/"
#         })


@method_decorator(csrf_exempt, name='dispatch')
class StudentCallHistoryView(View):

    async def get(self, request):
        student_id = request.GET.get("student_id")
        lead_id = request.GET.get("lead_id")
        date_from = request.GET.get("date_from")  # 2024-01-01
        date_to = request.GET.get("date_to")  # 2024-01-31
        callid = request.GET.get("callid")


        try:
            def get_calls():
                filters = {}
                if callid:
                    filters["vats_call_id"] = callid
                if student_id:
                    filters["student_id"] = student_id
                if lead_id:
                    filters["lead_id"] = lead_id
                if date_from:
                    filters["called_at__date__gte"] = parse_date(date_from)
                if date_to:
                    filters["called_at__date__lte"] = parse_date(date_to)

                calls = (
                    CallLog.objects
                    .filter(**filters)
                    .select_related(
                        "student__user",
                        "lead"
                    )
                    .order_by("-called_at")
                )

                result = []
                for call in calls:
                    # Student yoki Lead ma'lumoti
                    person = {}
                    if call.student:
                        user = call.student.user
                        person = {
                            "type": "student",
                            "id": call.student.id,
                            "name": user.name or "",
                            "surname": user.surname or "",
                            "full_name": f"{user.name or ''} {user.surname or ''}".strip(),
                            "phone": user.phone or "",
                            "parents_number": call.student.parents_number or "",
                        }
                    elif call.lead:
                        person = {
                            "type": "lead",
                            "id": call.lead.id,
                            "name": call.lead.name or "",
                            "surname": "",
                            "full_name": call.lead.name or "",
                            "phone": call.lead.phone or "",
                        }

                    result.append({
                        "id": call.id,
                        "person": person,
                        'branch': call.branch_id,
                        # VATS ma'lumotlari
                        "vats_call_id": call.vats_call_id,
                        "vats_phone": call.vats_phone,
                        "vats_user": call.vats_user,
                        "vats_type": call.vats_type,
                        "vats_status": call.vats_status,
                        "vats_duration": call.vats_duration,
                        "vats_wait": call.vats_wait,
                        "vats_start": call.vats_start.isoformat() if call.vats_start else None,

                        # CRM ma'lumotlari
                        "status": call.status,
                        "category": call.category,
                        "comment": call.comment,
                        "audio_url": call.audio_url,
                        "audio": call.audio.url if call.audio else None,
                        "called_at": call.called_at.isoformat() if call.called_at else None,
                        "next_call_date": call.next_call_date.isoformat() if call.next_call_date else None,
                    })

                return result

            results = await sync_to_async(get_calls)()

            return JsonResponse({
                "ok": True,
                "count": len(results),
                "results": results
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CallStatusView(View):

    async def get(self, request):
        callid = request.GET.get("callid")
        call_log_id = request.GET.get("call_log_id")

        try:
            # 🔹 Barcha DB + relation ishlari sync ichida
            def get_call_with_data():
                qs = CallLog.objects.select_related(
                    "student__user",
                    "lead"
                )

                if callid:
                    call = qs.filter(vats_call_id=callid).first()
                else:
                    call = qs.filter(id=call_log_id).first()

                if not call:
                    return None

                # 🔹 is_finished
                is_finished = (
                        call.vats_duration is not None or
                        call.vats_status is not None
                )

                # 🔹 person build
                person = {}

                if call.student:
                    user = call.student.user
                    person = {
                        "type": "student",
                        "id": call.student.id,
                        "name": user.name or "",
                        "surname": user.surname or "",
                        "full_name": f"{user.name or ''} {user.surname or ''}".strip(),
                        "phone": user.phone or "",
                        "parents_number": call.student.parents_number or "",
                    }

                elif call.lead:
                    person = {
                        "type": "lead",
                        "id": call.lead.id,
                        "name": call.lead.name or "",
                        "surname": "",
                        "full_name": call.lead.name or "",
                        "phone": call.lead.phone or "",
                    }

                # 🔹 final response dict
                data = {
                    "id": call.id,
                    "person": person,
                    "is_finished": is_finished,

                    # VATS
                    "vats_call_id": call.vats_call_id,
                    "vats_phone": call.vats_phone,
                    "vats_user": call.vats_user,
                    "vats_type": call.vats_type,
                    "vats_status": call.vats_status,
                    "vats_duration": call.vats_duration,
                    "vats_wait": call.vats_wait,
                    "vats_start": call.vats_start.isoformat() if call.vats_start else None,

                    # CRM
                    "status": call.status,
                    "category": call.category,
                    "comment": call.comment,
                    "audio_url": call.audio_url,
                    "audio": call.audio.url if call.audio else None,
                    "called_at": call.called_at.isoformat() if call.called_at else None,
                    "next_call_date": call.next_call_date.isoformat() if call.next_call_date else None,
                }

                return data

            # 🔹 async call
            data = await sync_to_async(get_call_with_data)()

            if not data:
                return JsonResponse({"error": "CallLog topilmadi"}, status=404)

            return JsonResponse(data)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UpdateCallLogView(View):

    async def post(self, request):
        try:
            body = json.loads(request.body)
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Query params dan callid olish
        callid = request.GET.get('callid')

        if not callid:
            return JsonResponse({"error": "callid query paramda bo'lishi kerak"}, status=400)

        # Body dan ma'lumotlar
        next_call_date = body.get('next_call_date')
        comment = body.get('comment')

        if not next_call_date:
            return JsonResponse({"error": "next_call_date majburiy"}, status=400)

        try:
            # CallLog ni topish va yangilash
            call_log = await sync_to_async(CallLog.objects.get)(vats_call_id=callid)

            # Update qilish
            call_log.next_call_date = next_call_date
            if comment:
                call_log.comment = comment

            await sync_to_async(call_log.save)()

            return JsonResponse({
                "ok": True,
                "message": "CallLog muvaffaqiyatli yangilandi",
                "call_log_id": call_log.id,
                "vats_call_id": call_log.vats_call_id,
                "next_call_date": str(call_log.next_call_date),
                "comment": call_log.comment
            })

        except CallLog.DoesNotExist:
            return JsonResponse({
                "error": f"CallLog topilmadi: {callid}"
            }, status=404)
        except Exception as e:
            return JsonResponse({
                "error": f"Xatolik yuz berdi: {str(e)}"
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CallStatisticUpdateView(View):

    async def post(self, request):
        try:
            body = json.loads(request.body)
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        branch_id = body.get("branch")
        total = body.get("total", 0)

        today = now().date()

        def update_stat():
            stat, created = CallStatistic.objects.get_or_create(
                branch_id=branch_id,
                date=today,
                defaults={"total": total, "called": 0}
            )
            # Agar allaqachon bor bo'lsa total ni yangilamaymiz
            # faqat yangi yaratilganda total yoziladi
            return stat, created

        stat, created = await sync_to_async(update_stat)()

        return JsonResponse({
            "ok": True,
            "created": created,
            "branch_id": branch_id,
            "date": today.isoformat(),
            "total": stat.total,
            "called": stat.called,
            "percentage": stat.percentage
        })


@method_decorator(csrf_exempt, name='dispatch')
class CallStatisticView(View):

    async def get(self, request):
        """
        Query params:
        ?branch_id=1
        ?date=2024-01-15  (bo'lmasa bugun)
        """
        branch_id = request.GET.get("branch")
        date_str = request.GET.get("date")

        filters = {}
        if branch_id:
            filters["branch_id"] = branch_id

        if date_str:
            filters["date"] = parse_date(date_str)
        else:
            filters["date"] = now().date()

        def get_stats():
            stats = CallStatistic.objects.filter(**filters).select_related("branch")

            result = []
            for s in stats:
                result.append({
                    "id": s.id,
                    "branch_id": s.branch_id,
                    "date": s.date.isoformat(),
                    "total": s.total,
                    "called": s.called,
                    "percentage": s.percentage
                })
            return result

        results = await sync_to_async(get_stats)()

        return JsonResponse({
            "ok": True,
            "date": filters["date"].isoformat(),
            "results": results
        })


@method_decorator(csrf_exempt, name='dispatch')
class CalledListView(View):

    async def get(self, request):
        """
        Query params:
        ?branch_id=1&category=debtor
        ?date=2024-01-15  (bo'lmasa bugun)
        """
        branch_id = request.GET.get("branch_id")
        category = request.GET.get("category")
        date_str = request.GET.get("date")

        branch_id = int(branch_id)  # 🔥 MUHIM

        target_date = parse_date(date_str) if date_str else now().date()

        def get_calls():
            # Bugungi callloglar
            calls = (
                CallLog.objects
                .filter(
                    category=category,
                    called_at__date=target_date,
                    branch_id=branch_id
                )
                .select_related("student__user", "lead")
            )

            result = []
            for call in calls:
                person = {}
                if call.student:
                    user = call.student.user
                    person = {
                        "type": "student",
                        "id": call.student.id,
                        "full_name": f"{user.name or ''} {user.surname or ''}".strip(),
                        "phone": user.phone or "",
                        "parents_number": call.student.parents_number or "",
                    }
                elif call.lead:
                    person = {
                        "type": "lead",
                        "id": call.lead.id,
                        "full_name": call.lead.name or "",
                        "phone": call.lead.phone or "",
                    }

                result.append({
                    "id": call.id,
                    "person": person,
                    "status": call.status,
                    "category": call.category,
                    "vats_duration": call.vats_duration,
                    "vats_status": call.vats_status,
                    "audio_url": call.audio_url,
                    "comment": call.comment,
                    "called_at": call.called_at.isoformat() if call.called_at else None,
                })

            return result

        results = await sync_to_async(get_calls)()

        return JsonResponse({
            "ok": True,
            "count": len(results),
            "category": category,
            "date": target_date.isoformat(),
            "results": results
        })
