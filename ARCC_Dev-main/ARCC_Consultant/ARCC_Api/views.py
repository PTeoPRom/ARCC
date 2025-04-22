from django.shortcuts import render
from rest_framework import viewsets
from .models import AgentData
from .serializer import AgentDataSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

# Create your views here.
class AgentDataViewSet(viewsets.ModelViewSet):
    queryset = AgentData.objects.all()
    serializer_class = AgentDataSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)