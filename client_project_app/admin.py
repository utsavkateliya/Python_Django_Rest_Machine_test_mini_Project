from django.contrib import admin

# Register your models here.
from .models import Client, Project

class ClientAdmin(admin.ModelAdmin):
    list_display=('id','client_name','created_at','updated_at','created_by',)

class ProjectAdmin(admin.ModelAdmin):
    list_display=('project_name','client','created_at','created_by')

    # def client_name(self, obj):
    #     return obj.client.client_name  # Retrieve client_name from the related Client model
    # client_name.admin_order_field = 'client__client_name'  # Allow sorting by client_name
    # client_name.short_description = 'Client'

admin.site.register(Client, ClientAdmin)
admin.site.register(Project, ProjectAdmin)
