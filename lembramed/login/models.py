from django.db import models
from django.contrib.auth.hashers import make_password

class App_Person(models.Model):
    person_id = models.OneToOneField( # mesmo id do person_id do django app account New_Person
        'accounts.new_person',
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='app_person_id'
    )
    email = models.OneToOneField(
        'accounts.new_person',
        on_delete=models.CASCADE,
        related_name='app_person_email'
    )
    password = models.OneToOneField(
        'accounts.new_person',
        on_delete=models.CASCADE,
        related_name='app_person_password'
    )
    def save(self):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save()
    def __str__(self):
        return self.email