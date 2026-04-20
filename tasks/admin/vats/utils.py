import asyncio
import time
from datetime import datetime

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from celery import shared_task
from tasks.admin.vats.client import VatsCRMClient


async def send_ws(callid: str, status: str, extra: dict = {}):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"call_{callid}",
        {
            "type": "call_status",
            "data": {"callid": callid, "status": status, **extra}
        }
    )


async def update_call_statistic(call):
    from students.models import CallStatistic, Student
    from lead.models import Lead
    from django.utils.timezone import now
    from asgiref.sync import sync_to_async

    student_id = call.student_id
    lead_id = call.lead_id

    def full_logic():
        today = now().date()

        branch_id = None

        if student_id:
            branch_id = Student.objects.select_related('user') \
                .get(id=student_id).user.branch_id

        elif lead_id:
            branch_id = Lead.objects.get(id=lead_id).branch_id

        if not branch_id:
            return

        stat, _ = CallStatistic.objects.get_or_create(
            branch_id=branch_id,
            date=today,
            defaults={"called": 0, "total": 0}
        )

        stat.called += 1
        stat.save()

    try:
        await sync_to_async(full_logic, thread_sensitive=True)()
    except Exception as e:
        print(f"Statistika update xato: {e}")


async def wait_until_call_finished(client, callid: str,
                                   call_log_id: int,
                                   timeout: int = 1200):
    from students.models import CallLog

    TERMINAL_STATES = {
        "success", "answer", "answered",
        "missed", "noanswer", "no-answer",
        "cancelled", "cancel",
        "failed", "failure", "busy",
    }

    def poll_interval(elapsed):
        if elapsed < 10:
            return 0.5
        elif elapsed < 30:
            return 1
        elif elapsed < 60:
            return 2
        else:
            return 3

    start = time.time()
    print(f"Polling boshlandi: callid={callid}")

    while time.time() - start < timeout:
        elapsed = time.time() - start

        try:
            info = await client.get_call_info_by_id(callid)

            # Hali tugamagan
            if info is None:
                await send_ws(callid, "in_progress", {
                    "elapsed": int(elapsed)
                })
                await asyncio.sleep(poll_interval(elapsed))
                continue

            vats_status = info.get("status", "").lower()
            duration = int(info.get("duration", 0) or 0)

            # Tugaganmi tekshirish
            if vats_status not in TERMINAL_STATES and duration == 0:
                await asyncio.sleep(poll_interval(elapsed))
                continue

            # Tugadi
            crm_status = "answered" if vats_status in {
                "success", "answer", "answered"
            } else "not_answered"

            # CallLog yangilash
            try:
                call = await sync_to_async(CallLog.objects.get)(id=call_log_id)
                call.vats_status = info.get("status", "")
                call.vats_duration = duration
                call.vats_wait = int(info.get("wait", 0) or 0)
                call.audio_url = info.get("record", "")
                call.status = crm_status

                start_time = info.get("start")
                if start_time:
                    try:
                        call.vats_start = datetime.fromisoformat(
                            start_time.replace("Z", "+00:00")
                        )
                    except Exception:
                        pass

                await sync_to_async(call.save)()
                await update_call_statistic(call)
                print(f"CallLog {call_log_id} yangilandi: {crm_status}, {duration}s")

            except Exception as e:
                print(f"CallLog yangilash xato: {e}")

            # Frontend ga yuborish
            await send_ws(callid, "finished", {
                "status": crm_status,
                "vats_status": info.get("status", ""),
                "duration": duration,
                "wait": info.get("wait", 0),
                "audio_url": info.get("record", ""),
                "call_log_id": call_log_id
            })

            return info

        except Exception as e:
            print(f"Polling xato: {e}")
            await asyncio.sleep(poll_interval(elapsed))

    # Timeout
    await send_ws(callid, "timeout", {"elapsed": int(time.time() - start)})
    print(f"Timeout: {callid}")
    return None


@shared_task(bind=True, max_retries=3)
def poll_call_status_task(self, callid: str, call_log_id: int):
    """
    Celery task - qo'ng'iroq tugashini kutib, ma'lumotlarni yangilaydi
    """
    try:
        # Async funksiyani ishga tushirish
        asyncio.run(
            wait_until_call_finished_sync(
                callid=callid,
                call_log_id=call_log_id
            )
        )
    except Exception as e:
        print(f"Celery task error: {e}")
        # Retry qilish
        raise self.retry(exc=e, countdown=5)


async def wait_until_call_finished_sync(callid: str, call_log_id: int, timeout: int = 1200):
    """
    Qo'ng'iroq holatini polling qilish (Celery task ichida ishlaydi)
    """
    from students.models import CallLog
    from .utils import send_ws, update_call_statistic  # Sizning utillaringiz

    client = VatsCRMClient()

    TERMINAL_STATES = {
        "success", "answer", "answered",
        "missed", "noanswer", "no-answer",
        "cancelled", "cancel",
        "failed", "failure", "busy",
    }

    def poll_interval(elapsed):
        if elapsed < 10:
            return 0.5
        elif elapsed < 30:
            return 1
        elif elapsed < 60:
            return 2
        else:
            return 3

    start = time.time()
    print(f"[CELERY] Polling boshlandi: callid={callid}, call_log_id={call_log_id}")

    while time.time() - start < timeout:
        elapsed = time.time() - start

        try:
            info = await client.get_call_info_by_id(callid)

            # Hali tugamagan
            if info is None:
                await send_ws(callid, "in_progress", {
                    "elapsed": int(elapsed)
                })
                await asyncio.sleep(poll_interval(elapsed))
                continue

            vats_status = info.get("status", "").lower()
            duration = int(info.get("duration", 0) or 0)

            # Tugaganmi tekshirish
            if vats_status not in TERMINAL_STATES and duration == 0:
                await asyncio.sleep(poll_interval(elapsed))
                continue

            # Tugadi - CallLog yangilash
            crm_status = "answered" if vats_status in {
                "success", "answer", "answered"
            } else "not_answered"

            try:
                call = await sync_to_async(CallLog.objects.get)(id=call_log_id)
                call.vats_status = info.get("status", "")
                call.vats_duration = duration
                call.vats_wait = int(info.get("wait", 0) or 0)
                call.audio_url = info.get("record", "")
                call.status = crm_status

                start_time = info.get("start")
                if start_time:
                    try:
                        call.vats_start = datetime.fromisoformat(
                            start_time.replace("Z", "+00:00")
                        )
                    except Exception:
                        pass

                await sync_to_async(call.save)()
                await update_call_statistic(call)
                print(f"[CELERY] CallLog {call_log_id} yangilandi: {crm_status}, {duration}s")

            except Exception as e:
                print(f"[CELERY] CallLog yangilash xato: {e}")

            # Frontend ga yuborish
            await send_ws(callid, "finished", {
                "status": crm_status,
                "vats_status": info.get("status", ""),
                "duration": duration,
                "wait": info.get("wait", 0),
                "audio_url": info.get("record", ""),
                "call_log_id": call_log_id
            })

            print(f"[CELERY] Polling tugadi: callid={callid}")
            return info

        except Exception as e:
            print(f"[CELERY] Polling xato: {e}")
            await asyncio.sleep(poll_interval(elapsed))

    # Timeout
    await send_ws(callid, "timeout", {"elapsed": int(time.time() - start)})
    print(f"[CELERY] Timeout: {callid}")
    return None
