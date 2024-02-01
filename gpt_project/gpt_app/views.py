from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
import csv
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def home(request):
    return render(request, 'home.html')

def logout(request):
    return render(request, 'logout.html')

def chatbot(request):
    return render(request, 'chatbot.html')

def logout_template_view(request):
    return LogoutView.as_view(template_name='logout.html')(request)

@staff_member_required
def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        if not csv_file.name.lower().endswith('.csv'):
            return render(request, 'upload_csv.html', {'error_message': 'Only CSV files are supported.'})

        # Process the CSV file and create users
        reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
        for row in reader:
            username = row['username']
            email = row['email']
            password = row['password']
            is_staff = row.get('is_staff', 'False').lower() == 'true'

            User.objects.create_user(username=username, email=email, password=password, is_staff=is_staff)

        return render(request, 'upload_csv.html', {'success_message': 'Users created successfully.'})

    return render(request, 'upload_csv.html')