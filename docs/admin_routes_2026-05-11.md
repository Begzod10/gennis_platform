# Admin / Web Routes — Update Notes (2026-05-11)

Scope: non-mobile routes touched **today**. The only schema change today was on `terms.Test`
(added `flow` FK, relaxed `group` / `class_number` to nullable). That changed the
contract of these two admin endpoints, which share `TestCreateUpdateSerializer`:

- `POST /api/terms/create-test/`
- `PUT  /api/terms/update-test/<pk>/`
- `PATCH /api/terms/update-test/<pk>/`

All routes require `Authorization: Bearer <access>` from `/api/token/`.

---

## Model Change Summary — `terms.Test`

| Field         | Before                                       | After                                                  |
|---------------|----------------------------------------------|--------------------------------------------------------|
| `group`       | FK, `on_delete=CASCADE`, NOT NULL            | FK, `on_delete=SET_NULL`, NULL OK                      |
| `class_number`| FK, `on_delete=CASCADE`, NOT NULL            | FK, `on_delete=SET_NULL`, NULL OK                      |
| `flow`        | —                                            | **new** FK to `flows.Flow`, `on_delete=SET_NULL`, NULL OK |

A Test row is now valid when **at least one** of `group` or `flow` is set. The
serializer enforces this:

> `Either 'group' or 'flow' must be provided.`

When `group` is set, the serializer auto-derives `class_number` from
`group.class_number`. When only `flow` is set, `class_number` is stored as `NULL`.

---

## 1. `POST /api/terms/create-test/`

Create a Test row. Now supports `flow` in addition to `group`.

### Request body — JSON

| Field        | Type       | Required | Notes                                                            |
|--------------|------------|----------|------------------------------------------------------------------|
| `name`       | string     | yes      |                                                                  |
| `weight`     | int        | yes      | Test weight (sum across a term ideally ≤ 100)                    |
| `term`       | int (FK)   | yes      | `terms.Term.id`                                                  |
| `subject`    | int (FK)   | yes      | `subjects.Subject.id`                                            |
| `date`       | YYYY-MM-DD | no       | Defaults to today                                                |
| `group`      | int (FK)   | one-of   | `group.Group.id`. When set, `class_number` is derived from group |
| `flow`       | int (FK)   | one-of   | `flows.Flow.id`. Use for flow-only tests                         |
| `class_number` | int (FK) | no       | Server overwrites this for group tests; ignored for flow tests   |
| `deleted`    | bool       | no       | Soft-delete flag; defaults to false                              |

> At least one of `group` or `flow` is required. If both are sent, both are stored
> as-is — the serializer does not currently force mutual exclusivity, but downstream
> list endpoints treat group tests and flow tests separately.

### Sample request — group test

```http
POST /api/terms/create-test/
Authorization: Bearer <access>
Content-Type: application/json
```

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

### Sample response — 201 Created

```json
{
  "id": 401,
  "name": "Nazorat ishi 1",
  "weight": 30,
  "term": 4,
  "subject": 12,
  "group": 190,
  "flow": null,
  "class_number": 1,
  "date": "2026-04-10",
  "deleted": false
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

| Status | Body                                                                                   |
|--------|----------------------------------------------------------------------------------------|
| 400    | `{"non_field_errors": ["Either 'group' or 'flow' must be provided."]}`                 |
| 400    | `{"<field>": ["This field is required."]}` — when `name` / `weight` / `term` / `subject` missing |
| 400    | `{"<field>": ["Invalid pk \"X\" - object does not exist."]}` — bad FK id                 |

---

## 2. `PUT /api/terms/update-test/<pk>/`  (and `PATCH`)

Update an existing Test row. Same field rules as create. If `group` is set on the
update, `class_number` is rederived from `group.class_number`. If `group` is
cleared (set to `null`) and only `flow` remains, `class_number` is set to NULL.

### Sample request — switch a group test to a flow test

```http
PATCH /api/terms/update-test/401/
Authorization: Bearer <access>
Content-Type: application/json
```

```json
{
  "name": "Nazorat ishi 1 (qayta)",
  "weight": 35,
  "group": null,
  "flow": 5
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

### Sample request — change only the date

```json
{ "date": "2026-04-12" }
```

### Sample response — 200 OK

Full Test object as above, with `date` updated.

### Error responses

| Status | Body                                                                  |
|--------|-----------------------------------------------------------------------|
| 404    | `{"detail": "Not found."}` — wrong `pk`                                 |
| 400    | `{"non_field_errors": ["Either 'group' or 'flow' must be provided."]}` |
| 400    | `{"<field>": ["Invalid pk \"X\" - object does not exist."]}`           |

---

## Migration Checklist

```bash
python manage.py makemigrations terms
python manage.py migrate
```

The migration adds `flow_id` to `terms_test`, makes `group_id` and
`class_number_id` nullable, and switches their `on_delete` from `CASCADE` to
`SET_NULL`.

> Migrations are gitignored in this repo (`**/migrations/*`). Run
> `makemigrations` on every environment before deploying.

---

## 3. `GET /api/terms/list-test/<term>/<branch>/`

All Tests in a term, grouped by group and by flow, scoped to a branch. Rewritten
today to mirror the mobile `TeacherListTest` shape and to include flow-only
tests.

### Path params

| Name    | Type | Notes                                |
|---------|------|--------------------------------------|
| term    | int  | Must exist in `terms_term`. 404 else |
| branch  | int  | `branch.Branch.id`                   |

### What it returns

- One **group** block per non-deleted group in the branch (ordered by
  `class_number.number`).
- One **flow** block per flow in the branch (ordered by `Flow.order` then `id`),
  skipped when `flow.subject_id IS NULL`.
- Tests for a single term are bucketed by `(group_id, subject_id)` and
  `(flow_id, subject_id)`.

### Sample response — 200 OK

```json
[
  {
    "title": "1 green",
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
      },
      {
        "title": "Ona tili",
        "id": 18,
        "type": "subject",
        "tableData": []
      }
    ]
  },
  {
    "title": "2 red",
    "id": 191,
    "type": "group",
    "children": []
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

### Differences vs the mobile (`teachers/terms/list-test/`) variant

| Concern             | Admin (`/api/terms/list-test/`)        | Mobile (`teachers/terms/list-test/`)              |
|---------------------|----------------------------------------|---------------------------------------------------|
| Scope               | Branch + term                          | Authenticated teacher + term                      |
| Group source        | `Group.branch = <branch>` (no teacher) | `ClassTimeTable.group` ∪ `Group.teacher` M2M      |
| Subject source      | All `GroupSubjects` for the group       | Only subjects the teacher actually teaches        |
| Flow scope          | `Flow.branch = <branch>`                | `Flow.teacher = <current>`                        |
| Empty groups        | **Returned** (admin view of branch)    | **Omitted** (teacher only wants their own slate)  |

### Error responses

| Status | Body                       | Cause              |
|--------|----------------------------|--------------------|
| 404    | `{"detail": "Not found."}` | Unknown `term`     |

### Query counts

Five constant queries regardless of branch size:
1. `Group` (with `class_number`, `color`)
2. `Flow` (with `subject`)
3. `GroupSubjects` (joined to `subject`)
4. `Test` (single query covering group + flow tests for the term)
5. `Term.get(id=…)` (validation)

Previously this view fired `1 + G + G·S` queries (one Test query per
group×subject cell), which scaled badly with branch size.
