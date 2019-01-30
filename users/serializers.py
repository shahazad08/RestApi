from rest_framework import serializers  # Serializers allow complex data such as query sets and model instances to be
# converted to native Python data types that can then be easily rendered into JSON, XML or other content types


# ModelSerializer: It is a class which provides a useful shortcut for creating serializers
# that deal with model instances and query sets.

from .models import User


class UserSerializer(serializers.ModelSerializer):  #
    date_joined = serializers.ReadOnlyField()
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta(object):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined', 'password')
        # extra_kwargs = {'password': {'write_only': True}}


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'password']
