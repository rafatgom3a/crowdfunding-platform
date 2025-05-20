from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', False) # User is not active until email confirmation
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # Superuser is active by default

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None # We will use email as the unique identifier
    email = models.EmailField(unique=True, help_text='Required. Enter a valid email address.')
    first_name = models.CharField(max_length=30, help_text='Required.')
    last_name = models.CharField(max_length=150, help_text='Required.')
    
    egyptian_phone_regex = RegexValidator(
        regex=r'^01[0-2,5]{1}[0-9]{8}$',
        message="Phone number must be a valid Egyptian number, e.g., 01xxxxxxxxx."
    )
    mobile_phone = models.CharField(
        validators=[egyptian_phone_regex],
        max_length=11,
        unique=True,
        help_text='Required. Enter a valid Egyptian mobile number.'
    )
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    # For email activation
    activation_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    activation_token_expires_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'mobile_phone'] # email and password are required by default

    objects = UserManager()

    def __str__(self):
        return self.email

    def set_activation_token(self):
        self.activation_token = uuid.uuid4()
        self.activation_token_expires_at = timezone.now() + timezone.timedelta(hours=24)
        self.save()

    def is_activation_token_valid(self):
        return self.activation_token_expires_at is not None and self.activation_token_expires_at > timezone.now()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    birth_date = models.DateField(null=True, blank=True)
    facebook_profile = models.URLField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    # projects and donations will be linked here later via ForeignKey or ManyToManyField

    def __str__(self):
        return f"{self.user.email}'s Profile"

# Signal to create UserProfile when a new User is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()
