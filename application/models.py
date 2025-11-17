from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
# Create your models here.
class UserProfile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    age = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='assets_img/', blank=True)

    def __str__(self):
        return self.id_number

def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = UserProfile(user=instance)
        user_profile.save()

post_save.connect(create_profile, sender=User)