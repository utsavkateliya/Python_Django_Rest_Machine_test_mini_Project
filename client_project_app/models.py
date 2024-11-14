from django.db import models
from django.contrib.auth.models import User



############## Client model ##############
class Client(models.Model):
    client_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.client_name, self.id

############## Project model ##############
class Project(models.Model):
    project_name = models.CharField(max_length=100)
    client = models.ForeignKey(Client,related_name='projects', on_delete=models.CASCADE )
    users = models.ManyToManyField(User,related_name='projects')
    created_at =models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')

    def __str__(self):
        return self.project_name