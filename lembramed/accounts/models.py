from django.db import models
import uuid
from django.contrib.auth.hashers import make_password, check_password

class New_Person(models.Model):
    # Use the default auto-created primary key `id` (already present in DB).
    # Provide a `person_id` property to preserve existing code that expects
    # `person.person_id` without changing the database schema.

    # user = models.OneToOneField(
    #     User,
    #     null = False,
    #     blank = False,
    #     on_delete=models.CASCADE
    # )
    person_id = models.UUIDField(
        default = uuid.uuid4,
        editable = False,
        primary_key=True,
        #unique=True
    )
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth = models.DateField(blank=True, null=True) # YYYY-MM-DD
    email = models.EmailField(max_length=254) # data from app_person
    password = models.CharField(max_length=255) # data from app_person
    #gender 
    #race
    #location
    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    @property
    def person_id(self):
        return self.id

    def __str__(self):
        return self.email #self.str(person_id)