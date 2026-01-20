from django.db import models

class Person(models.Model):
    person_id = models.CharField(
        max_length=255,
        primary_key=True,
        unique=True
    )
    birth = models.DateField()
    def __str__(self):
        return self.person_id