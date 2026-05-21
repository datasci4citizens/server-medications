from django.db import models
from .time_stamped_model import TimeStampedModel

class Medication_Name(TimeStampedModel):
    # medication = models.ForeignKey(
    #     Medication,
    #     on_delete = models.CASCADE,
    #     related_name = 'name',
    # )
    name = models.TextField()

    def __str__(self):
        return self.name

class Active_Ingredient(TimeStampedModel):
    # medication = models.ForeignKey(
    #     Medication,
    #     on_delete = models.CASCADE,
    #     related_name = 'ingredient',
    # )
    active_ingredient = models.TextField()

    def __str__(self):
        return self.active_ingredient

class Therapeutic_Class(TimeStampedModel):
    # medication = models.ForeignKey(
    #     Medication,
    #     on_delete = models.CASCADE,
    #     related_name = 'therapeutic_class',
    # )
    therapeutic_class = models.TextField()

    def __str__(self):
        return self.therapeutic_class

class Category(TimeStampedModel):
    # medication = models.ForeignKey(
    #     Medication,
    #     on_delete = models.CASCADE,
    #     related_name = 'category',
    # )
    category = models.TextField()

    def __str__(self):
        return self.category

class Brand(TimeStampedModel):
    # medication = models.ForeignKey(
    #     Medication,
    #     on_delete = models.CASCADE,
    #     related_name = 'brand',
    # )
    brand = models.TextField()

    def __str__(self):
        return self.brand
    
class Dosage(TimeStampedModel):
    # medication = models.ForeignKey(
    #     Medication,
    #     on_delete = models.CASCADE,
    #     related_name = 'dosage',
    # )
    dosage = models.CharField(null=True)

    def __str__(self):
        return self.dosage

class Company(TimeStampedModel):
    # medication = models.ForeignKey(
    #     Medication,
    #     on_delete = models.CASCADE,
    #     related_name = 'company',
    # )
    company = models.TextField()

    def __str__(self):
        return self.company

class Formato(TimeStampedModel):
    # medication = models.ForeignKey(
    #     Medication,
    #     on_delete = models.CASCADE,
    #     related_name = 'formato',
    # )
    formato = models.CharField(null=True) # type

    def __str__(self):
        return self.formato

class Medication(TimeStampedModel):
    medication_id = models.IntegerField(primary_key = True)
    process_num = models.BigIntegerField() # len == 17

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='medications')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, related_name='medications')

    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name='medications')
    name = models.ForeignKey(Medication_Name, on_delete=models.SET_NULL, null=True, related_name='medications')

    therapeutic_class = models.ForeignKey(Therapeutic_Class, on_delete=models.SET_NULL, null=True, related_name='medications')
    active_ingredients = models.ManyToManyField(Active_Ingredient, related_name='medications', blank=True)

    dosage = models.ForeignKey(Dosage, on_delete=models.SET_NULL, null=True, related_name='medications')
    formato = models.ForeignKey(Formato, on_delete=models.SET_NULL, null=True, related_name='medications')

    def __str__(self):
        return str(self.medication_id)