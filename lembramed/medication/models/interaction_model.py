from django.db import models
from .medication_model import Active_Ingredient
from .time_stamped_model import TimeStampedModel

class ingredient_Interaction(TimeStampedModel):
    active_ingredient1 = models.ForeignKey(
        Active_Ingredient,
        on_delete = models.CASCADE,
        related_name = 'ingredient1'
    )
    active_ingredient2 = models.ForeignKey(
        Active_Ingredient,
        on_delete = models.CASCADE,
        related_name = 'ingredient2'
    )
    # Major, Moderate, Minor, Unknown
    severity = models.CharField(max_length=10)
    description = models.TextField()

    def __str__(self):
        return self.severity
