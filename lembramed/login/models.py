from django.db import models
from django.contrib.auth.hashers import make_password

class App_Person(models.Model):
    person_id = models.OneToOneField( # mesmo id do person_id do django app account New_Person
        'accounts.New_Person',
        primary_key=True,
        on_delete=models.CASCADE
    )
    email = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    def save(self):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save()
    def __str__(self):
        return self.email