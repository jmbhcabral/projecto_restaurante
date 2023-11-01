from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from perfil.models import Perfil
from django.contrib.auth.models import User


class PerfilSerializer(ModelSerializer):
    class Meta:
        model = Perfil
        fields = ('data_nascimento', 'telemovel', 'estudante',)


class UserRegistrationSerializer(ModelSerializer):
    perfil = PerfilSerializer()

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'password',)

    def create(self, validated_data):
        perfil_data = validated_data.pop('perfil', None)
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        user.set_password(validated_data['password'])
        user.save()
        if perfil_data:
            Perfil.objects.create(usuario=user, **perfil_data)

        return user
