# New API Routes

> Created: 2026-04-15

---

## 1. Observation — Teacher-to-Teacher Schedule

Base path: `/api/Observation/`

All endpoints require `Authorization: Bearer <token>`.

---

### POST `schedule/generate/`
Generate a full observation cycle for a branch. Dispatched to Celery — returns immediately with a `task_id`.

**Request body:**
```json
{
  "branch_id": 1,
  "start_date": "2026-04-21"
}
```

**Response `202`:**
```json
{
  "task_id": "abc-123",
  "detail": "Schedule generation started."
}
```

---

### POST `schedule/test_generate/`
Same as `generate/` but uses the current week's Monday as `start_date`. For testing only.

**Request body:**
```json
{
  "branch_id": 1
}
```

**Response `202`:**
```json
{
  "task_id": "def-456",
  "detail": "Test schedule generation started."
}
```

---

### GET `schedule/task/<task_id>/`
Poll the status of a schedule generation Celery task.

**Response `200`:**
```json
{ "task_id": "abc-123", "state": "PENDING" }
```
```json
{ "task_id": "abc-123", "state": "SUCCESS", "result": { "created": 40 } }
```
```json
{ "task_id": "abc-123", "state": "FAILURE", "detail": "Branch not found." }
```

---

### GET `schedule/cycles/`
List all observation cycles for a branch, newest first.

**Query params:** `branch_id` (required)

**Response `200`:**
```json
[
  {
    "id": 1,
    "branch_id": 1,
    "start_date": "2026-04-21",
    "created_at": "2026-04-21T08:00:00Z",
    "total_schedules": 40,
    "completed": 12
  }
]
```

---

### GET `schedule/current_week/`
Returns the teachers that the given observer must observe in the current week.

**Query params:** `branch_id` (required), `teacher_id` (required)

**Response `200`:**
```json
{
  "cycle_id": 1,
  "current_week": 2,
  "schedule": [
    {
      "id": 5,
      "week": 2,
      "is_completed": false,
      "observer": { "id": 3, "name": "Ali", "surname": "Valiev" },
      "observed_teacher": { "id": 7, "name": "Jasur", "surname": "Toshev" },
      "time_table": { "id": 12, "name": "Matematika 9A" },
      "observation_day_id": null
    }
  ]
}
```

---

### GET `schedule/`
Full schedule (all weeks) for one observer teacher, grouped by week.

**Query params:** `branch_id` (required), `teacher_id` (required), `cycle_id` (optional)

**Response `200`:**
```json
{
  "cycle_id": 1,
  "start_date": "2026-04-21",
  "current_week": 2,
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
          "observer": { "id": 3, "name": "Ali", "surname": "Valiev" },
          "observed_teacher": { "id": 7, "name": "Jasur", "surname": "Toshev" },
          "time_table": { "id": 12, "name": "Matematika 9A" },
          "observation_day_id": 5
        }
      ]
    }
  ]
}
```

---

### GET `schedule/branch/`
All observers' assignments for a specific week. Admin/management overview.

**Query params:** `branch_id` (required), `week` (optional), `cycle_id` (optional)

**Response `200`:**
```json
{
  "cycle_id": 1,
  "start_date": "2026-04-21",
  "current_week": 2,
  "week": 2,
  "week_start": "2026-04-28",
  "observers": [
    {
      "observer": { "id": 3, "name": "Ali", "surname": "Valiev" },
      "assignments": [
        {
          "id": 5,
          "week": 2,
          "is_completed": false,
          "observer": { "id": 3, "name": "Ali", "surname": "Valiev" },
          "observed_teacher": { "id": 7, "name": "Jasur", "surname": "Toshev" },
          "time_table": { "id": 12, "name": "Matematika 9A" },
          "observation_day_id": null
        }
      ]
    }
  ]
}
```

---

### PATCH `schedule/<pk>/complete/`
Mark a schedule entry as completed. Optionally link to a `TeacherObservationDay`.

**Request body:**
```json
{
  "observation_day_id": 9
}
```

**Response `200`:**
```json
{
  "id": 5,
  "week": 2,
  "is_completed": true,
  "observer": { "id": 3, "name": "Ali", "surname": "Valiev" },
  "observed_teacher": { "id": 7, "name": "Jasur", "surname": "Toshev" },
  "time_table": { "id": 12, "name": "Matematika 9A" },
  "observation_day_id": 9
}
```

> **Note:** Schedule entry is also auto-completed when a teacher submits an observation via `POST teacher_observe/<group_id>/`. Deleting the `TeacherObservationDay` reverts `is_completed` back to `false`.

---

## 2. Lesson Plan — File Upload + AI Review (Admin)

Base path: `/api/Lesson_plan/`

---

### POST `file/upload/`
Upload a lesson plan file for a teacher and term. AI review starts automatically in the background.
One file per teacher per term — re-uploading replaces the previous file.

**Request:** `multipart/form-data`

| Field | Type | Required |
|-------|------|----------|
| `teacher_id` | integer | yes |
| `term_id` | integer | yes |
| `file` | file | yes — `.txt`, `.pdf`, `.docx` |

**Response `201` (new) / `200` (replaced):**
```json
{
  "id": 3,
  "teacher_id": 5,
  "term_id": 2,
  "status": "pending",
  "detail": "File uploaded. AI review started."
}
```

---

### GET `file/<pk>/`
Get AI review status, score, and feedback for a specific file.

**Response `200`:**
```json
{
  "id": 3,
  "teacher": { "id": 5, "name": "Ali", "surname": "Valiev" },
  "term": { "id": 2, "quarter": 2, "academic_year": "2025-2026" },
  "file": "/media/lesson_plan_files/2026/04/plan.pdf",
  "status": "done",
  "score": 82,
  "feedback": "Dars rejasi yaxshi tuzilgan. Maqsad va vazifalar aniq.",
  "uploaded_at": "2026-04-15T10:00:00Z",
  "reviewed_at": "2026-04-15T10:02:31Z"
}
```

Possible `status` values: `pending`, `checking`, `done`, `failed`

---

### GET `file/`
List lesson plan files. Filterable by teacher and/or term.

**Query params:** `teacher_id` (optional), `term_id` (optional)

**Response `200`:**
```json
[
  {
    "id": 3,
    "teacher": { "id": 5, "name": "Ali", "surname": "Valiev" },
    "term": { "id": 2, "quarter": 2, "academic_year": "2025-2026" },
    "file": "/media/lesson_plan_files/2026/04/plan.pdf",
    "status": "done",
    "score": 82,
    "feedback": "Dars rejasi yaxshi tuzilgan.",
    "uploaded_at": "2026-04-15T10:00:00Z",
    "reviewed_at": "2026-04-15T10:02:31Z"
  }
]
```

---

## 3. Mobile — Observation Schedule

Base path: `/api/Mobile/teachers/observation/`

Teacher is resolved from `request.user` — no `teacher_id` needed in the request.

---

### GET `schedule/`
Current or specific week's schedule for the authenticated teacher.

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
    }
  ]
}
```

---

### GET `schedule/all/`
Full schedule for the authenticated teacher — all weeks grouped.

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
Mark a schedule entry as completed from mobile.

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

## 4. Mobile — Lesson Plan File

Base path: `/api/Mobile/teachers/`

Teacher is resolved from `request.user` — no `teacher_id` needed.

---

### POST `lesson-plan/file/upload/`
Upload a lesson plan file for a term. AI review starts automatically.

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
Get AI review result for a specific file. Teacher can only view their own files.

**Response `200`:**
```json
{
  "id": 3,
  "term": { "id": 2, "quarter": 2, "academic_year": "2025-2026" },
  "file": "/media/lesson_plan_files/2026/04/plan.pdf",
  "status": "done",
  "score": 82,
  "feedback": "Dars rejasi yaxshi tuzilgan. Maqsad va vazifalar aniq ko'rsatilgan.",
  "uploaded_at": "2026-04-15T10:00:00Z",
  "reviewed_at": "2026-04-15T10:02:31Z"
}
```

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

---

## 5. Modified Existing Routes

### GET/PATCH `/api/Users/users/<pk>/`
When the user is a teacher with subjects connected, the response now includes:

```json
{
  "id": 208,
  "name": "Ali",
  "role": "teacher",
  "teacher": {
    "id": 5,
    "subjects": [{ "id": 1, "name": "Matematika" }],
    "branches": [{ "id": 2, "name": "Chilonzor" }],
    "color": "#FF5733",
    "salary_percentage": 30,
    "working_hours": 160,
    "class_salary": 50000,
    "teacher_salary_type": { "id": 1, "name": "Foizli", "salary": 0 },
    "class_type": { "id": 2, "name": "Kichik guruh" }
  }
}
```

If the user is not a teacher or has no subjects: `"role": null, "teacher": null`
