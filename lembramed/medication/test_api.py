from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import Person
from medication.models import Medication, Take
from datetime import date


class TakeAPITest(TestCase):
    """Testes para validar adição, edição e remoção de medicamentos"""
    
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )

        self.medication1 = Medication.objects.create(
            medication_id=1001,
            indicacoes_para_uso="Para dor",
            efeitos_colaterais="Pode causar sonolência"
        )
        
        self.medication2 = Medication.objects.create(
            medication_id=1002,
            indicacoes_para_uso="Para febre",
            efeitos_colaterais="Pode causar alergia"
        )
        
        self.client.force_authenticate(user=self.user)
    
    # Addition
    
    def test_add_medication_success(self):
        """ add medication"""
        data = {
            'medication_id': self.medication1.medication_id,
            'quantity': '30'
        }
        
        response = self.client.post('/api/take/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Take.objects.filter(medication_id=self.medication1).exists())
    
    def test_add_medication_duplicate(self):
        """ prevent the addition of a duplicate medication"""
        Take.objects.create(
            person_id=self.user.person,
            medication_id=self.medication1,
            quantity='30'
        )
        
        data = {
            'medication_id': self.medication1.medication_id,
            'quantity': '30'
        }
        
        response = self.client.post('/api/take/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('já está registrado', str(response.data))
    
    def test_add_nonexistent_medication(self):
        """add a medication that is not in the bank"""
        data = {
            'medication_id': 9999,  # Não existe
            'quantity': '30'
        }
        
        response = self.client.post('/api/take/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('não encontrado', str(response.data))
    
    # edition
    
    def test_edit_medication_success(self):
        """edit a medicaiton"""
        take = Take.objects.create(
            person_id=self.user.person,
            medication_id=self.medication1,
            quantity='30'
        )
        
        data = {
            'quantity': '60'
        }
        
        response = self.client.patch(f'/api/take/{take.taken_id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        take.refresh_from_db()
        self.assertEqual(take.priority, 3)
        self.assertEqual(take.quantity, '60')
    
    def test_edit_medication_of_another_user(self):
        """impede the edition of another user medication"""
        # Criar outro usuário
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@test.com",
            password="testpass123"
        )
        take = Take.objects.create(
            person_id=other_user.person,
            medication_id=self.medication1,
            quantity='30'
        )
        
        data = {'priority': 2}
        response = self.client.patch(f'/api/take/{take.taken_id}/', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    # deletion
    
    def test_delete_medication_success(self):
        """delete a medication"""
        take = Take.objects.create(
            person_id=self.user.person,
            medication_id=self.medication1,
            quantity='30'
        )
        
        response = self.client.delete(f'/api/take/{take.taken_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Take.objects.filter(taken_id=take.taken_id).exists())
    
    def test_delete_medication_of_another_user(self):
        """impede the deletion of another user medicaiton"""
        # Criar outro usuário
        other_user = User.objects.create_user(
            username="otheruser2",
            email="other2@test.com",
            password="testpass123"
        )
     
        take = Take.objects.create(
            person_id=other_user.person,
            medication_id=self.medication1,
            quantity='30'
        )
        
        response = self.client.delete(f'/api/take/{take.taken_id}/')
    
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    # visualize medication
    
    def test_list_own_medications(self):
        """list user medications"""
        # Criar outro usuário com medicamento
        other_user = User.objects.create_user(
            username="otheruser3",
            email="other3@test.com",
            password="testpass123"
        )
        
        Take.objects.create(
            person_id=other_user.person,
            medication_id=self.medication1,
            quantity='30'
        )
        
        # Criar medicamento para usuário atual
        Take.objects.create(
            person_id=self.user.person,
            medication_id=self.medication2,
            quantity='20'
        )
        
        response = self.client.get('/api/take/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['medication_id'], self.medication2.medication_id)
    
    def test_get_medications_with_leaflets(self):
        """medication with leaflet informations"""
        Take.objects.create(
            person_id=self.user.person,
            medication_id=self.medication1,
            quantity='30'
        )
        
        response = self.client.get('/api/take/medications_with_leaflets/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn('indicacoes_para_uso', response.data[0])
        self.assertIn('efeitos_colaterais', response.data[0])


class MedicationReadOnlyTest(TestCase):
    """ check if the anvisa information is readonly"""
    
    def setUp(self):
        self.client = APIClient()
    
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        
        self.medication = Medication.objects.create(
            medication_id=2001,
            indicacoes_para_uso="Para dor",
            efeitos_colaterais="Pode causar sonolência"
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_cannot_create_medication_manually(self):
        data = {
            'medication_id': 2002,
            'indicacoes_para_uso': 'Teste'
        }
        
        response = self.client.post('/api/medications/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_cannot_edit_medication_fields(self):
        data = {'efeitos_colaterais': 'Novo efeito'}
        
        response = self.client.patch(f'/api/medications/{self.medication.medication_id}/', data, format='json')
        
       
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_cannot_delete_medication(self):
        response = self.client.delete(f'/api/medications/{self.medication.medication_id}/')
        

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_can_list_medications(self):

        response = self.client.get('/api/medications/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_can_retrieve_medication(self):
        response = self.client.get(f'/api/medications/{self.medication.medication_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['medication_id'], self.medication.medication_id)
