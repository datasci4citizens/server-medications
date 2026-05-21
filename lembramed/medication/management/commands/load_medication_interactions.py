import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from medication.models import Active_Ingredient, ingredient_Interaction


class Command(BaseCommand):
    help = "Carrega interações de medicamentos do Interactions.json"
    
    def handle(self, *args, **options):
        BASE = "/server-medications/lembramed/api/src/lembramed_data"

        self.stdout.write("Carregando Interactions.json...")

        with open(os.path.join(BASE, "Interactions.json"), "r") as f:
            json_data = json.load(f)
        
        created = 0
        skipped = 0
        
        for element in json_data.get("data", []):
            ing1_name = element[0]
            ing2_name = element[1]
            severity  = element[2]
            desc      = element[3]

            ing1 = Active_Ingredient.objects.filter(active_ingredient__iexact=ing1_name).first()
            ing2 = Active_Ingredient.objects.filter(active_ingredient__iexact=ing2_name).first()

            if not ing1 or not ing2:
                self.stdout.write(f"  Pulando: '{ing1_name}' ou '{ing2_name}' não encontrado no banco.")
                skipped += 1
                continue
            
            _, was_created = ingredient_Interaction.objects.get_or_create(
                active_ingredient1=ing1,
                active_ingredient2=ing2,
                defaults={"severity": severity, "description": desc},
            )
            
            if was_created:
                creates += 1
            
            else:
                skipped += 1
            
        self.stdout.write(self.style.SUCCESS(
            f"Concluído: {created} criadas, {skipped} ignoradas."
        ))



