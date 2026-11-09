import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skysync.settings')
application = get_wsgi_application()

from website.models import *
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils.timezone import now
from datetime import timedelta
from skysync import settings

class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        current_time = now()
        one_day_later = current_time + timedelta(days=1)

        upcoming_bookings = Booking.objects.filter(
            reminder_sent=False,
            booking_date__lte=one_day_later,
            booking_date__gt=current_time
        )

        for booking in upcoming_bookings:
            recipients_list = []
            all_booking_invoices = Invoice.objects.filter(
                bookingID=booking.bookingID
            )
            for invoices in all_booking_invoices:
                recipient = invoices.customerID.user.email
                recipients_list.append(recipient)

            flight_time = booking.booking_date.strftime('%Y-%m-%d %H:%M')

            send_mail(
                subject=f"Flight Reminder for Booking with {booking.userCreatorID.user.first_name} on {flight_time}",
                message=f"We are emailing to remind you that you have a booking on SkySync that is going to take place within the next 24 hours.\n\n"
                        f"The flight is at {flight_time} and you are travelling from {booking.start_location_id.location_name} to {booking.end_location_id.location_name} \n\n"
                        f"If you would like to know more about this flight, please check the booking via your user profile on the site \n\n"
                        f"If this email was sent in error, or this booking is a mistake, please contact a SkySync admin via the ticket page.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients_list,
                fail_silently=False
            )

            booking.reminder_sent = True
            booking.save()

        self.stdout.write(self.style.SUCCESS(f"Sent {upcoming_bookings.count()} reminders"))

