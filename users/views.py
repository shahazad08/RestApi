import jwt
from rest_framework.filters import OrderingFilter
from django.shortcuts import render
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
# from decorators import apiview
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import resolve
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect
# from usersexample.models import Profile
from django.template.loader import render_to_string
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from requests import auth
from rest_framework_jwt.settings import api_settings

from .serializers import UserSerializer, LoginSerializer
from rest_framework.renderers import TemplateHTMLRenderer
from .models import User
# from rest_framework.request import Request
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView  # Used for a create-only endpoints, provides a post method handler
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework.views import APIView  # Taking the views of REST framework Request & Response
# from .serializers import NoteSerializer,ReadNoteSerializer

# import django_auth.users.serializers
from .tokens import account_activation_token
from django.urls import reverse

# from django_auth.users.tokens import account_activation_token
# from django_auth.users.tokens import account_activation_token
from .forms import SignupForm

from .serializers import NoteSerializer, ReadNoteSerializer,PageNoteSerializer

from rest_framework.decorators import api_view
from .models import User, CreateNotes
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
# from django.core.paginator import Paginator

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


# from .serializers import UserSerializer, LoginSerializer


def home(request):
    return render(request, "home.html", {})  # home page


def signup(request):
    if request.method == 'POST':  # IF method id POST
        form = SignupForm(request.POST)  # SignUp Form
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()  # Save in a DB
            current_site = get_current_site(request)  # get the current site by comparing the domain with the host
            # name from the request.get_host() method.
            message = render_to_string('activate.html', {  # Pass the link information to the message variable
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your blog account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))  # UserId for a decoding
        user = User.object.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):  # if its a valid token
        user.is_active = True  # User is Active
        user.save()
        # login(request, user)
        # return redirect('home')
        return render(request, 'user_login.html')
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
        # return render(request, 'login.html', {'form': form})
    else:
        return HttpResponse('Activation link is invalid!')


def log_me(request):
    return render(request, 'user_login.html', {})


from django.contrib.auth import authenticate, login

from django.urls import reverse


def logins(request):
    print('******************************* **loginsssss***************************')
    print()
    try:
        if request.method == "POST":  # if method as post
            email = request.POST.get('email')  # Get Email
            password = request.POST.get('password')  # Get Password
            user = authenticate(email=email, password=password)
            # user = User.object.get(email=email, password=password)

            if user:  # If it is a User
                if user.is_active:  # If a User is active
                    login(request, user)  # Login maintains a request and a user
                    try:  # The claims in a JWT are encoded as a JSON object that is digitally signed using
                        # JSON Web Signature (JWS) and/or encrypted using JSON Web Encryption (JWE)
                        payload = {
                            'email': email,
                            'password': password,
                        }

                        global token
                        token = jwt.encode(payload, 'SECRET')  # Encodes the token with the secret key and encodes, and
                        # cache.set(token, timeout=CACHE_TTL)
                        # return Response(token, status=status.HTTP_201_CREATED)


                        # return HttpResponse(token,{})
                        return render(request, 'profile.html',{'token':token})  # After Sucessfull returns to the profile page

                        # return HttpResponse(token)
                    except Exception as e:  # Invalid
                        result = {'error': 'please provide an valid email and a password'}
                        return HttpResponse(result)
                else:
                    return HttpResponse('User is Inactive')
                    # # res = {'error': 'can not authenticate with the given credentials or the account has been deactivated'}
                    # return HttpResponse("User Not Found", status=status.HTTP_403_FORBIDDEN)
            else:
                message = "Invalid Login"
                messages.error(request, 'Please Enter the correct login details')
                return render(request, 'user_login.html')
    except Exception as e:
        res = {'error': 'please provide an valid email and a password'}
        return HttpResponse(res)


# @api_view(['GET'])
# def login_token(request):
#     if request.method == "POST":  # if method as post
#         email = request.POST.get('email')  # Get Email
#         password = request.POST.get('password')  # Get Password
#         user = authenticate(email=email, password=password)
#         # user = User.object.get(email=email, password=password)
#
#         if user:  # If it is a User
#             if user.is_active:  # If a User is active
#                 login(request, user)  # Login maintains a request and a user
#                 try:  # The claims in a JWT are encoded as a JSON object that is digitally signed using
#                     # JSON Web Signature (JWS) and/or encrypted using JSON Web Encryption (JWE)
#                     payload = {
#                         'email': email,
#                         'password': password,
#                     }
#
#                     global token
#                     token = jwt.encode(payload, 'SECRET')  #
#                     print(token)
    # if 'token' in cache:
    #     tokens = cache.get('token')
    #     return Response(tokens, status=status.HTTP_201_CREATED)
    #
    # else:









from django.contrib.auth import logout


def exit(request):  # For a Logout
    # logout(request)
    return render(request, "home.html")


import boto3


def fileupload(request):  # Upload a image
    return render(request, 'file_upload.html', {})


def upload(request):  # Displays the uploaded Image i,e Profile Dashboard
    return render(request, 'profile.html', {})


def upload_profilenew(request):
    if request.method == 'POST':
        print()
        print('In Upload View')
        print()
        s3 = boto3.client('s3')  # Using to write software that makes use of Amazon services like S3 and EC2.

        try:
            print('In Boto3')
            file = request.FILES['pic']  # Uploading a Pic
            email = request.POST.get('email')
            print('*******************', email)

            print('In Files')
            key = email + '.jpeg' or email + '.png'
            print('this is key', key)
            s3.upload_fileobj(file, 'fundoobucket', Key=key)


        except MultiValueDictKeyError:
            messages.error(request, "Please select valid file")
            return render(request, 'profile.html')

        return render(request, 'home.html')  # return Home Page
    else:

        return HttpResponse("GET Request")  # Get


# /*****************************************************************************************

#
# class CreateUserAPIView(CreateAPIView):
#     serializer_class = CreateNoteSerializer
#     queryset = Notes.objects.all()

#
# class UserCreateAPI(CreateAPIView):             # Registration using Rest framework Using User Model.
#
#     serializer_class=registrationSerializer
#     queryset = User.object.all()



class createnote(CreateAPIView):
    serializer_class = NoteSerializer
    notes = CreateNotes.objects.all()



class readnote(APIView):
    """
    Retrieve, update or delete a event instance.
    """

    def get_object(self, pk):
        try:
            return CreateNotes.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        event = self.get_object(pk)
        serializer = ReadNoteSerializer(event)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ReadNoteSerializer(data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#
# #
# class deletenote(APIView):
#     serializer_class = DeleteNoteSerializer
#     queryset = CreateNotes.objects.all()
#
#
# @api_view(["DELETE"])
# def delete(request, product_id):
#     CreateNotes.objects.get(id=product_id).delete()
#     return Response({"message": "Notes with id `{}` has been deleted.".format(pk)},status=204)

#
# # #
# def delete(self, request, pk):
#     # Get object with this pk
#     article = get_object_or_404(CreateNotes.objects.all(), pk=pk)
#     article.delete()
#     return Response({"message": "Notes with id `{}` has been deleted.".format(pk)},status=204)


class deletenote(APIView):
    """
    Retrieve, update or delete a event instance.
    """

    def get_object(self, pk):
        try:
            return CreateNotes.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404

    # def get(self, request, pk, format=None):
    #     event = self.get_object(pk)
    #     serializer = DeleteNoteSerializer(event)
    #     return Response(serializer.data)

    def delete(self, request, pk):
        note = CreateNotes.objects.get(pk=pk)
        # delete note
        note.delete()
        # return in response no content
        return Response({"message": "Notes with id `{}` has been deleted.".format(pk)}, status=204)


# serializers = ReadNoteSerializer(data=request.DATA)
# serializers.delete()
# # if serializer.is_valid():
# #     serializer.save()
# #     return Response(serializer.data, status=status.HTTP_201_CREATED)
# # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# return Response({"message": "Notes with id `{}` has been deleted.".format(pk)}, status=204)


class updatenote(APIView):
    def put(self, request, pk, format=None):
        # get all the notes of given requested id(pk)
        note = CreateNotes.objects.get(pk=pk)
        # requested data is serialized and store it in serializer variable
        serializer = ReadNoteSerializer(note, data=request.data)
        # check serialized data is valid or not
        if serializer.is_valid():
            # if valid then save it
            serializer.save()
            # in response return data in json format
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else return error msg in response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def table(request):
    notes = CreateNotes.objects.all().order_by('-created_time')
    return render(request, 'notes/index.html', {'notes': notes})


def paginate(request):
    notes1 = CreateNotes.objects.all()[:4]
    return render(request, 'notes/paginate.html', {'notes1': notes1})







def pratice(request):
    # notes=CreateNotes.objects.all()
    a=10,20
    d = [1, 2, 3, 4, 5, 6, 'Hello', 'Shahazad']
    return render(request,'notes/pratice.html', {'d':d},{'a',a})





from rest_framework import generics
from .paginate import PostLimitOffsetPagination, PostPageNumberPagination
from rest_framework.filters import SearchFilter

class PostListAPIView(generics.ListAPIView):
    serializer_class=PageNoteSerializer
    filter_backends=[SearchFilter,OrderingFilter]
    # search_fields=['title','description']
    pagination_class= PostPageNumberPagination

    def get_queryset(self,*args,**kwargs):
        query_list=CreateNotes.objects.filter()
        return query_list


