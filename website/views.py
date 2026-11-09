from skysync import settings
from .models import *
from .forms import *
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from .models import Booking, Airline, Invoice
from .forms import create_booking_form


def home(request):
    current_user_id = request.user.id
    return render(request, 'home.html', {'current_user_id': current_user_id})

def view_bookings(request):
    all_bookings = Booking.objects.all()
    form = bookings_filter_form(request.GET or None)

    if form.is_valid():
        if form.cleaned_data.get("start_date"):
            all_bookings = all_bookings.filter(booking_date__date=form.cleaned_data["start_date"])

        if form.cleaned_data.get("start_location"):
            all_bookings = all_bookings.filter(start_location_id=form.cleaned_data["start_location"])

        if form.cleaned_data.get("end_location"):
            all_bookings = all_bookings.filter(end_location_id=form.cleaned_data["end_location"])

        if form.cleaned_data.get("min_price") is not None:
            all_bookings = all_bookings.filter(economy_price__gte=form.cleaned_data["min_price"])

        if form.cleaned_data.get("max_price") is not None:
            all_bookings = all_bookings.filter(economy_price__lte=form.cleaned_data["max_price"])

        if form.cleaned_data.get("is_disabled_friendly"):
            all_bookings = all_bookings.filter(disabled_friendly=True)

    start_location = request.GET.get("start_location")
    end_location = request.GET.get("end_location")

    selected_start_location = None
    selected_end_location = None

    if start_location:
        selected_start_location = get_object_or_404(Location, id=int(start_location))
    if end_location:
        selected_end_location = get_object_or_404(Location, id=int(end_location))

    return render(request, 'booking_system/view_bookings.html', {
        'all_bookings': all_bookings,
        'form': form,
        'selected_start_location': selected_start_location,
        'selected_end_location': selected_end_location
    })



def booking_details(request, booking_id):
    booking = get_object_or_404(Booking, bookingID=booking_id)
    flight_time_hours = booking.calc_flight_time / 60
    return render(request, 'booking_system/booking_details.html', {
        'booking': booking,
        'flight_time_hours': flight_time_hours,
        'start_latitude': booking.start_location_id.coordinate_lat,
        'start_longitude': booking.start_location_id.coordinate_long,
        'end_latitude': booking.end_location_id.coordinate_lat,
        'end_longitude': booking.end_location_id.coordinate_long
    })



def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, bookingID=booking_id)
    booking_user = booking.userCreatorID.id
    current_user = Airline.objects.get(user=request.user).id

    is_allowed = booking_user == current_user

    if request.method == "POST":
        form = create_booking_form(request.POST, instance=booking)
        if form.is_valid():
            updated_booking = form.save(commit=False)
            old_booking = get_object_or_404(Booking, bookingID=booking_id)
            updated_booking_date = form.cleaned_data['booking_date']

            if updated_booking_date != old_booking.booking_date:
                updated_booking.reminder_sent = False

            updated_booking.userCreatorID = Airline.objects.get(id=current_user)

            changed_fields = []
            for field in ['booking_date', 'start_location_id', 'end_location_id', 'plane_id',
                          'economy_price', 'economy_plus_price', 'business_price', 'first_class_price']:
                old_value = getattr(old_booking, field)
                new_value = getattr(updated_booking, field)
                if old_value != new_value:
                    changed_fields.append((field, old_value, new_value))

            updated_booking.save()

            if changed_fields:
                invoices = Invoice.objects.filter(bookingID=updated_booking)
                customer_emails = [invoice.customerID.user.email for invoice in invoices if invoice.customerID.user.email]

                if customer_emails:
                    email_subject = "Update: Your Flight Booking Has Changed"
                    email_body = f"Dear Customer,\n\nThe following changes have been made to your flight booking:\n"
                    for field, old_value, new_value in changed_fields:
                        email_body += f"- {field.replace('_', ' ').title()}: {old_value} ➝ {new_value}\n"
                    email_body += "\nPlease check your booking details and contact support if needed.\n\nBest regards,\nYour Airline Team"

                    send_mail(
                        email_subject,
                        email_body,
                        settings.DEFAULT_FROM_EMAIL,
                        customer_emails,
                        fail_silently=True
                    )

            messages.success(request, "Your Booking has now been updated, and the changes have been emailed to all passengers signed-up!")
            return redirect('view_your_bookings')

    else:
        form = create_booking_form(instance=booking)

    return render(request, 'booking_management_system/edit_booking.html', {'form': form, 'booking': booking, 'is_allowed': is_allowed})



def registration_email(request):
    user = request.user
    user_first_name = user.first_name
    user_email = user.email
    user_last_name = user.last_name
    if request.user.groups.filter(name="Customers").exists():
        group = "Customers"
    elif request.user.groups.filter(name="Airlines").exists():
        group = "Airlines"
    else:
        group = "ERROR"

    subject = "Welcome to our site"
    message = (f"Thank you {user_first_name} for registering! You have registered for a {group} account, and if that "
               f"has been done in error, please contact an admin via a ticket.\n\n"
               f"To get started, please take a look at your profile page to finish setting up your account\n\n"
               f"The email that we have recorded in our system is {user_email}\n\n"
               f"The Last Name that we have recorded in our system is {user_last_name}\n\n"
               f"If any of this information is incorrect, or there is something that you need to change, "
               f"please either contact an admin via a ticket or change it through your profile.\n\n"
               f"We hope you enjoy your stay on SkySync!")
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
    messages.success(request, "Check your emails!")
    return redirect('home')


def bookings_dashboard(request):
    return render(request, 'booking_management_system/bookings_dashboard.html', {})


def create_bookings(request):
    if request.method == "POST":
        form = create_booking_form(request.POST)
        if form.is_valid():
            booking_date = form.cleaned_data['booking_date']
            start_location_id = form.cleaned_data['start_location_id']
            end_location_id = form.cleaned_data['end_location_id']
            plane = form.cleaned_data['plane_id']
            disabled_friendly = form.cleaned_data['disabled_friendly']
            economy_price = form.cleaned_data['economy_price']
            economy_plus_price = form.cleaned_data['economy_plus_price']
            business_price = form.cleaned_data['business_price']
            first_class_price = form.cleaned_data['first_class_price']

            user_airline = Airline.objects.get(user=request.user)
            booking = Booking.objects.create(
                booking_date=booking_date,
                start_location_id=start_location_id,
                end_location_id=end_location_id,
                plane_id=plane,
                userCreatorID=user_airline,
                disabled_friendly=disabled_friendly,
                economy_price=economy_price,
                economy_plus_price=economy_plus_price,
                business_price=business_price,
                first_class_price=first_class_price,
                economy_booked=0,
                economy_plus_booked=0,
                business_booked=0,
                first_class_booked=0,
            )

            airline_user = get_object_or_404(Airline, user_id=request.user.id)
            airline_user.amount_of_bookings += 1
            airline_user.save()

            messages.success(request, "Booking has been created. Customers can now book seats.")
            return redirect('view_your_bookings')

    else:
        form = create_booking_form()

    return render(request, 'booking_management_system/create_bookings.html', {'form': form})


def create_locations(request):
    if request.method == "POST":
        form = create_location_form(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            user_airline = Airline.objects.get(user=request.user)
            location.userCreatorID = user_airline
            location_name = form.cleaned_data['location_name']
            coordinate_lat = form.cleaned_data['coordinate_lat']
            coordinate_long = form.cleaned_data['coordinate_long']
            location = Location.objects.create(
                userCreatorID=user_airline,
                coordinate_lat=coordinate_lat,
                coordinate_long=coordinate_long,
                location_name=location_name
            )
            messages.success(request, "Congratulations, you have just registered a new Location")
            return redirect('bookings_dashboard')
    else:
        form = create_location_form()
    return render(request, 'booking_management_system/create_location.html', {'form': form})


def create_planes(request):
    if request.method == "POST":
        form = create_plane_form(request.POST)
        if form.is_valid():
            plane = form.save(commit=False)
            user_airline = Airline.objects.get(user=request.user)
            plane.userCreatorID = user_airline

            plane_name = form.cleaned_data['plane_name']
            max_weight = form.cleaned_data['max_weight']
            average_speed = form.cleaned_data['average_speed']
            model_year = form.cleaned_data['model_year']
            max_flight_time = form.cleaned_data['max_flight_time']
            economy_seats = form.cleaned_data['economy_seats']
            economy_plus_seats = form.cleaned_data['economy_plus_seats']
            business_seats = form.cleaned_data['business_seats']
            first_class_seats = form.cleaned_data['first_class_seats']

            plane = Plane.objects.create(
                userCreatorID=user_airline,
                plane_name=plane_name,
                max_weight=max_weight,
                average_speed=average_speed,
                model_year=model_year,
                max_flight_time=max_flight_time,
                economy_seats=economy_seats,
                economy_plus_seats=economy_plus_seats,
                business_seats=business_seats,
                first_class_seats=first_class_seats
            )
            messages.success(request, "Congratulations you have registered a new plane for the website!")
            return redirect('bookings_dashboard')
    else:
        form = create_plane_form()
    return render(request, 'booking_management_system/create_plane.html', {'form': form})


def view_your_bookings(request):
    if request.user.groups.filter(name="Customers").exists():
        customer = Customer.objects.get(user=request.user)
        all_user_invoices = Invoice.objects.filter(customerID=customer)
        all_user_bookings = Booking.objects.filter(id__in=all_user_invoices.values_list('bookingID', flat=True))

    elif request.user.groups.filter(name="Airlines").exists():
        airline = Airline.objects.get(user=request.user)
        all_user_bookings = Booking.objects.filter(userCreatorID=airline)

    else:
        return redirect('home')

    return render(request, 'booking_system/view_your_bookings.html', {'all_user_bookings': all_user_bookings})


def redirect_to_profile(request):
    if request.user.is_authenticated:
        return redirect('user_profile', user_id=request.user.id)
    messages.error(request, "Please login to visit your profile page.")
    return redirect('home')


def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    current_user = request.user
    is_own_profile = current_user == user

    last_three_bookings = None

    if user.groups.filter(name="Customers").exists():
        try:
            customer = Customer.objects.get(user=user)
            previous_invoices = Invoice.objects.filter(customerID=customer).order_by('-date_of_creation')[:3]
            last_three_bookings = [invoice.bookingID for invoice in previous_invoices]
        except Customer.DoesNotExist:
            pass

        if is_own_profile and not user.profile.completed_extra_info:
            messages.success(request, 'Please press "Edit Profile" in order to complete your profile!')

    elif user.groups.filter(name="Airlines").exists():
        try:
            airline = Airline.objects.get(user=user)
            last_three_bookings = Booking.objects.filter(userCreatorID=airline).order_by('-dateCreation')[:3]
        except Airline.DoesNotExist:
            pass

    profile_picture = user.profile.profile_picture

    return render(request, 'profiles/profile.html', {
        'profile_picture': profile_picture,
        'user': user,
        'last_three_bookings': last_three_bookings,
        'is_own_profile': is_own_profile
    })


def edit_user_profile(request):
    profile = Profile.objects.get(user=request.user)
    user_id = request.user.id
    if request.method == "POST":
        form = profile_update_form(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            profile.check_if_completed()
            return redirect('user_profile', user_id)
    else:
        form = profile_update_form(instance=profile)

    return render(request, 'profiles/edit_user_profile.html', {'form': form})

@login_required
def view_booking_customers(request, booking_id):
    booking_id = booking_id
    bookings = get_object_or_404(Booking, bookingID=booking_id)
    related_invoices = Invoice.objects.filter(bookingID=bookings)
    all_customers = [invoice.customerID for invoice in related_invoices]

    return render(request, 'booking_management_system/view_booking_customers.html',
                  {'all_customers': all_customers, 'booking': bookings})


def remove_customer(request, booking_id, user_id):
    booking = get_object_or_404(Booking, bookingID=booking_id)
    current_user_id = request.user.id
    if booking.userCreatorID.user.id != current_user_id:
        messages.success(request, 'You are not allowed to edit this booking as you are not the creator')
        return redirect('home')

    if request.method == "POST":
        form = remove_customer_form(request.POST)
        if form.is_valid():
            reason_for_removal = form.cleaned_data['reason_for_removal']
            further_removal_description = form.cleaned_data['further_removal_description']

            customer = get_object_or_404(Customer, user_id=user_id)
            user = customer.user

            related_invoices = Invoice.objects.filter(bookingID=booking_id, customerID=customer)

            if related_invoices.exists():
                for invoice in related_invoices:
                    # Ensure the number of booked seats doesn't go negative
                    booking.economy_booked = max(0, booking.economy_booked - invoice.economy_seats_booked)
                    booking.economy_plus_booked = max(0, booking.economy_plus_booked - invoice.economy_plus_seats_booked)
                    booking.business_booked = max(0, booking.business_booked - invoice.business_seats_booked)
                    booking.first_class_booked = max(0, booking.first_class_booked - invoice.first_class_seats_booked)
                    booking.save()

                    invoice.delete()

            else:
                print(f"No invoices found for booking {booking_id}, customer {user_id}")

            startlocationname = booking.start_location_id.location_name
            endlocationname = booking.end_location_id.location_name
            subject = "Account Removal Notification"
            message = (
                f"Dear {user.first_name},\n\n"
                f"Your account has been removed from flight {startlocationname} to {endlocationname}.\n\n"
                f"Reason: {reason_for_removal}\n"
                f"Details: {further_removal_description if further_removal_description else 'No additional details provided.'}\n\n"
                f"This action was taken by {request.user.first_name}.\n\n"
                f"If you have any concerns, please contact support and open a ticket.\n\n"
                f"Best regards,\nSkySync Support Team"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            messages.success(request, f"Customer {user.first_name} {user.last_name} has been removed successfully.")
            return redirect('view_booking_customers', booking_id)
    else:
        form = remove_customer_form()
    return render(request, 'booking_management_system/remove_customer_from_booking.html', {'form': form})



def submit_a_ticket(request):
    if request.method == "POST":
        form = create_a_ticket_form(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            current_user = request.user
            ticket.userCreatorID = current_user
            ticket_reason = form.cleaned_data['ticket_reason']
            ticket_title = form.cleaned_data['ticket_title']
            ticket_description = form.cleaned_data['ticket_description']
            ticket = Ticket.objects.create(
                userCreatorID=current_user,
                ticket_reason=ticket_reason,
                ticket_title=ticket_title,
                ticket_description=ticket_description
            )

            messages.success(request, "You have successfully submitted the ticket")
            return redirect('home')
    else:
        form = create_a_ticket_form()
    return render(request, "Ticket System/create_a_ticket.html", {'form': form})

@user_passes_test(lambda u: u.is_staff)
def view_tickets(request):
    all_tickets = Ticket.objects.all()
    form = Tickets_filter_form(request.GET or None)

    if form.is_valid():
        if form.cleaned_data.get("filter_completed"):
            all_tickets = all_tickets.filter(successfully_fixed=form.cleaned_data["filter_completed"])

        if form.cleaned_data.get("reason"):
            all_tickets = all_tickets.filter(ticket_reason=form.cleaned_data["reason"])

    return render(request, 'Ticket System/view_tickets.html', {'all_tickets': all_tickets, 'form': form})

@user_passes_test(lambda u: u.is_staff)
@require_POST
def mark_ticket_as_fixed(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.successfully_fixed = True
    ticket.save()
    ticket_customer = ticket.userCreatorID
    ticket_customer_email = ticket_customer.email
    ticket_title = ticket.ticket_title
    ticket_reason = ticket.ticket_reason
    ticket_description = ticket.ticket_description

    message = (
        f"Dear {ticket_customer.first_name}, \n\n"
        f"Your ticket, titled {ticket_title} has been marked completed by an admin \n\n"
        f"If your issue still persists, please submit another ticket letting the admins know that the bug is still prevalent \n\n"
        f"The details of your ticket are below - please reference this one in your next ticket if you are still having the same issue \n\n"
        f"ID: {ticket.id}\n\n"
        f"TITLE: {ticket_title}\n\n"
        f"REASON: {ticket_reason}\n\n"
        f"DESCRIPTION: {ticket_description}\n\n"
    )

    subject = (f"TICKET COMPLETED | ID:{ticket.id}")
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [ticket_customer_email])
    messages.success(request, f"You have successfully completed ticket: ID {ticket.id} | Title: {ticket_title}")
    return redirect('view_tickets')


def create_ticket_descriptions(request):
    if request.user.groups.filter(name='Airlines').exists():
        airline = request.user.airline
        if request.method == "POST":
            form = airline_ticket_descriptions_form(request.POST, instance=airline)
            if form.is_valid():
                form.save()
                messages.success(request, 'You have successfully saved the ticket descriptions')


        else:
            form = airline_ticket_descriptions_form(instance=airline)
    else:
        messages.success(request, 'You do not have the correct account type to visit this page')
        return redirect('home')

    return render(request, 'profiles/create_ticket_descriptions.html', {'form': form})


def book_flight_seats(request, booking_id):
    if Invoice.objects.filter(bookingID=booking_id, customerID=request.user.customer.id).exists():
        messages.success(request,
                         "You have already booked this flight! To check the flights that you have booked, check your profile page.")
        return redirect('view_bookings')

    if not request.user.groups.filter(name="Customers").exists():
        messages.success(request, 'You do not have the correct account type to book a flight.')
        return redirect('home')

    booking = get_object_or_404(Booking, pk=booking_id)

    # Calculate available seats
    available_economy = booking.plane_id.economy_seats - booking.economy_booked
    available_economy_plus = booking.plane_id.economy_plus_seats - booking.economy_plus_booked
    available_business = booking.plane_id.business_seats - booking.business_booked
    available_first_class = booking.plane_id.first_class_seats - booking.first_class_booked

    if request.method == "POST":
        form = book_flights_form(request.POST)
        if form.is_valid():
            customerID = get_object_or_404(Customer, user=request.user)
            economy_seats_booked = form.cleaned_data['economy_seats_booked']
            economy_plus_seats_booked = form.cleaned_data['economy_plus_seats_booked']
            business_seats_booked = form.cleaned_data['business_seats_booked']
            first_class_seats_booked = form.cleaned_data['first_class_seats_booked']

            # Ensure there are enough available seats
            if (economy_seats_booked > available_economy or
                    economy_plus_seats_booked > available_economy_plus or
                    business_seats_booked > available_business or
                    first_class_seats_booked > available_first_class):
                messages.error(request, "Not enough seats available in the selected class.")
                return redirect('book_flight_seats', booking_id=booking_id)

            # Create the invoice
            Invoice.objects.create(
                bookingID=booking,
                customerID=customerID,
                date_of_creation=now(),
                economy_seats_booked=economy_seats_booked,
                economy_plus_seats_booked=economy_plus_seats_booked,
                business_seats_booked=business_seats_booked,
                first_class_seats_booked=first_class_seats_booked,
            )

            # Update seat counts in the booking
            booking.economy_booked += economy_seats_booked
            booking.economy_plus_booked += economy_plus_seats_booked
            booking.business_booked += business_seats_booked
            booking.first_class_booked += first_class_seats_booked
            booking.save()

            # Update customer's total bookings
            customerID.amount_of_bookings += 1
            customerID.save()

            messages.success(request, 'You have successfully booked this flight!')
            return redirect('user_profile', request.user.id)

    else:
        form = book_flights_form()

    return render(request, 'booking_system/book_flight_and_seats.html', {
        'form': form,
        'booking': booking,
        'available_economy': available_economy,
        'available_economy_plus': available_economy_plus,
        'available_business': available_business,
        'available_first_class': available_first_class,
    })


def view_current_invoices(request, user_id):
    if not request.user.groups.filter(name="Customers").exists():
        messages.success(request,
                         "You do not have the correct account type to access this page. If this is a mistake, please contact an admin")
        return redirect('home')

    all_user_invoices = Invoice.objects.filter(customerID=request.user.customer)
    form = Invoice_filter_form(request.GET or None)

    if form.is_valid():
        if form.cleaned_data.get("filter_paid"):
            all_user_invoices = all_user_invoices.filter(has_paid=not (form.cleaned_data["filter_paid"]))

        if form.cleaned_data.get("filter_outstanding_bookings"):
            if form.cleaned_data["filter_outstanding_bookings"]:
                new_invoices = []
                for invoice in all_user_invoices:
                    if invoice.bookingID.booking_date >= now():
                        new_invoices.append(invoice)
                all_user_invoices = new_invoices

    return render(request, 'booking_system/view_invoices.html', {'form': form, 'all_user_invoices': all_user_invoices})


def delete_booking(request, booking_id):
    current_user = request.user
    related_booking = Booking.objects.filter(bookingID=booking_id, userCreatorID=current_user.airline.id)
    if not request.user.groups.filter(name="Airlines").exists():
        messages.error(request, "You do not have access to this page!")
        return redirect('home')

    if related_booking.exists():
        related_booking.delete()
        messages.success(request, f"The booking with ID: {booking_id} has been succesfully deleted!")
        return redirect('view_your_bookings')
    else:
        messages.error(request, f"No Bookings found with ID: {booking_id}, if this is in error please contact an admin")

@login_required
@require_POST
def set_customer_as_paid(request, booking_id, user_id):
    # Ownership validation
    booking = get_object_or_404(Booking, bookingID=booking_id)
    current_user = request.user
    if not current_user.groups.filter(name="Airlines").exists():
        messages.error(request, "You do not have access to this page!")
        return redirect('home')
    
    airline = Airline.objects.get(user=current_user)
    if booking.userCreatorID.id != airline.id:
        messages.success(request, 'You are not allowed to edit this booking as you are not the creator')
        return redirect('home')
    customer = get_object_or_404(Customer, user_id=user_id)
    related_invoice = get_object_or_404(Invoice, customerID=customer, bookingID=booking_id)
    related_invoice.has_paid = True
    related_invoice.save()

    messages.success(request, f"You have successfully set customer ID: {user_id} to TRUE paid status")
    return redirect('view_booking_customers', booking_id)
