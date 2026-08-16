from django.db import models
from .time_stamped_model import TimeStampedModel

class Medication_Name(TimeStampedModel):
    name = models.TextField()

    def __str__(self):
        return self.name

class Active_Ingredient(TimeStampedModel):
    active_ingredient = models.TextField()

    def __str__(self):
        return self.active_ingredient

class Therapeutic_Class(TimeStampedModel):
    therapeutic_class = models.TextField()

    def __str__(self):
        return self.therapeutic_class

class Category(TimeStampedModel):
    category = models.TextField()

    def __str__(self):
        return self.category

class Brand(TimeStampedModel):
    brand = models.TextField()

    def __str__(self):
        return self.brand

class Company(TimeStampedModel):
    company = models.TextField()

    def __str__(self):
        return self.company

class Formato(TimeStampedModel):
    formato = models.CharField(max_length=100, null=True, blank=True) # comprimido, capsula, liquido, pomada, injetavel, inalatorio, colirio, supositorio, adesivo transdermico

    def __str__(self):
        return self.formato

class Presentation(TimeStampedModel):
    register_num = models.BigIntegerField(primary_key=True) # == regularion_num + "presentation_id"

    formato = models.OneToOneField(
        Formato,
        on_delete = models.CASCADE,
        related_name = 'presentsation'
    )
    dosage = models.CharField(max_length=100,default="")
    embalagem = models.CharField(max_length=100,default="") # lista de strings (primaria,secundaria...)
    administration = models.CharField(max_length=100,default="") # oral...
    conservation = models.TextField(default="") # Como armazenar soq mais seguro de ter!
    prescription_restriction = models.CharField(max_length=100,default="") # Sob Prescricao Medica...
    usage_restriction = models.CharField(max_length=50,default="") # grupo(adultos...)
    label = models.CharField(max_length=20,default="") # tarja
    can_be_fractioned = models.BooleanField(default=False) # pode partir/macerar o medicamento

    def __str__(self):
        return str(self.register_num)

class Medication(TimeStampedModel):
    medication_id = models.IntegerField(primary_key = True)
    process_num = models.BigIntegerField() # len == 17

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='medications')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, related_name='medications')

    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name='medications')
    name = models.ForeignKey(Medication_Name, on_delete=models.SET_NULL, null=True, related_name='medications')

    therapeutic_class = models.ForeignKey(Therapeutic_Class, on_delete=models.SET_NULL, null=True, related_name='medications')
    active_ingredients = models.ManyToManyField(Active_Ingredient, related_name='medications', blank=True)

    presentation = models.ManyToManyField(Presentation, related_name='medications', blank=True)

    def __str__(self):
        return str(self.medication_id)