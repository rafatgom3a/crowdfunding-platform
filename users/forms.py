from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from .models import User, UserProfile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile_phone', 'profile_picture', 'password']
        help_texts = {
            'email': None, # Remove default help text if not needed or override
            'first_name': None,
            'last_name': None,
            'mobile_phone': None,
        }


    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords don't match")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Email'}
        )
        self.fields['username'].label = "Email" # Change label from Username to Email
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Password'}
        )

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'mobile_phone', 'profile_picture']
        help_texts = {
            'first_name': None,
            'last_name': None,
            'mobile_phone': None,
        }

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        # Email is not editable as per requirements
        if 'email' in self.fields:
            self.fields['email'].disabled = True
            self.fields['email'].required = False


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birth_date', 'facebook_profile', 'country']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}), # Use HTML5 date picker
        }

# Django's built-in forms can be used directly or customized if needed
# For password reset, we can use Django's PasswordResetForm
class EmailPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(EmailPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Enter your email address'}
        )
        
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Override the send_mail method to add logging and fix the domain
        """
        # Override the domain in the context with full URL including protocol
        context['domain'] = 'http://localhost:8000'
        # We don't need separate protocol since it's included in domain now
        if 'protocol' in context:
            del context['protocol']
            
        print(f"Sending password reset email to: {to_email}")
        # Call the parent class's send_mail method with the modified context
        result = super().send_mail(
            subject_template_name, email_template_name, context, from_email,
            to_email, html_email_template_name
        )
        print(f"Password reset email sent successfully to {to_email}, result: {result}")
        return result

# For setting the new password after reset, Django's SetPasswordForm
class NewPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(NewPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'New password'}
        )
        self.fields['new_password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Confirm new password'}
        )