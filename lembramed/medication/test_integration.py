from copy import deepcopy
from unittest.mock import patch
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from medication.models import Medication, Medication_Name, Active_Ingredient, Leaflet, Take, TakeRecord

class IntegrationTests(APITestCase):
    def setUp(self):
        name = Medication_Name.objects.create(name='Catálogo de teste')
        self.med = Medication.objects.create(medication_id=1, process_num=123, name=name)
        self.med.active_ingredients.add(Active_Ingredient.objects.create(active_ingredient='ingrediente'))
        Leaflet.objects.create(medication=self.med, como_usar_medicamento='Texto de teste')
        self.credentials = {'email':'patient@example.com','password':'IntegrationPassword42','first_name':'Paciente','last_name':'Teste','profile':{'wakeTime':'07:00'}}
        response = self.client.post('/auth/register/', self.credentials, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.user = response.data['user']
        self.tokens = response.data['tokens']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+self.tokens['access'])
        self.payload = {'medication_id':1, 'priority':1, 'quantity':'20', 'client_id':'stable-client-id', 'dosage':'1 comprimido', 'brand':'Marca', 'type':'tablet', 'stock_reminder_enabled':True,'stock_reminder_threshold':5,'dose_status':{}, 'records':[{'cycle_type':'daily','begin':'2026-10-30','end':None,'days':'sun,mon,tue,wed,thu,fri,sat','take_at':'08:00'}, {'cycle_type':'daily','begin':'2026-10-30','end':None,'days':'mon','take_at':'20:00'}]}

    def create_take(self):
        response = self.client.post('/medication/take/', self.payload, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        return response.data['taken_id']

    def test_auth_login_me_and_refresh(self):
        me = self.client.get('/auth/me/')
        self.assertEqual(me.data['person_id'], self.user['person_id'])
        self.assertEqual(me.data['profile']['wakeTime'], '07:00')
        self.client.credentials()
        login = self.client.post('/auth/login/', {key:self.credentials[key] for key in ['email','password']}, format='json')
        self.assertEqual(login.status_code, 200, login.data)
        self.assertEqual(login.data['user']['person_id'], self.user['person_id'])
        refresh = self.client.post('/auth/refresh/', {'refresh':self.tokens['refresh']}, format='json')
        self.assertEqual(refresh.status_code, 200, refresh.data)
        self.assertIn('access', refresh.data)
        self.assertIn('refresh', refresh.data)
        self.assertEqual(self.client.post('/auth/refresh/', {'refresh':self.tokens['refresh']}, format='json').status_code, 401)

    @patch('authentication.views.id_token.verify_oauth2_token')
    def test_google_uses_same_contract(self, verify):
        verify.return_value = {'sub':'google-test-id','email':'google@example.com','given_name':'Google','family_name':'Teste'}
        self.client.credentials()
        response = self.client.post('/auth/google/', {'token':'test-id-token'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('person_id', response.data['user'])
        self.assertIn('access', response.data['tokens'])

    def test_catalog_contract_search_and_leaflet(self):
        response = self.client.get('/medication/?search=ingrediente')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['count'], 1)
        med = response.data['results'][0]
        self.assertEqual(med['active_ingredients'], [{'active_ingredient':'ingrediente'}])
        self.assertEqual(med['leaflet']['como_usar_medicamento'], 'Texto de teste')

    def test_create_edit_dose_history_and_delete(self):
        pk = self.create_take()
        self.assertEqual(TakeRecord.objects.filter(taken_id=pk).count(), 2)
        self.assertEqual(str(Take.objects.get(pk=pk).person_id_id), self.user['person_id'])
        data = deepcopy(self.payload)
        data['records'] = [{'cycle_type':'interval','begin':'2026-10-30','end':None,'days':'sun,mon,tue,wed,thu,fri,sat','take_at':'08:00','take_cycle':8}]
        data['dose_status'] = {'stable-client-id-2026-10-30-08:00':{'status':'taken','takenAt':'2026-10-30T11:00:00Z'}}
        response = self.client.patch(f'/medication/take/{pk}/', data, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(len(response.data['records']), 1)
        self.assertIsNone(response.data['records'][0]['end'])
        listed = self.client.get('/medication/take/').data['results'][0]
        self.assertEqual(listed['dose_status'], data['dose_status'])
        self.assertEqual(listed['dosage'], data['dosage'])
        self.assertEqual(self.client.delete(f'/medication/take/{pk}/').status_code, 204)
        self.assertFalse(TakeRecord.objects.filter(taken_id=pk).exists())

    def test_retries_do_not_duplicate_treatment(self):
        pk = self.create_take()
        self.assertEqual(self.create_take(), pk)
        self.assertEqual(Take.objects.count(), 1)
        self.assertEqual(TakeRecord.objects.count(), 2)
        self.payload['dosage'] = '2 comprimidos'
        self.assertEqual(self.create_take(), pk)
        self.assertEqual(Take.objects.get(pk=pk).dosage, '2 comprimidos')

    def test_patient_isolation(self):
        pk = self.create_take()
        other = User.objects.create_user(username='other', email='other@example.com', password='AnotherPassword42')
        self.client.force_authenticate(other)
        self.assertEqual(self.client.get('/medication/take/').data['count'], 0)
        for method in ['get','patch','delete']:
            response = getattr(self.client, method)(f'/medication/take/{pk}/', {}, format='json')
            self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.get('/medication/take_record/').data['count'], 0)
        spoof = deepcopy(self.payload); spoof['person_id'] = self.user['person_id']; spoof['client_id'] = 'other'
        response = self.client.post('/medication/take/', spoof, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(str(Take.objects.get(pk=response.data['taken_id']).person_id_id), str(other.person.pk))

    def test_invalid_schedule_is_atomic(self):
        invalid = deepcopy(self.payload); invalid['records'][1]['end'] = '2020-01-01'
        response = self.client.post('/medication/take/', invalid, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(Take.objects.count(), 0)
        pk = self.create_take()
        response = self.client.patch(f'/medication/take/{pk}/', invalid, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TakeRecord.objects.count(), 2)
