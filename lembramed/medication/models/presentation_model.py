from django.db import models
from .time_stamped_model import TimeStampedModel
from .medication_model import Medication, Active_Ingredient

class Formato(TimeStampedModel):
    formato = models.CharField(max_length=100, null=True, blank=True, unique=True) # comprimido, capsula, liquido, pomada, injetavel, inalatorio, colirio, supositorio, adesivo transdermico

    def __str__(self):
        return self.formato

class AnvisaRegister(TimeStampedModel):
    register_num = models.IntegerField(primary_key=True) # len = 9

    process_num = models.BigIntegerField() # len == 17, same as Medication one
    expiration_date = models.DateField() # 09/2028

    def __str__(self):
        return str(self.register_num)
    
class Presentation(TimeStampedModel):
    # regulation_num == "register_num" (from AnvisaRegister) + "presentation_id" == 9 + 4
    regulation_num = models.BigIntegerField(primary_key=True)

    register = models.ForeignKey(
        AnvisaRegister,
        on_delete=models.CASCADE,
        related_name="presentation",
    )
    formato = models.ForeignKey(
        Formato,
        on_delete = models.CASCADE,
        related_name = 'presentation'
    )
    dosage = models.TextField(default="")
    embalagem = models.JSONField(default=dict, blank=True) # lista de strings (primaria,secundaria...)
    administration = models.CharField(max_length=100,default="") # oral...
    conservation = models.TextField(default="") # Como armazenar soq mais seguro de ter!
    prescription_restriction = models.CharField(max_length=100,default="") # Sob Prescricao Medica...
    usage_restriction = models.TextField(default="") # grupo(adultos...)
    label = models.CharField(max_length=100,default="") # tarja
    can_be_fractioned = models.BooleanField(default=False) # pode partir/macerar o medicamento

    def __str__(self):
        return str(self.regulation_num)

class DosageIngredients(TimeStampedModel):
    
    presentation = models.ForeignKey(
        Presentation,
        on_delete=models.CASCADE,
        related_name="concentration_order",
    )
    active_ingredient = models.ForeignKey(
        Active_Ingredient,
        on_delete=models.CASCADE,
        related_name="dosage_ingredients"
    )
    order = models.PositiveIntegerField()

    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=["presentation", "active_ingredient", "order"],
            name="unique_dosage_ingredient_per_presentation",
        )
        ]
