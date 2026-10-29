import calendar
import json
import re
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from medication.models import (
    Active_Ingredient,
    AnvisaRegister,
    Brand,
    Category,
    Company,
    DosageIngredients,
    Formato,
    Leaflet,
    Medication,
    Medication_Name,
    Presentation,
    Therapeutic_Class,
)


FORMATO_RULES = (
    ("adesivo transdermico", re.compile(r"\bADES\s+TRANSD\b")),
    ("injetavel", re.compile(r"\b(?:SOL|SUS)\s+INJ\b")),
    ("inalatorio", re.compile(r"\b(?:P[ÓO]\s+)?INAL\b")),
    ("colirio", re.compile(r"\b(?:COL[ÍI]RIO|SOL\s+OFT)\b")),
    ("supositorio", re.compile(r"\bSUP(?:\s+RET)?\b")),
    ("capsula", re.compile(r"\bCAP\b")),
    ("comprimido", re.compile(r"\bCOM\b")),
    ("pomada", re.compile(r"\b(?:POM|UNG|CREM|GEL)\b")),
    ("liquido", re.compile(r"\b(?:XPE|SOL|SUS)\b")),
    ("granulado", re.compile(r"\bGRAN\b")),
)

LEAFLET_FIELDS = (
    "indicacoes_para_uso",
    "funcionamento_medicamento",
    "quando_nao_usar",
    "conhecimento_previo_necessario",
    "como_usar_medicamento",
    "esqueceu_medicamento",
    "efeitos_colaterais",
    "quantidade_a_mais",
    "como_guardar_medicamento",
)


class Command(BaseCommand):
    help = "Load valid ANVISA medications, leaflets, presentations, and dosage ingredients."

    @property
    def data_directory(self):
        project_root = Path(__file__).resolve().parents[4]
        return project_root / "lembramed" / "api" / "src" / "anvisa_data"

    @staticmethod
    def clean_text(value):
        if value is None:
            return ""
        return str(value).replace("\x00", "").strip()

    def load_json(self, filename):
        with (self.data_directory / filename).open(encoding="utf-8") as source:
            return json.load(source)

    @staticmethod
    def parse_expiration_month(value):
        try:
            month, year = map(int, str(value).strip().split("/"))
            return date(year, month, calendar.monthrange(year, month)[1])
        except (TypeError, ValueError):
            return None

    @staticmethod
    def extract_formato(dosage):
        normalized = re.sub(r"\s+", " ", (dosage or "").upper()).strip()

        for formato, pattern in FORMATO_RULES:
            if pattern.search(normalized):
                return formato

        return None

    def parse_leaflets(self, raw_leaflets):
        leaflets = {}

        for raw_medication_id, sections in raw_leaflets.items():
            try:
                medication_id = int(raw_medication_id)
            except (TypeError, ValueError):
                continue

            fields = dict.fromkeys(LEAFLET_FIELDS, "")
            for section in sections or []:
                title = self.clean_text(section.get("titulo")).upper()
                content = self.clean_text(section.get("conteudo"))
                if not content:
                    continue

                if title.startswith("PARA QUE ESTE MEDICAMENTO"):
                    fields["indicacoes_para_uso"] = content
                elif title.startswith("COMO ESTE MEDICAMENTO FUNCIONA"):
                    fields["funcionamento_medicamento"] = content
                elif title.startswith("QUANDO NÃO DEVO USAR"):
                    fields["quando_nao_usar"] = content
                elif title.startswith("O QUE DEVO SABER ANTES DE USAR"):
                    fields["conhecimento_previo_necessario"] = content
                elif title.startswith("COMO DEVO USAR"):
                    fields["como_usar_medicamento"] = content
                elif title.startswith("O QUE DEVO FAZER QUANDO EU ME ESQUECER"):
                    fields["esqueceu_medicamento"] = self.remove_repeated_heading(content)
                elif title.startswith("QUAIS OS MALES"):
                    fields["efeitos_colaterais"] = content
                elif title.startswith("O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR"):
                    fields["quantidade_a_mais"] = self.remove_repeated_heading(content)
                elif title.startswith("ONDE COMO E POR QUANTO TEMPO POSSO GUARDAR"):
                    fields["como_guardar_medicamento"] = content

            # O arquivo contém registros sem conteúdo útil. Não criamos uma bula vazia.
            if any(fields.values()):
                leaflets[medication_id] = fields

        return leaflets

    @staticmethod
    def remove_repeated_heading(content):
        prefixes = (
            "DESTE MEDICAMENTO?",
            "INDICADA DESTE MEDICAMENTO?",
            "MEDICAMENTO?",
            "A INDICADA DESTE MEDICAMENTO?",
        )
        if content.upper().startswith(prefixes):
            return content.partition("?")[2].strip()
        return content

    def get_reference(self, model, field, value):
        value = self.clean_text(value)
        if not value:
            return None
        reference, _ = model.objects.get_or_create(**{field: value})
        return reference

    def load_medications(self, medications, leaflets):
        created_medications = updated_medications = 0
        created_leaflets = updated_leaflets = missing_leaflets = 0

        for medication_id, info in medications.items():
            with transaction.atomic():
                medication, created = Medication.objects.update_or_create(
                    medication_id=medication_id,
                    defaults={"process_num": int(info["process_num"])},
                )
                created_medications += created
                updated_medications += not created

                medication.therapeutic_class = self.get_reference(
                    Therapeutic_Class,
                    "therapeutic_class",
                    info["therapeutic_class"],
                )
                medication.company = self.get_reference(Company, "company", info["company"])
                medication.category = self.get_reference(Category, "category", info["category"])

                if info["category"] == "GENÉRICO":
                    medication.name = self.get_reference(
                        Medication_Name,
                        "name",
                        info["name"],
                    )
                    medication.brand = None
                else:
                    medication.brand = self.get_reference(Brand, "brand", info["name"])
                    medication.name = None

                medication.save()

                active_ingredients = []
                for active_ingredient in info["active_ingredients"].split(" + "):
                    ingredient = self.get_reference(
                        Active_Ingredient,
                        "active_ingredient",
                        active_ingredient,
                    )
                    if ingredient:
                        active_ingredients.append(ingredient)
                medication.active_ingredients.set(active_ingredients)

                leaflet_fields = leaflets.get(medication_id)
                if leaflet_fields is None:
                    missing_leaflets += 1
                    continue

                _, created = Leaflet.objects.update_or_create(
                    medication=medication,
                    defaults=leaflet_fields,
                )
                created_leaflets += created
                updated_leaflets += not created

        self.stdout.write(
            self.style.SUCCESS(
                "Medications: "
                f"{created_medications} created, {updated_medications} updated.\n"
                "Leaflets: "
                f"{created_leaflets} created, {updated_leaflets} updated, "
                f"{missing_leaflets} without useful content."
            )
        )

    def sync_dosage_ingredients(self, presentation, concentration_order):
        desired_rows = set()

        for order, active_ingredient in enumerate(concentration_order or [], start=1):
            ingredient = self.get_reference(
                Active_Ingredient,
                "active_ingredient",
                active_ingredient,
            )
            if ingredient is None:
                continue

            # `order` faz parte da identidade: um mesmo princípio ativo pode aparecer
            # mais de uma vez em uma apresentação, em concentrações diferentes.
            DosageIngredients.objects.update_or_create(
                presentation=presentation,
                active_ingredient=ingredient,
                order=order,
            )
            desired_rows.add((ingredient.pk, order))

        # Mantém a relação idempotente quando o arquivo-fonte remover ou alterar um item.
        for dosage_ingredient in DosageIngredients.objects.filter(presentation=presentation):
            if (dosage_ingredient.active_ingredient_id, dosage_ingredient.order) not in desired_rows:
                dosage_ingredient.delete()

    def load_presentations(self, medications, raw_presentations):
        created_presentations = updated_presentations = 0
        skipped_presentations = skipped_registers = 0

        for process_num, source_register in raw_presentations.items():
            raw_registration_num = source_register.get("regulation_num")
            try:
                registration_num = int(raw_registration_num)
            except (TypeError, ValueError):
                skipped_registers += 1
                continue

            medication = medications.get(registration_num)
            if medication is None or medication["process_num"] != str(process_num):
                # presentations.json também contém produtos que não estão válidos no
                # arquivo ANVISA usado para carregar Medication.
                skipped_registers += 1
                continue

            expiration_date = self.parse_expiration_month(source_register.get("expiration_date"))
            if expiration_date is None:
                skipped_registers += 1
                continue

            valid_presentations = []
            for regulation_num, data in source_register.get("presentations", {}).items():
                try:
                    valid_presentations.append((int(regulation_num), data))
                except (TypeError, ValueError):
                    skipped_presentations += 1

            if not valid_presentations:
                continue

            with transaction.atomic():
                register, _ = AnvisaRegister.objects.update_or_create(
                    register_num=registration_num,
                    defaults={
                        "process_num": int(process_num),
                        "expiration_date": expiration_date,
                    },
                )

                for regulation_num, presentation_data in valid_presentations:
                    dosage = self.clean_text(presentation_data.get("dosage"))
                    formato, _ = Formato.objects.get_or_create(
                        formato=self.extract_formato(dosage),
                    )
                    presentation, created = Presentation.objects.update_or_create(
                        regulation_num=regulation_num,
                        defaults={
                            "register": register,
                            "formato": formato,
                            "dosage": dosage,
                            "embalagem": presentation_data.get("embalagem") or {},
                            "administration": self.clean_text(presentation_data.get("administration")),
                            "conservation": self.clean_text(presentation_data.get("conservation")),
                            "prescription_restriction": self.clean_text(
                                presentation_data.get("prescription_restriction"),
                            ),
                            "usage_restriction": self.clean_text(
                                presentation_data.get("usage_restriction"),
                            ),
                            "label": self.clean_text(presentation_data.get("label")),
                            "can_be_fractioned": bool(
                                presentation_data.get("can_be_fractioned"),
                            ),
                        },
                    )
                    created_presentations += created
                    updated_presentations += not created
                    self.sync_dosage_ingredients(
                        presentation,
                        presentation_data.get("concentration_order"),
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "Presentations: "
                f"{created_presentations} created, {updated_presentations} updated, "
                f"{skipped_presentations} skipped.\n"
                f"Registers skipped: {skipped_registers}."
            )
        )

    def handle(self, *args, **options):
        raw_anvisa = self.load_json("anvisa_data.json")
        medications = {}

        for row in raw_anvisa.get("data", []):
            if row[0] != "MEDICAMENTO" or row[9] != "VÁLIDO":
                continue

            try:
                medication_id = int(row[4])
                process_num = str(int(row[6]))
            except (TypeError, ValueError):
                continue

            medications[medication_id] = {
                "name": self.clean_text(row[1]),
                "process_num": process_num,
                "company": self.clean_text(row[8]).split(" - ", 1)[-1],
                "active_ingredients": self.clean_text(row[10]),
                "therapeutic_class": self.clean_text(row[7]),
                "category": self.clean_text(row[3]),
            }

        leaflets = self.parse_leaflets(self.load_json("leaflets.json"))
        self.stdout.write(
            f"Valid medications: {len(medications)}. "
            f"Leaflets with useful content: {len(leaflets)}."
        )

        self.load_medications(medications, leaflets)
        self.load_presentations(medications, self.load_json("presentations.json"))
