from rest_framework import serializers
from .models import UserModel
from django.contrib.auth.hashers import make_password

class userSerializer(serializers.ModelSerializer):
    avatar_url = serializers.ImageField(use_url=True, required=False, allow_null=True)

    class Meta:
        model = UserModel
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False,    # ✅ not required on update
                'allow_blank': True,  # ✅ allow empty string
            }
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # ✅ only hash password if it's actually provided
        if 'password' in validated_data and validated_data['password']:
            validated_data['password'] = make_password(validated_data['password'])
        else:
            validated_data.pop('password', None)  # ✅ remove it so existing password stays
        return super().update(instance, validated_data)