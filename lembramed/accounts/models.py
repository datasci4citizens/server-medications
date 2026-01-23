from django.db import models
import uuid

#class App_Person(models.Model):
  #  person_id = models.OneToOneField( # mesmo id do person_id do django app PERSON
     #   'user.person',
      #  primary_key=True,
      #  on_delete=models.CASCADE
   # )
  #  email = models.CharField(max_length=255, blank=True, null=True)
  #  password = models.TextField()
  #  def __str__(self):
  #      return self.email

class New_Person(models.Model):
    # user = models.OneToOneField(
    #     User,
    #     null = False,
    #     blank = False,
    #     on_delete=models.CASCADE
    # )
    person_id = models.UUIDField(
        default = uuid.uuid4,
        editable = False,
        primary_key=True,
        #unique=True
    )
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth = models.DateField(blank=True, null=True)
    email = models.CharField(max_length=255, default="seu_email_aqui@gmail.com") # data from app_person
    password = models.CharField(max_length=255, default="sua_senha_aqui") # data from app_person
    #gender 
    #race
    #location
    def __str__(self):
        return self.name #self.str(person_id)