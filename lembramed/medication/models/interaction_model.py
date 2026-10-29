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
    severity = models.CharField(max_length=10) # Major, Moderate, Minor, Unknown
    description = models.TextField()
    
    def __str__(self):
        return self.severity

    def save(self,*args,**kwargs):
        if self.active_ingredient1_id > self.active_ingredient2_id:
            self.active_ingredient1, self.active_ingredient2 = self.active_ingredient2, self.active_ingredient1
        super().save(*args,**kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["active_ingredient1", "active_ingredient2"],
                name="unique_ingredientinteraction",
            )
        ]
