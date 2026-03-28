from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.auth.hashers import make_password
from django.dispatch import receiver
import uuid

class Person(models.Model):
    user = models.OneToOneField(
        User,
        null = False,
        blank = False,
        on_delete=models.CASCADE,
        related_name="person"
    )
    person_id = models.UUIDField(
        default = uuid.uuid4,
        editable = False,
        primary_key=True,
        unique=True
    )

    birth = models.DateField(blank=True, null=True) # YYYY-MM-DD
    google_id = models.CharField(max_length=100, blank=True, null=True)
    # profile_picture = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.email
    
@receiver(post_save, sender=User)
def create_or_update_person(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(user=instance)
    else:
        instance.person.save()
