# Evason International Secondary School: Django website and results portal

## Quick start
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_school        # creates JSS1 to SS3, starter subjects and the current term
python manage.py createsuperuser    # your administrator login
python manage.py runserver
```
Open http://127.0.0.1:8000/

## How it works
| Who | What they can do |
|---|---|
| Student | Registers at `/register/`, picks a class (JSS1 to SS3), gets a registration number (e.g. EIS-2026-0001) used to log in. Sees only their own **published** results at `/dashboard/results/`. |
| Administrator (superuser or role "Administrator") | Everything: assign subjects to classes (`/portal/subjects/`), upload and publish results, manage users in `/admin/`. |
| Result-admin teacher | Create the user in `/admin/` with role "Teacher", then add a **Teacher profile** and tick "Result admin". They can upload and publish results for any class. |
| Ordinary teacher | Can view classes, students and broadsheets only. |

## Uploading results
1. `/portal/` then type the student's registration number and choose the term (or open a class and click *Enter results*).
2. The form lists exactly the subjects assigned to that student's class. Enter first test (/20), second test (/20) and exam (/60).
3. Total, grade, average and class position are calculated automatically.
4. Tick **Publish** to show it on the student's dashboard, or save as a draft. Use *Publish all* on the class page to release a whole class.

Grades: A 70+, B 60 to 69, C 50 to 59, D 45 to 49, E 40 to 44, F below 40 (edit `GRADE_SCALE` in `academics/models.py`).

## Customising
* School name, address, phone, email: `SCHOOL` in `evason/settings.py`.
* New terms: `/admin/` then Terms (tick *Is current* for the active term).
* Page text: `templates/website/*.html`. Colours and fonts: `static/css/style.css`.

## Going live
Set `DJANGO_DEBUG=0`, a real `DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS`; run `python manage.py collectstatic`; serve with gunicorn plus nginx (or WhiteNoise); consider PostgreSQL instead of SQLite.
