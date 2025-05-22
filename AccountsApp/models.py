from django.db import models
from django.db.models.signals import post_save
from ProductsApp.models import Products
from django.contrib.auth.models import User
from django.dispatch import receiver
from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.ENCRYPTION_KEY)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    new_token = models.CharField(max_length=50, default='', blank=True)
    ex_date = models.DateTimeField(null=True, blank=True)
    user_type = models.CharField(
        max_length=10,
        choices=[('customer', 'customer'), ('vendor', 'vendor')],
        default='customer'
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_code = models.CharField(max_length=6, blank=True, null=True)

    def set_two_factor_code(self, code):
        self.two_factor_code = fernet.encrypt(code.encode()).decode()
        self.save()

    def verify_two_factor_code(self, code):
        try:
            decrypted_code = fernet.decrypt(self.two_factor_code.encode()).decode()
            return decrypted_code == code
        except Exception:
            return False

    def __str__(self):
        return f"Profile of {self.user.username}"


# Create profile automatic when user craeted 
@receiver(post_save, sender=User)
def auto_add_profile(sender, instance, created, **kwargs):
    user = instance
    if created:
        profile = Profile(user = instance)
        profile.save()

