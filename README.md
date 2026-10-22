# Alderwick Family Health Web Application

The patient website and staff application for **Alderwick Family Health**, a fictional medical group with four clinics in the Salt Lake valley plus a video-visit service. Built with Django and SQLite.

The application serves four types of users:

| User | Area | What they do |
|---|---|---|
| Patients and visitors | Public site and patient portal | Find providers, request appointments, view records, send messages |
| Front office | `/staff/front-office/` | Work the request queue, schedule, check patients in, answer administrative messages |
| Doctors | `/staff/clinician/` | Review schedules and charts, write and sign notes, answer clinical messages |
| AI engineers | `/staff/ai-operations/` | AI operations workspace (empty: the application has no AI features) |

Sign-in details for every account are in **[USER-GUIDE.md](USER-GUIDE.md)**.

> **All data is synthetic.** Never enter real names, health information, insurance details, or credentials.

---

## Quick start in GitHub Codespaces

1. Open the repository in a Codespace. The dev container installs Django, creates the database, and loads the demo data automatically.
2. Start the server:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

3. Open the forwarded port 8000 when VS Code prompts you, or from the **Ports** tab.
4. Sign in with an account from [USER-GUIDE.md](USER-GUIDE.md).

## Quick start on your own computer

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

## Connecting to Gemini

All calls to Google's Gemini models go through [clinic/gemini.py](clinic/gemini.py). Its docstring has a usage example, so build new AI features on `gemini.generate_text()` instead of creating a separate client.

1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey) or your GCP project.
2. Add it as a Codespaces secret named `GEMINI_API_KEY`: on GitHub, **Settings → Codespaces → Secrets → New secret**, and give it access to this repository. (If you create the Codespace afterwards, GitHub will also prompt you for it.)
3. Rebuild or restart the Codespace so it picks up the secret. A Codespace that is already running does not see new secrets.
4. Start the server and open `/dev/gemini/` on the forwarded port. Send the default prompt. A green "It works" box means the key, project, and model are all set up correctly.

Optional environment variables:

| Variable | Purpose |
|---|---|
| `GEMINI_MODEL` | Model ID to use (default `gemini-3.5-flash-lite`) |
| `GOOGLE_GENAI_USE_VERTEXAI` | Which endpoint the key is sent to. The Codespace sets it to `true`, which sends requests to Vertex AI (`aiplatform.googleapis.com`), as GCP project keys need. With an AI Studio key, set it to `false`, which sends requests to `generativelanguage.googleapis.com`. Using the wrong endpoint for your key fails with `403 API_KEY_SERVICE_BLOCKED`. |

On your own computer, run `export GEMINI_API_KEY=...` before `runserver`. The `/dev/gemini/` page is not linked from the application and returns 404 when `DJANGO_DEBUG=0`. Send synthetic text only, never real patient information.

## Demo data

`seed_demo_data` loads the whole practice:

- 5 locations, 6 specialties, 7 insurance plans, and 24 providers with weekly schedules
- 100 patients (80 with portal accounts) with allergies, conditions, medications, visit notes, and lab results
- Today's clinic schedule, upcoming appointments, and unsigned notes
- An appointment request queue from the website, portal, and phone
- Secure message threads for the front office and care teams
- 9 patient-facing policy documents: new patients, cancellations, billing, visit preparation, video visits, refills, the portal, after-hours care, and privacy

Dates are generated relative to when you run the command, so there is always a "today." Names, usernames, passwords, and medical record numbers are the same every time.

```bash
python manage.py seed_demo_data --reset                          # wipe everything and reload
python manage.py seed_demo_data --reset --as-of 2026-12-08T09:00 # reload as if it were a specific time
```

`--reset` deletes **all** data, including user accounts and the audit log.

## Running the tests

```bash
python manage.py test
```

The suite covers models, scheduling and access rules, the demo-data loader (including a check that every account in the user guide exists), every view for every role, and the logging and audit system. Tests write logs to a temporary directory, never to `logs/`.

To measure coverage:

```bash
pip install coverage
coverage run manage.py test && coverage report
```

## Project layout

| Path | Purpose |
|---|---|
| `config/` | Settings, root URLs, and logging configuration |
| `accounts/` | Custom `User` model with a `role` field, sign-in and sign-out, and the `role_required` decorator |
| `clinic/` | Core data model, business logic (`services.py`), demo data (`seed.py`, `seed_content.py`), template tags, and test factories (`testing.py`) |
| `audit/` | `AuditLog` model, `log_event()` helper, sign-in signals, and request-logging middleware |
| `public/` | Public website: home, provider directory, locations, insurance, patient resources, and the appointment request form |
| `portal/` | Patient portal |
| `frontdesk/` | Front-office workspace |
| `clinician/` | Clinician workspace |
| `aiops/` | AI operations workspace |
| `templates/` | Shared layouts (`layouts/public.html`, `layouts/staff.html`) and includes |
| `static/css/alderwick.css` | All styles |

## Access rules

Access is enforced in server code, not only in the interface.

| Rule | Where it's enforced |
|---|---|
| Each workspace is limited to one role | `accounts.decorators.role_required` on every view (wrong role returns 403 and records an `access_denied` audit event) |
| Patients see only their own records, appointments, and messages | Portal views always query through `request.user.patient` |
| Doctors open charts only for patients they have a care relationship with | `clinic.services.provider_can_view_patient` (primary provider, or any appointment or visit with that provider) |
| Doctors edit only their own unsigned notes; signed notes are locked | `clinician.views.edit_note` and `Visit.sign()` |
| Front office sees demographics, insurance, and appointments, not clinical records | Front-office templates and views never load problems, medications, labs, or notes |
| Clinical messages go to the patient's primary provider; administrative ones go to the front office | `MessageThread.route()` |
| Appointments can only be booked into open slots on a provider's schedule | `clinic.services.book_appointment` |

## Logging and auditing

The application has two kinds of logs.

**1. Application logs** (`logs/alderwick.log`)

- `audit.middleware.RequestLoggingMiddleware` logs every request: method, path, status, duration, user, and role.
- Each request gets an ID, returned in the `X-Request-ID` response header, so one request can be traced through every log.
- Use the `alderwick.*` logger namespace for your own code:

  ```python
  import logging
  logger = logging.getLogger("alderwick.myfeature")
  logger.info("something happened id=%s", some_id)
  ```

**2. Audit log** (`logs/audit.log` and the `audit.AuditLog` table)

The audit log records who did what to which patient's data: sign-ins, failed sign-ins, denied access, chart views, scheduling, cancellations, messages, and note signing. Record an event with:

```python
from audit.models import AuditLog
from audit.utils import log_event

log_event(request, AuditLog.Action.VIEW_CHART, patient=patient, target=patient, section="labs")
```

Extra keyword arguments are stored as JSON in `details`. Never put clinical content in audit details. Administrators can browse the audit log (read-only) in the Django admin at `/admin/audit/auditlog/`.

Logging is configured in `config/settings.py` (`LOGGING`). Set `ALDERWICK_LOG_LEVEL=DEBUG` for more detail, or `ALDERWICK_LOG_DIR` to write logs elsewhere.

## Configuration

| Environment variable | Default | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | development key | Set a real value for any shared deployment |
| `DJANGO_DEBUG` | `1` | Set to `0` to turn off debug mode |
| `DJANGO_ALLOWED_HOSTS` | (none) | Extra comma-separated host names |
| `ALDERWICK_LOG_LEVEL` | `INFO` | Application log level |
| `ALDERWICK_LOG_DIR` | `logs/` | Where log files are written |

**Secrets** such as API keys belong in environment variables. In Codespaces, add them as [Codespaces secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces) and read them with `os.environ`. Never commit them. `.env` files are already in `.gitignore`.

## Notes

- `localhost`, `127.0.0.1`, and Codespaces `*.app.github.dev` addresses are allowed hosts. CSRF is configured for Codespaces port forwarding.
- Sessions last 8 hours.
- Alderwick Family Health, its staff, patients, insurance plans, and phone numbers (555-01xx) are fictional.
- Some change here to the readme.
