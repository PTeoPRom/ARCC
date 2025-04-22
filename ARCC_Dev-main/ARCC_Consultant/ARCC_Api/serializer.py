from rest_framework import serializers
from .models import AgentData

class AgentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentData
        fields = '__all__'