
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),

    path('submit_a_ticket', views.submit_a_ticket, name="submit_a_ticket"),
    path('view_tickets', views.view_tickets, name="view_tickets"),
    path('tickets/mark_ticket_fixed/<int:ticket_id>/', views.mark_ticket_as_fixed, name='mark_ticket_as_fixed'),


    path('booking/view_bookings', views.view_bookings, name="view_bookings"),
    path('booking/<int:booking_id>/', views.booking_details, name='booking_details'),
    path('booking/<int:booking_id>/book', views.book_flight_seats, name='book_flight_seats'),

    path('booking/bookings_dashboard', views.bookings_dashboard, name="bookings_dashboard"),
    path('booking/create_bookings', views.create_bookings, name="create_bookings"),
    path('booking/create_locations', views.create_locations, name="create_locations"),
    path('booking/create_planes', views.create_planes, name="create_planes"),
    path('booking/see_your_bookings', views.view_your_bookings, name="view_your_bookings"),
    path('booking/edit_booking/<int:booking_id>', views.edit_booking, name="edit_booking"),
    path('booking/view_booking_customers/<int:booking_id>', views.view_booking_customers, name="view_booking_customers"),
    path('booking/delete_booking/<int:booking_id>', views.delete_booking, name="delete_booking"),
    path('booking/remove_customer/<int:booking_id>/<int:user_id>', views.remove_customer, name="remove_customer"),
    path('booking/set_customer_as_paid/<int:booking_id>/<int:user_id>', views.set_customer_as_paid, name="set_customer_as_paid"),

    path('registration-email/', views.registration_email, name='registration_email'),

    path('profile/<int:user_id>/', views.user_profile, name="user_profile"),
    path('profile/create_ticket_descriptions', views.create_ticket_descriptions, name="create_ticket_descriptions"),
    path('profile/edit_user_profile', views.edit_user_profile, name="edit_user_profile"),
    path('profile/<int:user_id>/view_invoices', views.view_current_invoices, name="view_invoices"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

