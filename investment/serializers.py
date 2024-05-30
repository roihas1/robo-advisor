from rest_framework import serializers
from .models import Investment


class investmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = '__all__'
