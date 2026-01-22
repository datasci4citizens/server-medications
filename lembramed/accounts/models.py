from django.db import models

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
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth = models.DateField(blank=True, null=True)
    email = models.CharField(max_length=255, default="seu_email_aqui@gmail.com")
    password = models.CharField(max_length=255, default="sua_senha_aqui")
    #gender 
    #race
    #location
    def __str__(self):
        return self.name