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

## Tech stack

Python 3.9+, Django, SQLite, HTML/CSS, Bootstrap, JavaScript

### Configuration

Secrets are read from environment variables and are not stored in the repo:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for local development |
| `EMAIL_HOST_USER` | SMTP account used for emails |
| `EMAIL_HOST_PASSWORD` | SMTP app password |

Email reminders can be run manually with `python manage.py send_booking_reminders`.

## Data model

`Customer`, `Airline`, `Location`, `Plane`, `Booking`, `Invoice`, `Ticket` and
`Profile`, with relationships between them designed around [normalised
relational design].

## Security notes

- Passwords are handled by Django's authentication system, with its password
  validators enabled
- CSRF protection on all forms

## What I would improve

- Add automated tests for the booking and payment logic
- Move from SQLite to PostgreSQL
- Add real payment processing


## Author

Benjamin Workman