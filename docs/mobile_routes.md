# Mobile API Routes

> Created: 2026-04-16  
> Base path: `/api/Mobile/teachers/`  
> All endpoints require `Authorization: Bearer <token>`  
> Teacher is always resolved from `request.user` — no `teacher_id` needed.

---

## Observation

Base path: `/api/Mobile/teachers/observation/`

---

### GET `observation_info_list/`
Returns the list of observation criteria (info items).

**Response `200`:**
```json
[
  { "id": 1, "name": "Maqsad va vazifalar" },
  { "id": 2, "name": "Dars mazmuni" },
  { "id": 3, "name": "O'quvchilar faolligi" }
]
```

---

### GET `observation_options/`
Returns the list of scoring options used when submitting an observation.

**Response `200`:**
```json
[
  { "id": 1, "name": "A'lo", "value": 5 },
  { "id": 2, "name": "Yaxshi", "value": 4 },
  { "id": 3, "name": "Qoniqarli", "value": 3 }
]
```

---

### POST `teacher_observe/<group_id>/`
Submit an observation for a teacher's class (ClassTimeTable).  
Automatically marks the matching `TeacherObservationSchedule` entry as completed.

**URL param:** `group_id` — ClassTimeTable ID

**Request body:**
```json
{
  "day": 15,
  "month": 4,
  "year": 2026,
  "list": [
    { "id": 1, "value": 3, "comment": "Yaxshi tushuntirildi" },
    { "id": 2, "value": 5, "comment": "" },
    { "id": 3, "value": 4, "comment": "Faol ishtirok etdi" }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `day` | integer | Day of observation (optional, defaults to today) |
| `month` | integer | Month of observation (optional) |
| `year` | integer | Year (optional, defaults to current year) |
| `list` | array | Observation scores |
| `list[].id` | integer | ObservationInfo ID (criterion) |
| `list[].value` | integer | ObservationOptions ID (score option) |
| `list[].comment` | string | Optional comment |

**Response `200`:**
```json
{
  "msg": "Teacher has been observed",
  "success": true
}
```

> **Side effect:** After saving, the system finds the open `TeacherObservationSchedule` entry where `observer` = current teacher and `observed_teacher` = group's teacher, and marks it `is_completed = true`.  
> If the `TeacherObservationDay` is later deleted, the schedule entry reverts back to `is_completed = false`.

---

### GET `teacher_observe/<group_id>/`
List all past observations for a specific class (ClassTimeTable).

**Response `200`:**
```json
{
  "observation_tools": [
    {
      "id": 7,
      "date": "2026-04-15",
      "average": 82,
      "teacher": 4,
      "group": 12
    },
    {
      "id": 8,
      "date": "2026-04-10",
      "average": 75,
      "teacher": 4,
      "group": 12
    }
  ]
}
```

---

### GET `teacher_options/`
Returns today's class schedule for the authenticated observer teacher.  
Used to pick which class to observe.

**Query params:** `day`, `month`, `year` (all optional — defaults to today)

**Response `200`:**
```json
{
  "groups": [
    {
      "id": 22,
      "name": "9A",
      "subject": "Matematika",
      "teacher": "Jasur Toshev",
      "flow": null,
      "type": "group",
      "is_flow": false
    },
    {
      "id": 31,
      "name": null,
      "subject": "Ingliz tili",
      "teacher": "Malika Yusupova",
      "flow": "Oqim 1",
      "type": "flow",
      "is_flow": true
    }
  ],
  "old_current_dates": ["2026-04-14", "2026-04-15", "2026-04-16"]
}
```

---

### GET `schedule/`
Current or specific week's observation schedule for the authenticated teacher.

**Query params:** `week` (optional — defaults to current week)

**Response `200`:**
```json
{
  "current_week": 2,
  "total_weeks": 5,
  "week": 2,
  "week_start": "2026-04-28",
  "cycle_start": "2026-04-21",
  "schedule": [
    {
      "id": 11,
      "week": 2,
      "is_completed": false,
      "observed_teacher": { "id": 4, "name": "Jasur", "surname": "Toshev" },
      "time_table": { "id": 22, "name": "Matematika 9A" },
      "observation_day_id": null
    },
    {
      "id": 12,
      "week": 2,
      "is_completed": true,
      "observed_teacher": { "id": 5, "name": "Malika", "surname": "Yusupova" },
      "time_table": { "id": 31, "name": "Ingliz tili 8B" },
      "observation_day_id": 7
    }
  ]
}
```

---

### GET `schedule/all/`
Full schedule — all weeks grouped, for the authenticated teacher.

**Response `200`:**
```json
{
  "current_week": 2,
  "cycle_start": "2026-04-21",
  "weeks": [
    {
      "week": 1,
      "week_start": "2026-04-21",
      "is_current": false,
      "entries": [
        {
          "id": 1,
          "week": 1,
          "is_completed": true,
          "observed_teacher": { "id": 2, "name": "Dilnoza", "surname": "Rahimova" },
          "time_table": { "id": 10, "name": "Tarix 7A" },
          "observation_day_id": 5
        }
      ]
    },
    {
      "week": 2,
      "week_start": "2026-04-28",
      "is_current": true,
      "entries": [
        {
          "id": 11,
          "week": 2,
          "is_completed": false,
          "observed_teacher": { "id": 4, "name": "Jasur", "surname": "Toshev" },
          "time_table": { "id": 22, "name": "Matematika 9A" },
          "observation_day_id": null
        }
      ]
    }
  ]
}
```

---

### PATCH `schedule/<pk>/complete/`
Manually mark a schedule entry as completed and optionally link an observation day.

**Request body:**
```json
{
  "observation_day_id": 9
}
```

**Response `200`:**
```json
{
  "id": 11,
  "week": 2,
  "is_completed": true,
  "observed_teacher": { "id": 4, "name": "Jasur", "surname": "Toshev" },
  "time_table": { "id": 22, "name": "Matematika 9A" },
  "observation_day_id": 9
}
```

---

## Lesson Plan File

Base path: `/api/Mobile/teachers/`

---

### POST `lesson-plan/file/upload/`
Upload a lesson plan file for a term. AI review starts automatically in the background.  
One file per teacher per term — re-uploading replaces the previous file.

**Request:** `multipart/form-data`

| Field | Type | Required |
|-------|------|----------|
| `term_id` | integer | yes |
| `file` | file | yes — `.txt`, `.pdf`, `.docx` |

**Response `201` (new) / `200` (replaced):**
```json
{
  "id": 3,
  "term_id": 2,
  "status": "pending",
  "detail": "File uploaded. AI review started."
}
```

---

### GET `lesson-plan/file/<pk>/`
Get AI review status, score, and feedback for a specific file.  
Teacher can only view their own files.

**Response `200`:**
```json
{
  "id": 3,
  "term": { "id": 2, "quarter": 2, "academic_year": "2025-2026" },
  "file": "/media/lesson_plan_files/2026/04/plan.pdf",
  "status": "done",
  "score": 82,
  "feedback": "Dars rejasi yaxshi tuzilgan. Maqsad va vazifalar aniq ko'rsatilgan. Baholash mezonlari to'liq emas.",
  "uploaded_at": "2026-04-15T10:00:00Z",
  "reviewed_at": "2026-04-15T10:02:31Z"
}
```

Possible `status` values: `pending`, `checking`, `done`, `failed`

---

### GET `lesson-plan/file/`
List all lesson plan files uploaded by the authenticated teacher.

**Query params:** `term_id` (optional)

**Response `200`:**
```json
[
  {
    "id": 3,
    "term": { "id": 2, "quarter": 2, "academic_year": "2025-2026" },
    "file": "/media/lesson_plan_files/2026/04/plan.pdf",
    "status": "done",
    "score": 82,
    "feedback": "Dars rejasi yaxshi tuzilgan...",
    "uploaded_at": "2026-04-15T10:00:00Z",
    "reviewed_at": "2026-04-15T10:02:31Z"
  }
]
```
