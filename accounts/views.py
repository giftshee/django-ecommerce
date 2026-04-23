from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

# LOGIN
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accounts:account')  # Go to account dashboard after login
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# REGISTER
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')  # After registration, go to login
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('accounts:login')  # Redirect to login page

# ACCOUNT DASHBOARD
@login_required(login_url='accounts:login')
def account_view(request):
    return render(request, 'accounts/account.html')
