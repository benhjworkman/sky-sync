from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib import messages
from .forms import RegisterCustomerForm, RegisterAirlineForm
from website.models import Customer, Airline, Profile


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.success(request, ("There was an error logging in! try again..."))
            return redirect('login')
    else:
        return render(request, 'authenticate/login.html', {})

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, ("Logged out successfully"))
    else:
        messages.success(request, ("You are not logged into an account!"))
    return redirect('home')

def register_now(request):
    if request.user.is_authenticated:
        userName = request.user.email
    else:
        userName = None
    return render(request, "authenticate/register_now.html", {'user': userName})

def register_customer(request):
    if request.method == "POST":
        form = RegisterCustomerForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            group = Group.objects.get(name='Customers')
            user.groups.add(group)
            Customer.objects.create(user=user)
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, ("Your registration was successful!"))
            return redirect('registration_email')

    else:
        form = RegisterCustomerForm()

    return render(request, 'authenticate/register_customer.html', {'form': form})


def register_airline(request):
    if request.method == "POST":
        form = RegisterAirlineForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            group = Group.objects.get(name='Airlines')
            user.groups.add(group)
            Airline.objects.create(user=user)
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, ("Your company has been registered successfully!"))
            return redirect('registration_email')
    else:
        form = RegisterCustomerForm()

    return render(request, 'authenticate/register_airline.html', {'form': form})
