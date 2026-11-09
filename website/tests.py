from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    Customer, Airline, Location, Plane,
    Booking, Invoice
)


class SkySyncTests(TestCase):

    def setUp(self):
        # Create customer user and group
        self.customer_group, _ = Group.objects.get_or_create(name="Customers")

        self.user = User.objects.create_user(
            username="testcustomer",
            password="TestPassword123!"
        )

        self.user.groups.add(self.customer_group)

        self.customer = Customer.objects.create(
            user=self.user
        )

        # Create airline user
        self.airline_group, _ = Group.objects.get_or_create(name="Airlines")

        self.airline_user = User.objects.create_user(
            username="testairline",
            password="TestPassword123!"
        )

        self.airline_user.groups.add(self.airline_group)

        self.airline = Airline.objects.create(
            user=self.airline_user
        )

        # Create flight locations
        self.start_location = Location.objects.create(
            location_name="London",
            coordinate_lat=51.5074,
            coordinate_long=-0.1278,
            userCreatorID=self.airline
        )

        self.end_location = Location.objects.create(
            location_name="Paris",
            coordinate_lat=48.8566,
            coordinate_long=2.3522,
            userCreatorID=self.airline
        )

        # Create plane with different seat capacities
        self.plane = Plane.objects.create(
            plane_name="Test Boeing 737",
            max_flight_time=Decimal("10.00"),
            average_speed=550,
            model_year=2024,
            max_weight=80000,
            userCreatorID=self.airline,
            economy_seats=100,
            economy_plus_seats=30,
            business_seats=20,
            first_class_seats=10
        )

        # Create a future flight
        self.booking = Booking.objects.create(
            booking_date=timezone.now() + timedelta(days=7),
            start_location_id=self.start_location,
            end_location_id=self.end_location,
            plane_id=self.plane,
            userCreatorID=self.airline,
            economy_price=Decimal("100.00"),
            economy_plus_price=Decimal("150.00"),
            business_price=Decimal("250.00"),
            first_class_price=Decimal("400.00")
        )

    # Check available seats are calculated correctly
    def test_available_seats(self):
        self.booking.economy_booked = 20
        self.booking.economy_plus_booked = 5
        self.booking.business_booked = 10
        self.booking.first_class_booked = 2

        self.booking.save()

        available = self.booking.available_seats()

        self.assertEqual(available['economy'], 80)
        self.assertEqual(available['economy_plus'], 25)
        self.assertEqual(available['business'], 10)
        self.assertEqual(available['first_class'], 8)

    # Check flight revenue is calculated correctly
    def test_total_revenue(self):
        self.booking.economy_booked = 2
        self.booking.economy_plus_booked = 3
        self.booking.business_booked = 1
        self.booking.first_class_booked = 1

        self.booking.save()

        expected_revenue = Decimal("1300.00")

        self.assertEqual(
            self.booking.total_revenue(),
            expected_revenue
        )

    # Check invoice seat totals and pricing
    def test_invoice_total_price(self):
        invoice = Invoice.objects.create(
            customerID=self.customer,
            bookingID=self.booking,
            economy_seats_booked=2,
            economy_plus_seats_booked=1,
            business_seats_booked=1,
            first_class_seats_booked=0
        )

        self.assertEqual(invoice.total_seats_booked, 4)

        expected_price = Decimal("600.00")

        self.assertEqual(invoice.total_price, expected_price)

    # Check a customer can successfully book a flight
    def test_customer_can_book_flight(self):
        self.client.force_login(self.user)

        response = self.client.post(
            f'/booking/{self.booking.bookingID}/book',
            {
                'economy_seats_booked': 2,
                'economy_plus_seats_booked': 1,
                'business_seats_booked': 0,
                'first_class_seats_booked': 0
            }
        )

        self.booking.refresh_from_db()
        self.customer.refresh_from_db()

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            Invoice.objects.filter(
                bookingID=self.booking,
                customerID=self.customer
            ).count(),
            1
        )

        self.assertEqual(self.booking.economy_booked, 2)
        self.assertEqual(self.booking.economy_plus_booked, 1)
        self.assertEqual(self.customer.amount_of_bookings, 1)

    # Check customers cannot book more seats than available
    def test_customer_cannot_overbook_flight(self):
        self.client.force_login(self.user)

        # Make all economy seats unavailable
        self.booking.economy_booked = 100
        self.booking.save()

        response = self.client.post(
            f'/booking/{self.booking.bookingID}/book',
            {
                'economy_seats_booked': 1,
                'economy_plus_seats_booked': 0,
                'business_seats_booked': 0,
                'first_class_seats_booked': 0
            }
        )

        self.booking.refresh_from_db()

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            Invoice.objects.filter(bookingID=self.booking).count(),
            0
        )

        self.assertEqual(self.booking.economy_booked, 100)

    def test_non_owner_cannot_mark_invoice_paid(self):
        invoice = Invoice.objects.create(customerID=self.customer, bookingID=self.booking,
                                        economy_seats_booked=1)
        self.client.force_login(self.user)   # a customer, not the booking's airline
        self.client.post(f'/booking/set_customer_as_paid/{self.booking.bookingID}/{self.user.id}')
        invoice.refresh_from_db()
        self.assertFalse(invoice.has_paid)

    def test_non_staff_cannot_view_tickets(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/view_tickets').status_code, 302)