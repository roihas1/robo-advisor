# from rest_framework import serializers
# from .models import InvestorUser, CustomUser
#
#
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = InvestorUser,CustomUser
#         fields = ['id', 'name', 'description']
from rest_framework import serializers
from .models import CustomUser, InvestorUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
        ]


class InvestorUserSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = InvestorUser
        fields = [
            'id',
            'user',
            'risk_level',
            'total_investment_amount',
            'total_profit',
            'stocks_collection_number',
            'stocks_symbols',
            'stocks_weights',
            'sectors_names',
            'sectors_weights',
            'annual_returns',
            'annual_max_loss',
            'annual_volatility',
            'annual_sharpe',
            'total_change',
            'monthly_change',
            'daily_change',
        ]
