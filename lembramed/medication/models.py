from django.db import models

# Create your models here.

class Medication(models.Model):
    DAYS_OF_WEEK = [
        ('mon', 'Segunda'),
        ('tue', 'Terça'),
        ('wed', 'Quarta'),
        ('thu', 'Quinta'),
        ('fri', 'Sexta'),
        ('sat', 'Sábado'),
        ('sun', 'Domingo'),
    ]
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    time = models.TimeField() # check how to put the format of time I wanna
    begin = models.DateField() # solve data problem
    end = models.DateField()
    days= models.CharField(max_length=50)
    # add the option to put more than one time of day
    # add option to put the day of the week

    def __str__(self):
        return self.name
    def get_days_display(self):
        day_dict = dict(self.DAYS_OF_WEEK)
        return ', '.join(day_dict[d] for d in self.days.split(',')) 