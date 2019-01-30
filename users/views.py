from datetime import datetime

import jwt
import objects as objects
from django.conf import settings
from django.contrib.auth import user_logged_in
# from rest_framework.request import Request
from django.http import HttpResponse
from django.shortcuts import render
from django_extensions.db.fields import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt import settings
from rest_framework_jwt.serializers import jwt_payload_handler
from . import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import User
from .serializers import UserSerializer, LoginSerializer
from django.contrib.auth import authenticate, login


def home(request):
    return render(request, "home.html", {})


#   return HttpResponse('home.html',{})

class CreateUserAPIView(CreateAPIView):
    # permission_classes = (AllowAny,)
    #
    # def post(self, request):
    #     user = request.data
    #     serializer = UserSerializer(data=user)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    serializer_class = UserSerializer
    queryset = User.object.all()


class LoginView(APIView):
    serializer_class = LoginSerializer
    queryset = User.object.all()
    http_method_names = ['post', 'get']



    def post(self, request):
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            # user = authenticate(email=email, password=password)
            user = User.object.get(email=email, password=password)
            if user:
                try:
                    payload = {
                        'email': email,
                        'password': password,
                    }
                    # token = {'token': jwt.encode(payload,'SECRET')}
                    token = jwt.encode(payload, 'SECRET')
                    return HttpResponse(token, {})
                except Exception as e:
                    raise e
            # else:
            #     res = {'error': 'can not authenticate with the given credentials or the account has been deactivated'}
            #     return Response(res, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            res = {'error': 'please provide an valid email and a password'}
            return Response(res)
