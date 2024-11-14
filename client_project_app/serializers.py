from rest_framework import serializers
from .models import Client, Project
from django.contrib.auth.models import User
from django.contrib.auth import authenticate



############# Serializers For Projects #############
class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.client_name', read_only = True)
    created_by = serializers.CharField(source='created_by.username')
    users = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id','project_name', 'client_name', 'users','created_at', 'created_by']

    def get_users(self,obj):
        return[{'id': user.id, 'username':user.username} for user in obj.users.all() ]



############# Serializers For Client #############
class BasicClientSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Client
        fields = ['id','client_name','created_at','created_by']


class DetailedClientSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    class Meta:
        model = Client
        fields = ['id','client_name','projects','created_at','created_by','updated_at']


############# Serializer For User Registration #############

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    class Meta:
        model = User
        fields = ['id','username','email','password']
        extra_kargs = {'password': {'write_only':True}}

    def create(self,validated_data):
        email = validated_data.pop('email')
        user = User.objects.create_user(email=email, **validated_data)
        return user



############# Serializer For User Login #############

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username and password :
                raise serializers.ValidationError('Username and Password are Required')

        user = authenticate(username=username,password=password)
        if not user:
            raise serializers.ValidationError('Invalid Username or Password')
            
            
        attrs['user'] = user
        return attrs

