from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import Person
from medication.models.medication_model import Medication
from medication.models.take_model import Take


class TakeSecurityTests(APITestCase):

    def setUp(self):
        # Cria dois usuários. O signal de Person cria seus perfis automaticamente.
        self.user1 = User.objects.create_user(
            username="paciente1",
            email="paciente1@example.com",
            password="SenhaSegura123!"
        )

        self.user2 = User.objects.create_user(
            username="paciente2",
            email="paciente2@example.com",
            password="SenhaSegura123!"
        )

        self.person1 = Person.objects.get(user=self.user1)
        self.person2 = Person.objects.get(user=self.user2)

        # Medicamento utilizado nos testes.
        self.medication = Medication.objects.create(
            medication_id=12345,
            process_num=12345678901234567
        )

        self.take1 = Take.objects.create(
            person_id=self.person1,
            medication_id=self.medication,
            priority=1
        )

        self.take2 = Take.objects.create(
            person_id=self.person2,
            medication_id=self.medication,
            priority=1
        )

        self.list_url = reverse("take-list")

    def test_paciente_lista_apenas_proprias_tomadas(self):
        """Um paciente não deve visualizar tomadas de outros pacientes."""
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [
            item["taken_id"] for item in response.data
        ]

        self.assertIn(self.take1.taken_id, returned_ids)
        self.assertNotIn(self.take2.taken_id, returned_ids)

    def test_paciente_nao_acessa_tomada_de_outro_paciente(self):
        """Um paciente não deve consultar uma tomada pertencente a outro."""
        self.client.force_authenticate(user=self.user1)

        url = reverse(
            "take-detail",
            kwargs={"pk": self.take2.taken_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_paciente_nao_exclui_tomada_de_outro_paciente(self):
        """Um paciente não deve excluir uma tomada de outro paciente."""
        self.client.force_authenticate(user=self.user1)

        url = reverse(
            "take-detail",
            kwargs={"pk": self.take2.taken_id}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            Take.objects.filter(pk=self.take2.taken_id).exists()
        )

    def test_criacao_de_tomada_associa_usuario_autenticado(self):
        """
        Mesmo que o paciente envie o person_id de outra pessoa,
        a tomada deve ser associada ao próprio usuário autenticado.
        """
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            self.list_url,
            {
                "person_id": str(self.person2.person_id),
                "medication_id": self.medication.medication_id,
                "priority": 1
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_take = Take.objects.get(
            taken_id=response.data["taken_id"]
        )

        self.assertEqual(
            created_take.person_id,
            self.person1
        )

        self.assertNotEqual(
            created_take.person_id,
            self.person2
        )

    def test_usuario_nao_autenticado_nao_acessa_tomadas(self):
        """Usuários não autenticados não devem acessar as tomadas."""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_url)

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN
            ]
        )
