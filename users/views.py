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
from django.conf import settings
from decouple import config

from donations.models import Donation
from projects.models import Project
from donations.models import Donation


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

    # Get protocol (http or https)
    protocol = 'https' if request.is_secure() else 'http'

    # Ensure token is a string without hyphens to match our comparison logic
    token_str = str(user.activation_token).replace('-', '')

    # Render the email template with context
    message = render_to_string('users/email/account_activation_email.html', {
        'user': user,
        'domain': config('SITE_URL', default='localhost:8000'),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_str,
        'protocol': protocol,
    })

    to_email = user.email

    # Use Django's send_mail function instead of EmailMessage
    try:
        from django.core.mail import send_mail
        result = send_mail(
            subject=mail_subject,
            message='',  # Empty plain text message
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=message,  # HTML content
            fail_silently=False,
        )
        print(f"Email sent successfully to {to_email}, result: {result}")
        return True
    except ConnectionRefusedError:
        print("Email sending error: Connection refused")
        messages.error(
            request, "Error sending activation email: Connection refused. Please check your email server configuration.")
        return False
    except TimeoutError:
        print("Email sending error: Connection timed out")
        messages.error(
            request, "Error sending activation email: Connection timed out. Please check your email server configuration.")
        return False
    except Exception as e:
        # Log the error for debugging
        print(f"Email sending error: {str(e)}")
        messages.error(request, f"Error sending activation email: {str(e)}")
        return False

# --- Registration View ---


def register_view(request):
    if request.user.is_authenticated:
        return redirect('projects:home')  # Or wherever your home page is

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Don't save the user yet - create the instance but don't commit to database
            user = form.save(commit=False)
            user.is_active = False  # User is not active until email confirmation
            user.set_activation_token()  # Generate token and expiry

            # Try to send the activation email before saving the user
            if send_activation_email(request, user):
                # Only save the user if email was sent successfully
                user.save()
                messages.success(
                    request, 'Registration successful! Please check your email to activate your account.')
                # Redirect to login or a specific "check email" page
                return redirect('users:login')
            else:
                # If email sending failed, don't save the user
                messages.error(
                    request, 'Registration failed: Could not send activation email. Please try again later.')
                # Return to the same page with the form data preserved
                return render(request, 'users/register.html', {'form': form, 'title': 'Register'})
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form, 'title': 'Register'})

# --- Account Activation View ---


def activate_view(request, uidb64, token):
    print(f"Activation attempt with uidb64: {uidb64}, token: {token}")

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(f"Decoded UID: {uid}")
        user = User.objects.get(pk=uid)
        print(
            f"Found user: {user.email}, token from URL: {token}, user token: {user.activation_token}")

        # Check if user is already active
        if user.is_active:
            print(f"User {user.email} is already active")
            messages.info(
                request, 'This account is already active. You can log in now.')
            return redirect('users:login')

    except (TypeError, ValueError, OverflowError) as e:
        print(f"Error decoding UID: {str(e)}")
        messages.error(request, 'Invalid activation link format.')
        return redirect('users:register')
    except User.DoesNotExist as e:
        print(f"User with ID {uid} not found: {str(e)}")
        messages.error(request, 'No user found with this activation link.')
        return redirect('users:register')

    # Check token match - handle both string and UUID comparison
    if user.activation_token is None:
        print(f"User {user.email} has no activation token")
        messages.error(
            request, 'Activation link is invalid! No token found for this user.')
        return redirect('users:register')

    # Convert both to strings for comparison to avoid type issues
    user_token_str = str(user.activation_token).lower().replace('-', '')
    url_token_str = str(token).lower().replace('-', '')

    print(
        f"Comparing tokens: URL token '{url_token_str}' vs user token '{user_token_str}'")

    if user_token_str != url_token_str:
        print(
            f"Token mismatch: URL token '{token}' != user token '{user.activation_token}'")
        messages.error(
            request, 'Activation link is invalid! Token does not match.')
        return redirect('users:register')

    # Check token validity (expiration)
    if not user.is_activation_token_valid():
        print(f"Token expired for user {user.email}")
        messages.error(
            request, 'Activation link has expired. Please request a new one.')
        return redirect('users:resend_activation')

    # If we get here, everything is valid
    user.is_active = True
    user.activation_token = None  # Clear the token after use
    user.activation_token_expires_at = None
    user.save()
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    messages.success(
        request, 'Your account has been activated successfully! You are now logged in.')
    return redirect('projects:home')

# --- Login View ---


def login_view(request):
    if request.user.is_authenticated:
        return redirect('projects:home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            # AuthenticationForm uses 'username'
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(
                        request, f'Welcome back, {user.first_name}!')
                    # Redirect to a success page or intended page
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('projects:home')  # Or user's profile page
                else:
                    # Add a resend activation link option
                    messages.error(
                        request, 'Your account is not active. Please check your email for the activation link.')
                    # Store the inactive user's email in session for resend functionality
                    request.session['inactive_user_email'] = email
                    return redirect('users:resend_activation')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            # Or more specific form errors
            messages.error(request, 'Invalid email or password.')
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
        'user_profile': user.profile,  # Access UserProfile via related_name 'profile'
        'title': 'My Profile'
        # 'projects': projects,
        # 'donations': donations,
    }
    return render(request, 'users/profile_view.html', context)

# --- Profile Edit View ---


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        user_form = UserEditForm(
            request.POST, request.FILES, instance=request.user)
        profile_form = UserProfileEditForm(
            request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(
                request, 'Your profile has been updated successfully!')
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
        messages.success(
            request, 'Your account has been successfully deleted.')
        # Or a specific "account deleted" page
        return redirect('projects:home')

    return render(request, 'users/delete_account_confirm.html', {'title': 'Delete Account'})


# --- Password Reset Views (using Django's built-in views) ---
# We can customize templates and some behavior

class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'users/password/password_reset_form.html'
    email_template_name = 'users/password/password_reset_email.html'
    subject_template_name = 'users/password/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')
    form_class = EmailPasswordResetForm  # Use your custom form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use SITE_URL from settings or config
        context['domain'] = config('SITE_URL', default='localhost:8000')
        # Get protocol (http or https)
        protocol = 'https' if self.request.is_secure() else 'http'
        context['protocol'] = protocol
        return context

    def form_valid(self, form):
        messages.success(self.request, "We've emailed you instructions for setting your password, "
                                    "if an account exists with the email you entered. You should receive them shortly.")
        return super().form_valid(form)


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'users/password/password_reset_done.html'
    title = 'Password Reset Sent'


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'users/password/password_reset_confirm.html'
    form_class = NewPasswordForm  # Our custom form for setting new password
    success_url = reverse_lazy('users:password_reset_complete')
    title = 'Enter New Password'

    def form_valid(self, form):
        messages.success(
            self.request, "Your password has been set. You may go ahead and log in now.")
        return super().form_valid(form)


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'users/password/password_reset_complete.html'
    title = 'Password Reset Complete'

# Note: For password change when user is logged in, Django provides PasswordChangeView and PasswordChangeDoneView
# We can add them if needed, similar to password reset.

# --- Resend Activation Email View ---


def resend_activation_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
            # Generate a new token
            user.set_activation_token()
            user.save()

            if send_activation_email(request, user):
                messages.success(
                    request, 'A new activation email has been sent. Please check your inbox.')
                return redirect('users:login')
            else:
                messages.error(
                    request, 'Failed to send activation email. Please try again later.')
        except User.DoesNotExist:
            messages.error(
                request, 'No inactive account found with this email address.')

    # Get email from session if available
    email = request.session.get('inactive_user_email', '')
    if 'inactive_user_email' in request.session:
        del request.session['inactive_user_email']

    return render(request, 'users/resend_activation.html', {'email': email, 'title': 'Resend Activation Email'})



# --- User Projects and Donations Views ---
@login_required
def user_projects(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, 'users/projects_list.html', {'projects': projects})

# @login_required


def user_donations(request):
    donations = Donation.objects.filter(user=request.user).select_related('project')
    return render(request, 'users/donations_list.html', {'donations': donations})
