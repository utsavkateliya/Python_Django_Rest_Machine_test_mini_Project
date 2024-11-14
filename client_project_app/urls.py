from django.urls import path 
from . import views

urlpatterns = [
    path('register',views.register_user,name='register_user'),
    path('login',views.Login,name='Login'),
    path('logout',views.logout,name='logout'),
    path('clients',views.get_client,name='get_client'),
    path('clients/<int:id>',views.get_client_by_id,name='get_client_by_id'),
    path('create',views.create_client,name='create_client'),
    path('projects',views.get_project,name='get_project'),
    path('projects/<int:id>',views.get_project_by_id,name='get_project_by_id'),
    path('client/<int:client_id>/project',views.assign_project,name='assign_project'),
]
