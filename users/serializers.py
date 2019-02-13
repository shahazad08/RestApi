from rest_framework.validators import UniqueValidator

from .models import User, CreateNotes
from rest_framework import serializers  # Serializers allow complex data such as query sets and model instances to be
# from rest_framework.pagination import PaginationSerializer
from django.core.paginator import Paginator
from rest_framework import pagination


# from rest_framework.pagination import PaginationSerializer

# converted to native Python data types that can then be easily rendered into JSON, XML or other content types


# ModelSerializer: It is a class which provides a useful shortcut for creating serializers
# that deal with model instances and query sets.


class UserSerializer(serializers.ModelSerializer):  # Created the User Serializer for all the fields in a model
    date_joined = serializers.ReadOnlyField()  # date joined should be in a read_only modes
    password = serializers.CharField(style={'input_type': 'password'})  # password should be properly validated
    # email = serializers.EmailField(validators=[UniqueValidator(queryset=User.object.all())])
    email = serializers.RegexField(regex=r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                                   required=True)

    class Meta(object):  # We have  use of Meta class is simply to provide metadata to the ModelForm class.
        model = User  # Shows that the User fields contain the model class
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined', 'password')


class LoginSerializer(serializers.ModelSerializer):  # Created the user serializer for a Login
    password = serializers.CharField(style={'input_type': 'password'})
    email = serializers.RegexField(regex=r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                                   required=True)

    # email = serializers.CharField(max_length=30)
    class Meta:
        model = User  # Contains the fields of email and a password
        fields = ['email', 'password']


# ***********************************************************************************


#
# class registrationSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(max_length=20)
#     password = serializers.CharField(style={'input_type': 'password'})
#     # confirm_password=serializers.CharField(style={'input_type':'password'})
#     email = serializers.RegexField(regex=r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
#                                    required=True)
#
#     class Meta:
#         model = User  # Database Model to  store the data in .
#         fields = ('username', 'password', 'email')
#
#


class NoteSerializer(serializers.ModelSerializer):
    title= serializers.RegexField(regex=r"^[a-zA-Z]+$",required=True)
    color= serializers.RegexField(regex=r"^[a-zA-Z]+$",required=True)
    label = serializers.RegexField(regex=r"^[a-zA-Z]+$", required=True)

    class Meta:
        model = CreateNotes
        # fields = '__all__'
        fields = ('title', 'description', 'color', 'label')


class ReadNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateNotes
        fields = '__all__'



class PageNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateNotes
        fields = ('title', 'description')

