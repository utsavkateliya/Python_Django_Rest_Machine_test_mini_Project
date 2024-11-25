from .models import Client, Project, User
from .serializers import UserSerializer, UserLoginSerializer,BasicClientSerializer, DetailedClientSerializer, ProjectSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from rest_framework.exceptions import AuthenticationFailed


# Create your views here.
################# Users Registration #################
@api_view(['POST']) 
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message':'User Created Successfully','user':{'id':user.id,'username':user.username,'email':user.email}},status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

################# Users LogIn #################
@api_view(['POST'])
def Login(request): # API endpoint to handle user login.
    if request.user.is_authenticated: # Check if the user is already logged in
        return Response({"error": "You are already logged in"}, status=401) # if logged in no other user can log in 
    else:
        serializer = UserLoginSerializer(data = request.data)
        if serializer.is_valid():
            username=serializer.validated_data['username']
            password=serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                django_login(request,user)
                return Response({'msg':'Login Successfull'},status=status.HTTP_202_ACCEPTED)
            else:
                raise AuthenticationFailed('Inavalid Credentials')
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

################# Users LogOut #################
@api_view(['POST'])
def logout(request): # API endpoint to handle user logout.
    if not request.user.is_authenticated:
        return Response({"error": "You must be logged in to logout"}, status=401)
    else:
        django_logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


################# Clients #################
# GET ALL CLIENTS
@api_view(["GET"]) 
def get_client(request): # API endpoint to fetch client details
    if not request.user.is_authenticated:
        return Response({"error": "You must be logged in to view client details"}, status=401) # checks if the user is logged in then only can view the clients
    else:
        client = Client.objects.all()
        seriaizers = BasicClientSerializer(client, many=True)
        return Response(seriaizers.data)
    

# GET CLIENTS BY ID
#GET/ PUT/ DELETE
@api_view(['GET','PUT','PATCH','DELETE'])
def get_client_by_id(request,id) :# API endpoint to fetch client details with a specific [ID]
    if not request.user.is_authenticated:
        return Response({"error": "You must be logged in to view clients and projects"}, status=401)
    else:    
        try:
            client = Client.objects.get(pk=id) # getting clients id directly from the url 
        except Client.DoesNotExist:
            return Response({'msg': 'Client Does Not Exists'},status=status.HTTP_404_NOT_FOUND) # throws msg if client does not exists with a specific id 
        
        if request.method == 'GET':
            searilizers = DetailedClientSerializer(client)
            return Response(searilizers.data)
        
        elif request.method == 'PUT':  # Handle full data update
            serializers = DetailedClientSerializer(client, data=request.data)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            return Response(serializers.errors, status=status.HTTP_404_NOT_FOUND)

        elif request.method == 'PATCH': # Handle partial data updates
            serializers = DetailedClientSerializer(client, data=request.data, partial=True)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_200_OK)
            return Response({'msg':'Enter the details to be updated'}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE': # if the user logged in is superuser then only the clients data will be deleted 
            if request.user.is_superuser:
                client.delete()
                return Response({'msg':'Client Deleted Successfully'},status.HTTP_204_NO_CONTENT)
            else:
                return Response({'msg':'You must be a super user to delete a client'},status.HTTP_204_NO_CONTENT)


# POST CLIENT (CREATING NEW CLIENTS)
# POST
@api_view(["POST"])
def create_client(request): # API endpoint to create a new client. 
    if not request.user.is_authenticated:
        return Response({"error": "You must be logged in to create new clients"}, status=401)
    else:
        serializers = BasicClientSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save(created_by=request.user)
            serializers.save()
            return Response({'msg':'Data Created','client':serializers.data}, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)




################## Projects #################
# GET ALL PROJECTS FOR THE USERS WHO ARE LOGGED IN   
@api_view(['GET']) 
def get_project(request): # API endpoint to fetch project details
    if not request.user.is_authenticated:
        return Response({"error": "You must be logged in to view projects"}, status=401) # the user must be logged in to view projects

    if request.method =='GET':
        project = Project.objects.filter(users=request.user) #returns only the project with the specific user logged in 
        serializers = ProjectSerializer(project, many=True)
        return Response(serializers.data)
    


# GET project details by id
@api_view(['GET','DELETE']) 
def get_project_by_id(request, id):  # API endpoint to fetch project details by specific project [ID]
    if not request.user.is_authenticated: 
        return Response({"error": "You must be logged in to view projects"}, status=401)
    try: 
        project = Project.objects.get(pk=id)
    except Project.DoesNotExist:
        msg={"message":"No Project Found with such Id"}
        return Response(msg,status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        seralizers = ProjectSerializer(project)
        return Response(seralizers.data)
    elif request.method == 'DELETE':
            project.delete()
            return Response({'msg':'Project Deleted Successfully'},status.HTTP_204_NO_CONTENT)


# Creating a new project and assigning it to the existing user
@api_view(['POST'])
def assign_project(request,client_id): # API endpoint to assign project to the existing user with sepcific User['id','username']
    if not request.user.is_authenticated: # validates if the user is logged in before creating and assigning task
        return Response({"error": "You must be logged in to Create projects"}, status=401)
    
    project_name = request.data.get('project_name')
    # client_id = request.data.get('client_id') # ignored so it can directly take clientid from the url
    user_data = request.data.get('users')
    if not project_name or not user_data:
        return Response({"error": "Project name and users are required"}, status=400)

    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return Response({"error":"Client Not Found"},status=status.HTTP_404_NOT_FOUND)
    
    users = []  # This will hold the list of user objects
    for user_info in user_data:
        try:
            # Verify both user ID and username
            user = User.objects.get(id=user_info['id'], username = user_info['username'])
            users.append(user)  # Append the user to the list
        except User.DoesNotExist:
            return Response({"error": f"User with id {user_info['id']} and username {user_info['username']} not found."}, status=status.HTTP_400_BAD_REQUEST)
    
    project = Project.objects.create(project_name=project_name, client=client, created_by=request.user)
    project.users.set(users)

    serializer = ProjectSerializer(project)
    return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    




