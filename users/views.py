from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from .models import User, UserProfile
from .forms import (
    UserRegistrationForm, UserLoginForm, UserEditForm, UserProfileEditForm,
    EmailPasswordResetForm, NewPasswordForm
)

# Django's built-in password reset views
from django.contrib.auth import views as auth_views

# --- Helper function to send activation email ---
def send_activation_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your Crowdfunding account'
    # It's good practice to create an HTML template for the email body
    message = render_to_string('users/email/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': user.activation_token,
    })
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = "html"
    try:
        email.send()
    except Exception as e:
        # Log the error e
        print(f"Email sending error: {str(e)}")  # Add this line to print the error
        messages.error(request, f"Error sending activation email: {str(e)}")
        return False
    return True

# --- Registration View ---
def register_view(request):
    if request.user.is_authenticated:
        return redirect('projects:home') # Or wherever your home page is

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # User is not active until email confirmation
            user.set_activation_token() # Generate token and expiry
            user.save()
            
            if send_activation_email(request, user):
                messages.success(request, 'Registration successful! Please check your email to activate your account.')
                return redirect('users:login') # Redirect to login or a specific "check email" page
            else:
                # If email sending failed, perhaps delete the user or mark for retry
                # For now, we'll let the user try to log in and resend activation if needed
                messages.warning(request, 'Registration successful, but we could not send the activation email. Please try logging in to resend.')
                return redirect('users:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form, 'title': 'Register'})

# --- Account Activation View ---
def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and str(user.activation_token) == token:
        if user.is_activation_token_valid():
            user.is_active = True
            user.activation_token = None # Clear the token after use
            user.activation_token_expires_at = None
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend') # Log the user in
            messages.success(request, 'Your account has been activated successfully! You are now logged in.')
            return redirect('projects:home') # Or user's profile page
        else:
            messages.error(request, 'Activation link has expired. Please try to register again or request a new one.')
            # Optionally, provide a way to resend activation link
            return redirect('users:register') # Or a specific page for expired links
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('users:register') # Or home page

# --- Login View ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('projects:home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username') # AuthenticationForm uses 'username'
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    # Redirect to a success page or intended page
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('projects:home') # Or user's profile page
                else:
                    messages.error(request, 'Your account is not active. Please check your email for the activation link or contact support.')
                    # Optionally, add a way to resend activation link here
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.') # Or more specific form errors
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form, 'title': 'Login'})

# --- Logout View ---
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('users:login')

# --- Profile View ---
@login_required
def profile_view(request):
    user = request.user
    # Later, you'll fetch user's projects and donations here
    # projects = Project.objects.filter(creator=user)
    # donations = Donation.objects.filter(user=user)
    context = {
        'user_profile': user.profile, # Access UserProfile via related_name 'profile'
        'title': 'My Profile'
        # 'projects': projects,
        # 'donations': donations,
    }
    return render(request, 'users/profile_view.html', context)

# --- Profile Edit View ---
@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, request.FILES, instance=request.user)
        profile_form = UserProfileEditForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile_view')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileEditForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Edit Profile'
    }
    return render(request, 'users/profile_edit.html', context)

# --- Account Deletion View ---
@login_required
def delete_account_view(request):
    if request.method == 'POST':
        # For bonus: Add password confirmation here
        # if request.user.check_password(request.POST.get('password')):
        #     request.user.delete()
        #     logout(request)
        #     messages.success(request, 'Your account has been successfully deleted.')
        #     return redirect('projects:home') # Or a specific "account deleted" page
        # else:
        #     messages.error(request, 'Incorrect password. Account not deleted.')
        #     return redirect('users:delete_account')

        # Basic deletion without password confirmation for now
        request.user.delete()
        logout(request)
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('projects:home') # Or a specific "account deleted" page

    return render(request, 'users/delete_account_confirm.html', {'title': 'Delete Account'})


# --- Password Reset Views (using Django's built-in views) ---
# We can customize templates and some behavior

class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'users/password/password_reset_form.html'
    email_template_name = 'users/password/password_reset_email.html' # Email body
    subject_template_name = 'users/password/password_reset_subject.txt' # Email subject
    form_class = EmailPasswordResetForm # Our custom form if needed, or Django's default
    success_url = reverse_lazy('users:password_reset_done')

    def form_valid(self, form):
        messages.success(self.request, "We've emailed you instructions for setting your password, "
                                       "if an account exists with the email you entered. You should receive them shortly.")
        return super().form_valid(form)

class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'users/password/password_reset_done.html'
    title = 'Password Reset Sent'

class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'users/password/password_reset_confirm.html'
    form_class = NewPasswordForm # Our custom form for setting new password
    success_url = reverse_lazy('users:password_reset_complete')
    title = 'Enter New Password'

    def form_valid(self, form):
        messages.success(self.request, "Your password has been set. You may go ahead and log in now.")
        return super().form_valid(form)

class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'users/password/password_reset_complete.html'
    title = 'Password Reset Complete'

# Note: For password change when user is logged in, Django provides PasswordChangeView and PasswordChangeDoneView
# We can add them if needed, similar to password reset.
