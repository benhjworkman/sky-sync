from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import datetime, date
import math

def validate_future_date(value):
    if value < now():
        raise ValidationError("The booking date cannot be in the past.")

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    amount_of_bookings = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Airline(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    company_description = models.TextField(default="", max_length=650)
    amount_of_bookings = models.IntegerField(default=0)

    economy_description = models.TextField(default="", max_length=500)
    economy_plus_description = models.TextField(default="", max_length=500)
    business_description = models.TextField(default="", max_length=500)
    first_class_description = models.TextField(default="", max_length=500)
    def __str__(self):
        return self.user.username

class Location(models.Model):
    location_name = models.CharField(max_length=35, unique=True)
    coordinate_lat = models.FloatField()
    coordinate_long = models.FloatField()
    userCreatorID = models.ForeignKey(Airline, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.location_name}"

def user_dir_path(instance, filename):
    return f"profile_images/{instance.user.id}/{filename}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(default='default-profile-icon.jpg', upload_to='profile_images')
    completed_extra_info = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    about_me = models.TextField(default='', blank=True, max_length=400)


    def check_if_completed(self):
        required_fields_to_complete = [self.profile_picture, self.about_me, self.date_of_birth]
        if all(required_fields_to_complete):
            self.completed_extra_info = True
        else:
            self.completed_extra_info = False
        self.save()

    def calculate_user_age(self):
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year
            if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
                age -= 1
            return age
        return None

    def __str__(self):
        return f"Profile of {self.user.username}"


class Plane(models.Model):
    plane_name = models.CharField(max_length=35, unique=True)
    max_flight_time = models.DecimalField(validators=[MinValueValidator(0)], decimal_places=2, max_digits=5) #in hours
    average_speed = models.FloatField(validators=[MinValueValidator(0)]) #in mph
    model_year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(datetime.now().year)])
    max_weight = models.IntegerField(validators=[MinValueValidator(0)]) #kg
    userCreatorID = models.ForeignKey(Airline, on_delete=models.CASCADE)

    economy_seats = models.PositiveIntegerField(default=0)
    economy_plus_seats = models.PositiveIntegerField(default=0)
    business_seats = models.PositiveIntegerField(default=0)
    first_class_seats = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Name: {self.plane_name} - Model Year: {self.model_year}"


class Booking(models.Model):

    bookingID = models.AutoField(primary_key=True) #custom primary key
    booking_date = models.DateTimeField(validators=[validate_future_date])

    start_location_id = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='start_location_id')
    end_location_id = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='end_location_id')
    plane_id = models.ForeignKey(Plane, on_delete=models.CASCADE)
    userCreatorID = models.ForeignKey(Airline, on_delete=models.CASCADE)

    disabled_friendly = models.BooleanField(default=False)
    dateCreation = models.DateTimeField(auto_now_add=True)
    reminder_sent = models.BooleanField(default=False)

    economy_booked = models.PositiveIntegerField(default=0)
    economy_plus_booked = models.PositiveIntegerField(default=0)
    business_booked = models.PositiveIntegerField(default=0)
    first_class_booked = models.PositiveIntegerField(default=0)

    economy_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    economy_plus_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    business_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    first_class_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def available_seats(self):
        return {
            'economy': max(0, self.plane_id.economy_seats - self.economy_booked),
            'economy_plus': max(0, self.plane_id.economy_plus_seats - self.economy_plus_booked),
            'business': max(0, self.plane_id.business_seats - self.business_booked),
            'first_class': max(0, self.plane_id.first_class_seats - self.first_class_booked),
        }

    def is_fully_booked(self):
        check = 0
        for seats in self.available_seats():
            if seats != 0:
                check += 1
        if check == 0:
            return True
        return False

    def total_revenue(self):
        return (
            (self.economy_booked * self.economy_price) +
            (self.economy_plus_booked * self.economy_plus_price) +
            (self.business_booked * self.business_price) +
            (self.first_class_booked * self.first_class_price)
        )

    @property
    def calc_distance(self):
        start_location = self.start_location_id
        end_location = self.end_location_id

        lat1, lon1 = start_location.coordinate_lat, start_location.coordinate_long
        lat2, lon2 = end_location.coordinate_lat, end_location.coordinate_long
        lat1, lat2, lon1, lon2 = map(lambda x: x * (math.pi / 180), [lat1, lat2, lon1, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        earth_radius = 6371
        return earth_radius * c

    @property
    def calc_flight_time(self):
        current_plane = self.plane_id
        average_speed_in_mph = current_plane.average_speed
        average_speed_in_kph = average_speed_in_mph*1.609344
        flight_distance = self.calc_distance
        return (flight_distance/average_speed_in_kph)*60

    def __str__(self):
        return f"{self.userCreatorID} - {self.start_location_id} to {self.end_location_id} on {self.booking_date}"

class Invoice(models.Model):
    invoiceID = models.AutoField(primary_key=True)
    customerID = models.ForeignKey(Customer, on_delete=models.CASCADE)
    bookingID = models.ForeignKey(Booking, on_delete=models.CASCADE)
    date_of_creation = models.DateTimeField(auto_now_add=True)

    economy_seats_booked = models.PositiveIntegerField(default=0)
    economy_plus_seats_booked = models.PositiveIntegerField(default=0)
    business_seats_booked = models.PositiveIntegerField(default=0)
    first_class_seats_booked = models.PositiveIntegerField(default=0)

    has_paid = models.BooleanField(default=False)

    @property
    def total_seats_booked(self):
        return (
            self.economy_seats_booked +
            self.economy_plus_seats_booked +
            self.business_seats_booked +
            self.first_class_seats_booked
        )

    @property
    def total_price(self):
        return(
            (self.economy_seats_booked*self.bookingID.economy_price)
            + (self.economy_plus_seats_booked*self.bookingID.economy_plus_price)
            + (self.business_seats_booked*self.bookingID.business_price)
            + (self.first_class_seats_booked*self.bookingID.first_class_price)
        )

    def __str__(self):
        return (f"Invoice No. {self.invoiceID} |"
                f"Customer: {self.customerID.user.first_name} | Airline: {self.bookingID.userCreatorID.user.first_name} | "
                f"Total Seats Booked: {self.total_seats_booked}" f" | Total Price: £{self.total_price}")


class Ticket(models.Model):

    SUBJECT_CHOICES = [
        ("REPORT_ACCOUNT", "Report Another Account"),
        ("REPORT_BOOKING", "Report a Booking"),
        ("REPORT_INVOICE", "Report an Invoice Error"),
        ("REPORT_BOOKING_ERROR", "Report a Booking Error"),
        ("REPORT_BUG", "Report a Website Bug"),
        ("CONTACT_ADMIN", "Contact an Admin"),
        ("OTHER", "Other"),
    ]

    userCreatorID = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket_reason = models.CharField(
        max_length=50,
        choices=SUBJECT_CHOICES,
        default="OTHER"
    )
    ticket_title = models.CharField(max_length=100)
    ticket_description = models.TextField()
    successfully_fixed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.userCreatorID} | {self.get_ticket_reason_display()} - {self.ticket_title}"
