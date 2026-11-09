from django import forms
from .models import Booking, Location, Plane, Profile, Ticket, Airline, Invoice
from datetime import datetime, date
from django.utils.timezone import now


class create_booking_form(forms.ModelForm):

    booking_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text = "Select a future date and Time"
    )

    start_location_id = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Start Location"
    )

    end_location_id = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select End Location"
    )

    plane_id = forms.ModelChoiceField(
        queryset=Plane.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Plane"
    )

    economy_price = forms.DecimalField(
        required=True, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Price for Economy Seat"
    )

    economy_plus_price = forms.DecimalField(
        required=True, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Price for Economy Plus Seat"
    )

    business_price = forms.DecimalField(
        required=True, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Price for Business Seat"
    )

    first_class_price = forms.DecimalField(
        required=True, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Price for First Class Seat"
    )

    disabled_friendly = forms.BooleanField(
        widget = forms.CheckboxInput(),
        required=False)



    class Meta:
        model = Booking
        fields = [
            'booking_date', 'start_location_id', 'end_location_id',
            'plane_id', 'disabled_friendly','economy_price',
            'economy_plus_price', 'business_price', 'first_class_price'
        ]

    def clean_booking_date(self):
        booking_datetime = self.cleaned_data.get('booking_date')
        if booking_datetime <= now():
            raise forms.ValidationError("Please select a booking date that is in the future")
        return booking_datetime

    def clean_booking_seats(self):
        cleaned_data = super().clean()
        plane = cleaned_data.get("plane_id")

        if plane:
            # Ensure users do not book more seats than available on the selected plane
            if cleaned_data.get("economy_booked", 0) > plane.economy_seats:
                self.add_error("economy_booked", "Not enough economy seats available.")

            if cleaned_data.get("economy_plus_booked", 0) > plane.economy_plus_seats:
                self.add_error("economy_plus_booked", "Not enough economy plus seats available.")

            if cleaned_data.get("business_booked", 0) > plane.business_seats:
                self.add_error("business_booked", "Not enough business seats available.")

            if cleaned_data.get("first_class_booked", 0) > plane.first_class_seats:
                self.add_error("first_class_booked", "Not enough first-class seats available.")

        return cleaned_data

class create_location_form(forms.ModelForm):

    location_name = forms.CharField(
        max_length = 35,
        widget = forms.TextInput(attrs={'class': 'form-control'})
    )

    coordinate_lat = forms.DecimalField(
        max_digits=6,
        max_value=90,
        min_value=-90,
        decimal_places=4,
        widget = forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Please enter the Latitude for the Location to 4 decimal places. "
    )

    coordinate_long = forms.DecimalField(
        max_digits=6,
        max_value=90,
        min_value=-90,
        decimal_places=4,
        widget = forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Please enter the Longitude for the Location to 4 decimal places. "
    )


    def clean_location(self):
        latitude = self.cleaned_data.get("coordinate_lat")
        longitude = self.cleaned_data.get("coordinate_long")
        if Location.objects.filter(coordinate_lat=latitude, coordinate_long=longitude).exists():
            raise forms.ValidationError("This Location has already been saved to the database")


    class Meta:
        model = Location
        fields = ['location_name', 'coordinate_long', 'coordinate_lat']


class profile_update_form(forms.ModelForm):

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )

    class Meta:
        model = Profile
        fields = ['profile_picture', 'about_me', 'date_of_birth']

    def clean_date_of_birth(self):
        booking_date_of_birth = self.cleaned_data.get('date_of_birth')
        if booking_date_of_birth >= date.today():
            raise forms.ValidationError("Please select a date of birth that is in the past")
        return booking_date_of_birth

# endregion

class bookings_filter_form(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Start Date"
    )
    start_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Start Location"
    )
    end_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="End Location"
    )
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Min Price"}),
        label="Minimum Price"
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Max Price"}),
        label="Maximum Price"
    )
    is_disabled_friendly = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Disabled-Friendly"
    )

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date <= datetime.today().date():
            raise forms.ValidationError("Please select a booking date that is in the future")
        return start_date

    def clean_locations(self):
        start_location = self.cleaned_data.get('start_location')
        end_location = self.cleaned_data.get('end_location')
        if start_location and end_location and start_location == end_location:
            raise forms.ValidationError("Please select different locations for the start and end locations")


class create_plane_form(forms.ModelForm):

    plane_name = forms.CharField(
        max_length = 20,
        widget = forms.TextInput(attrs={'class': 'form-control'})
    )

    max_flight_time = forms.DecimalField(
        min_value=0,
        widget = forms.NumberInput(attrs={'class': 'form-control'}),
        help_text = "Please enter the maximum amount of time that your plane can fly for at once."
    )

    average_speed = forms.IntegerField(
        min_value=0,
        widget = forms.NumberInput(attrs={'class': 'form-control'}),
        help_text = "Please enter the average speed of the plane rounded to the nearest whole number in MPH"
    )

    model_year = forms.IntegerField(
        min_value=1990,
        max_value=datetime.now().year,
        help_text = "Enter the year that the plane was manufactured"
    )

    max_weight = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Please enter the maximum weight that the plane can hold in KGs to the nearest KG"
    )

    economy_seats = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Number of economy class seats on the plane."
    )

    economy_plus_seats = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Number of economy plus class seats on the plane."
    )

    business_seats = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Number of business class seats on the plane."
    )

    first_class_seats = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Number of first class seats on the plane."
    )

    def clean_plane(self):
        plane_name = self.cleaned_data.get('plane_name')
        model_year = self.cleaned_data.get('model_year')
        if Plane.objects.filter(plane_name=plane_name, model_year=model_year).exists():
            raise forms.ValidationError("This plane has already been registered to the database")



    class Meta:
        model = Plane
        fields = [
            'plane_name',
            'max_flight_time',
            'average_speed',
            'model_year',
            'max_weight',
            'economy_seats',
            'economy_plus_seats',
            'business_seats',
            'first_class_seats'
        ]


class remove_customer_form(forms.Form):

    REASONS_FOR = [
        ('fraud', 'Fraudulent Account'),
        ('inactive', 'Inactive account'),
        ('request', 'Customer request'),
        ('other', 'Other'),
    ]

    reason_for_removal = forms.ChoiceField(
        choices=REASONS_FOR,
        label="Reason for Removal",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    further_removal_description = forms.CharField(
        widget = forms.Textarea(attrs={'class': 'form-control'})
    )


class create_a_ticket_form(forms.ModelForm):

    ticket_reason = forms.ChoiceField(
        choices=Ticket.SUBJECT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the reason for submitting this ticket."
    )

    ticket_title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ticket title'}),
        help_text="Provide a brief title for your issue."
    )

    ticket_description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the issue in detail'}),
        help_text="Describe your issue as clearly as possible."
    )

    class Meta:
        model = Ticket
        fields = ['ticket_reason', 'ticket_title', 'ticket_description']


class Tickets_filter_form(forms.Form):

    filter_completed = forms.BooleanField(
        widget = forms.CheckboxInput(attrs={'class': 'form-control'}),
        required = False,
        label = "has the ticket been completed?"
    )

    reason = forms.ChoiceField(
        choices=[("", "All Reasons")] + Ticket.SUBJECT_CHOICES,  # Add "All Reasons" option
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Reason For Ticket"
    )

class Invoice_filter_form(forms.Form):

    filter_paid = forms.BooleanField(
        widget = forms.CheckboxInput(attrs={'class': 'form-control'}),
        required = False,
        label = "Filter paid invoices"
    )

    filter_outstanding_bookings = forms.BooleanField(
        widget = forms.CheckboxInput(attrs={'class': 'form-control'}),
        required = False,
        label="Filter invoices to ones that with bookings that have not already passed"
    )


class airline_ticket_descriptions_form(forms.ModelForm):
    class Meta:
        model = Airline
        fields = ['economy_description', 'economy_plus_description', 'business_description', 'first_class_description']



class book_flights_form(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['economy_seats_booked', 'economy_plus_seats_booked', 'business_seats_booked', 'first_class_seats_booked']

    def __init__(self, *args, **kwargs):
        self.booking = kwargs.pop('booking', None)  # Get the booking instance
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        economy_requested = cleaned_data.get('economy_seats_booked', 0)
        economy_plus_requested = cleaned_data.get('economy_plus_seats_booked', 0)
        business_requested = cleaned_data.get('business_seats_booked', 0)
        first_class_requested = cleaned_data.get('first_class_seats_booked', 0)

        total_seats_requested = economy_requested + economy_plus_requested + business_requested + first_class_requested

        if total_seats_requested <= 0:
            raise forms.ValidationError("You must book at least one seat.")

        if self.booking:
            plane = self.booking.plane_id

            # Check seat availability
            if economy_requested > (plane.economy_seats - self.booking.economy_booked):
                raise forms.ValidationError(f"Not enough Economy seats available. Remaining: {plane.economy_seats - self.booking.economy_booked}")

            if economy_plus_requested > (plane.economy_plus_seats - self.booking.economy_plus_booked):
                raise forms.ValidationError(f"Not enough Economy Plus seats available. Remaining: {plane.economy_plus_seats - self.booking.economy_plus_booked}")

            if business_requested > (plane.business_seats - self.booking.business_booked):
                raise forms.ValidationError(f"Not enough Business seats available. Remaining: {plane.business_seats - self.booking.business_booked}")

            if first_class_requested > (plane.first_class_seats - self.booking.first_class_booked):
                raise forms.ValidationError(f"Not enough First Class seats available. Remaining: {plane.first_class_seats - self.booking.first_class_booked}")

        return cleaned_data
