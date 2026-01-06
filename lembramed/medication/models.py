from django.db import models

# Create your models here.

class Medication(models.Model):
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    time = models.TimeField() # check how to put the format of time I wanna
    begin = models.DateField()
    end = models.DateField()
    # add the option to put more than one time of day
    # add option to put the day of the week

    def __str__(self):
        return self.name
    