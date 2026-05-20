from django.db import models
from .time_stamped_model import TimeStampedModel

class Medication(TimeStampedModel):
    medication_id = models.IntegerField(primary_key = True)
    process_num = models.BigIntegerField() # len == 17

    def __str__(self):
        return str(self.medication_id)

class Medication_Name(TimeStampedModel):
    medication = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'name',
    )
    name = models.TextField()

    def __str__(self):
        return self.name

class Active_Ingredient(TimeStampedModel):
    medication = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'ingredient',
    )
    active_ingredient = models.TextField()

    def __str__(self):
        return self.active_ingredient

class Therapeutic_Class(TimeStampedModel):
    medication = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'therapeutic_class',
    )
    therapeutic_class = models.TextField()

    def __str__(self):
        return self.therapeutic_class

class Category(TimeStampedModel):
    medication = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'category',
    )
    category = models.TextField()

    def __str__(self):
        return self.category

class Brand(TimeStampedModel):
    medication = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'brand',
    )
    brand = models.TextField()

    def __str__(self):
        return self.brand
    
class Dosage(TimeStampedModel):
    medication = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'dosage',
    )
    dosage = models.CharField(null=True)

    def __str__(self):
        return self.dosage

class Company(TimeStampedModel):
    medication = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'company',
    )
    company = models.TextField()

    def __str__(self):
        return self.company

class Formato(TimeStampedModel):
    medication = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'formato',
    )
    formato = models.CharField(null=True) # type

    def __str__(self):
        return self.formato
