# Mobile Teacher Routes — Update Notes (2026-05-11)

Scope: routes added or changed in the recent passes covering
- `Test.flow` FK addition
- `TeacherListTest` rewrite (groups + flows union, bulk fetched)
- `LessonPlanFile.subject` FK addition
- `TeacherGroupsAndFlowsView` (`my-classes`) source-of-truth fix

All routes below require `Authorization: Bearer <access_token>` obtained from `/api/token/`.

Base prefix for every route in this doc: `/api/Mobile/teachers/`.

---

## 1. `GET terms/my-classes/`

Class+flow list for the authenticated teacher. Source of truth is the union of `ClassTimeTable.group_id` and the legacy `Group.teacher` M2M, so teachers whose M2M was never maintained still see all their groups.

### Request

No body. No query params.

### Sample response — 200 OK

```json
{
  "groups": [
    {
      "id": 190,
      "name": "1-green",
      "type": "group",
      "students_count": 7,
      "subjects": [
        { "id": 12, "name": "Matematika" },
        { "id": 18, "name": "Ona tili" }
      ]
    },
    {
      "id": 191,
      "name": "2-red",
      "type": "group",
      "students_count": 22,
      "subjects": [
        { "id": 12, "name": "Matematika" }
      ]
    }
  ],
  "flows": [
    {
      "id": 5,
      "name": "Advanced English A",
      "type": "flow",
      "students_count": 14,
      "subjects": [
        { "id": 7, "name": "English" }
      ]
    }
  ]
}
```

### Error responses

| Status | Body | Cause |
|--------|------|-------|
| 403    | `{"detail": "Siz teacher emassiz"}` | Authenticated user has no Teacher row |

---

## 2. `GET terms/list-test/<term_id>/`

Tests visible to this teacher in the given term, grouped by **group** and by **flow**. Now returns flow-only tests as additional siblings.

### Path params

| Name    | Type | Notes                                |
|---------|------|--------------------------------------|
| term_id | int  | Must exist in `terms_term`. 404 else |

### Sample response — 200 OK

```json
[
  {
    "title": "1-green",
    "id": 190,
    "type": "group",
    "children": [
      {
        "title": "Matematika",
        "id": 12,
        "type": "subject",
        "tableData": [
          { "id": 401, "name": "Nazorat ishi 1", "weight": 30, "date": "2026-04-10" },
          { "id": 402, "name": "Mustaqil ish",    "weight": 20, "date": "2026-04-22" }
        ]
      }
    ]
  },
  {
    "title": "Advanced English A",
    "id": 5,
    "type": "flow",
    "children": [
      {
        "title": "English",
        "id": 7,
        "type": "subject",
        "tableData": [
          { "id": 410, "name": "Speaking Test", "weight": 25, "date": "2026-04-15" }
        ]
      }
    ]
  }
]
```

### Error responses

| Status | Body | Cause |
|--------|------|-------|
| 403    | `{"detail": "Siz teacher emassiz"}` | No Teacher row for user |
| 404    | `{"detail": "Not found."}`          | Unknown `term_id`        |

### Notes

- Groups with **no** children (no teacher-relevant subjects) are omitted.
- Flow blocks with `flow.subject_id IS NULL` are omitted (no subject to render under).
- Flows are filtered by `teacher=<current>` only — no `activity` filter, consistent with the rest of the codebase.

---

## 3. `POST terms/create-test/`

Create a Test row. **Now accepts `flow` in addition to `group`.** Exactly one of `group` or `flow` is required.

### Request body (JSON)

| Field        | Type       | Required | Notes                                                  |
|--------------|------------|----------|--------------------------------------------------------|
| name         | string     | yes      |                                                        |
| weight       | int        | yes      | Test weight 1–100                                      |
| term         | int (FK)   | yes      |                                                        |
| subject      | int (FK)   | yes      |                                                        |
| date         | YYYY-MM-DD | no       | Defaults to today                                      |
| group        | int (FK)   | one-of   | When set, `class_number` is auto-derived from group    |
| flow         | int (FK)   | one-of   | Mutually exclusive in practice with `group` (one wins) |
| class_number | int (FK)   | no       | Server overwrites this for group tests                 |
| deleted      | bool       | no       | Defaults to false                                      |

### Sample request — group test

```json
{
  "name": "Nazorat ishi 1",
  "weight": 30,
  "term": 4,
  "subject": 12,
  "group": 190,
  "date": "2026-04-10"
}
```

### Sample request — flow test

```json
{
  "name": "Speaking Test",
  "weight": 25,
  "term": 4,
  "subject": 7,
  "flow": 5,
  "date": "2026-04-15"
}
```

### Sample response — 201 Created

```json
{
  "id": 410,
  "name": "Speaking Test",
  "weight": 25,
  "term": 4,
  "subject": 7,
  "group": null,
  "flow": 5,
  "class_number": null,
  "date": "2026-04-15",
  "deleted": false
}
```

### Error responses

| Status | Body                                                            |
|--------|-----------------------------------------------------------------|
| 400    | `{"non_field_errors": ["Either 'group' or 'flow' must be provided."]}` |
| 400    | `{"<field>": ["This field is required."]}`                      |

---

## 4. `PUT/PATCH terms/update-test/<pk>/`

Update an existing Test row. Same field rules as create. If `group` is set, `class_number` is rederived. If `group` is cleared and `flow` is used, `class_number` is set to NULL.

### Sample request

```json
{
  "name": "Nazorat ishi 1 (qayta)",
  "weight": 35,
  "flow": 5,
  "group": null
}
```

### Sample response — 200 OK

```json
{
  "id": 401,
  "name": "Nazorat ishi 1 (qayta)",
  "weight": 35,
  "term": 4,
  "subject": 12,
  "group": null,
  "flow": 5,
  "class_number": null,
  "date": "2026-04-10",
  "deleted": false
}
```

---

## 5. `POST lesson-plan/file/upload/`

Upload a lesson plan file. **Now accepts `subject_id`** so per-subject lesson plans no longer collide on the unique constraint `(teacher, term, group, flow, subject)`. Re-uploading for the same key replaces the previous file (`update_or_create`).

### Request — `multipart/form-data`

| Field      | Type            | Required | Notes                                         |
|------------|-----------------|----------|-----------------------------------------------|
| term_id    | int             | yes      |                                               |
| file       | file            | yes      | Allowed: `.txt .pdf .docx .xlsx`              |
| group_id   | int             | no       |                                               |
| flow_id    | int             | no       |                                               |
| subject_id | int             | no       | Recommended when teacher has multiple subjects |

### Sample response — 201 Created (new) / 200 OK (replaced)

```json
{
  "id": 87,
  "term_id": 4,
  "group_id": 190,
  "flow_id": null,
  "subject_id": 12,
  "status": "pending",
  "detail": "File uploaded. AI review started."
}
```

### Error responses

| Status | Body                                                       |
|--------|------------------------------------------------------------|
| 400    | `{"detail": "term_id and file are required."}`             |
| 400    | `{"detail": "Unsupported format. Allowed: .pdf, .docx, .txt, .xlsx"}` |
| 404    | `{"detail": "Term not found."}` / `"Group not found."` / `"Flow not found."` / `"Subject not found."` |

---

## 6. `GET lesson-plan/file/<id>/`

Single file status. **Now includes `subject`** in the response envelope.

### Sample response — 200 OK

```json
{
  "id": 87,
  "term": { "id": 4, "quarter": 4, "academic_year": "2025-2026" },
  "group":   { "id": 190, "name": "1-green" },
  "flow":    null,
  "subject": { "id": 12, "name": "Matematika" },
  "file": "/media/lesson_plan_files/2026/04/plan.pdf",
  "status": "done",
  "score": 82,
  "rating": 4,
  "feedback": "Dars rejasi yaxshi tuzilgan...",
  "uploaded_at": "2026-04-15T10:00:00Z",
  "reviewed_at": "2026-04-15T10:02:31Z"
}
```

| Status | Body                                | Cause                            |
|--------|-------------------------------------|----------------------------------|
| 404    | `{"detail": "Teacher not found."}`  | User has no Teacher row          |
| 404    | `{"detail": "File not found."}`     | Wrong id or not owned by teacher |

---

## 7. `GET lesson-plan/file/`

List the teacher's lesson plan files. **Now supports the `subject_id` filter and returns the `subject` block** in each item.

### Query params (all optional, all int)

| Name       | Notes                       |
|------------|-----------------------------|
| term_id    | Filter by term              |
| group_id   | Filter by group             |
| flow_id    | Filter by flow              |
| subject_id | Filter by subject (new)     |

### Sample response — 200 OK

```json
[
  {
    "id": 87,
    "term":    { "id": 4, "quarter": 4, "academic_year": "2025-2026" },
    "group":   { "id": 190, "name": "1-green" },
    "flow":    null,
    "subject": { "id": 12, "name": "Matematika" },
    "file": "/media/lesson_plan_files/2026/04/plan.pdf",
    "status": "done",
    "score": 82,
    "rating": 4,
    "feedback": "Dars rejasi yaxshi tuzilgan...",
    "uploaded_at": "2026-04-15T10:00:00Z",
    "reviewed_at": "2026-04-15T10:02:31Z"
  }
]
```

---

## Migration Checklist

These routes depend on schema changes that need migrations applied on every environment:

```bash
python manage.py makemigrations terms lesson_plan
python manage.py migrate
```

Changes applied by these migrations:

- `terms.Test`
  - **add** `flow_id` FK to `flows.Flow` (nullable, `on_delete=SET_NULL`)
  - **alter** `group_id` → nullable, `on_delete=SET_NULL`
  - **alter** `class_number_id` → nullable, `on_delete=SET_NULL`
- `lesson_plan.LessonPlanFile`
  - **add** `subject_id` FK to `subjects.Subject` (nullable, `on_delete=SET_NULL`)
  - **alter** `UniqueConstraint` → `(teacher, term, group, flow, subject)`

> Note: migrations are gitignored in this repo (`**/migrations/*` per `.gitignore`). Each environment must run `makemigrations` locally before `migrate`.

---

## Quick Auth Recap

```bash
# 1. Login (admin/test/teacher user with mobile access)
curl -X POST https://<host>/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"<username>","password":"<password>"}'

# → { "access": "...", "refresh": "..." }

# 2. Call any route above
curl -H "Authorization: Bearer <access>" \
  https://<host>/api/Mobile/teachers/terms/my-classes/
```
