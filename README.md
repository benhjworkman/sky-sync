# SkySync

A flight booking web application built with Django, where airlines publish
flights and customers book seats. [Solo project]

## Features

- **Two user types:** separate registration, login and profiles for customers
  and airlines
- **Airline tools:** create locations, planes and flights, view and edit bookings,
  see who has booked, and mark customers as paid or remove them
- **Customer tools:** browse flights, book seats, view bookings and invoices
- **Support tickets:** users can submit tickets and staff can mark them as fixed
- **Email reminders:** a management command emails customers about flights
  departing within 24 hours
- **Profile pages** with image upload
- **Staff accounts** with full access to the database using Django admin site.

## Tech stack

Python 3.12+, Django, SQLite, HTML/CSS, Bootstrap, JavaScript

## Getting started

```bash
git clone https://github.com/benhjworkman/sky-sync.git
cd skysync
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

### Configuration

Secrets are read from environment variables and are not stored in the repo:

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DJANGO_DEBUG` | `True` for local development |
| `EMAIL_HOST_USER` | SMTP account used for emails |
| `EMAIL_HOST_PASSWORD` | SMTP app password |

## Data model

`Customer`, `Airline`, `Location`, `Plane`, `Booking`, `Invoice`, `Ticket` and
`Profile`.

## Security notes

- Passwords are handled by Django's authentication system, with its password
  validators enabled
- CSRF protection on all forms
- Credentials and the secret key are loaded from environment variables
- Sample data is fictional

## What I would improve

- Add automated tests for the booking and payment logic
- Move from SQLite to PostgreSQL
- Add real payment processing

## Author
Benjamin Workman
