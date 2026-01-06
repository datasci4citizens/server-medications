from django.db import models

# Create your models here.

class Medication(models.Model):
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    time_of_day = models.CharField(max_length=50)
    time = models.TimeField()
    # add the option to put more than one time of day
    # add option to put the day of the week

    def __str__(self):
        return self.name
    