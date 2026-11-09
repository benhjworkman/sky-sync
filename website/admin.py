from django.contrib import admin
from .models import Customer, Airline, Booking, Invoice, Location, Plane, Profile, Ticket

admin.site.register(Customer)
admin.site.register(Airline)
admin.site.register(Location)
admin.site.register(Plane)
admin.site.register(Booking)
admin.site.register(Invoice)
admin.site.register(Profile)
admin.site.register(Ticket)

