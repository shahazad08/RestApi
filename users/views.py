import json
import jwt
from django.views.decorators.http import require_POST
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
from django.http import JsonResponse
from .serializers import UserSerializer, LoginSerializer, LabelSerializer
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
from django.contrib.auth import logout
# from .serializers import NoteSerializer,ReadNoteSerializer

# import django_auth.users.serializers
from .tokens import account_activation_token
from django.urls import reverse

# from django_auth.users.tokens import account_activation_token
# from django_auth.users.tokens import account_activation_token
from .forms import SignupForm

from .serializers import NoteSerializer, ReadNoteSerializer, PageNoteSerializer

from rest_framework.decorators import api_view
from .models import User, CreateNotes, Labels, MapLabel
from django.core.cache import cache
from django.conf import settings
from .upload import upload_profilenew

from rest_framework import generics  # For a List API use a generics
from .paginate import PostLimitOffsetPagination, PostPageNumberPagination  # Creating our own no. of records in a Pages
from rest_framework.filters import SearchFilter  # it allows users to filter down a queryset based on a model's
# fields, displaying the form to let them do this.

from django.contrib.auth import authenticate, login

from django.urls import reverse

from django.core.cache.backends.base import DEFAULT_TIMEOUT  # Setting a time for a cache to store

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
            return Response('Please confirm your email address to complete the registration')

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


from django.views.decorators.csrf import csrf_exempt


#
@api_view(['POST'])
@csrf_exempt
# @require_POST
@require_POST
def logins(request):
    res = {}
    res['message'] = 'Something bad happend'
    res['success'] = False

    print('******************************* **loginsssss***************************')
    try:
        email = request.POST.get('email')  # Get Email
        password = request.POST.get('password')  # Get Password
        if email is None:
            raise Exception("Email is required")
        if password is None:
            raise Exception("Password is required")
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
                    token = jwt.encode(payload, "secret_key", algorithm='HS256').decode('utf-8')
                    # authenticate_header='token'
                    #
                    # jwt_token = {
                    #     'token': token
                    # }
                    res['message'] = "Login Sucessfull"
                    res['success'] = True
                    res['data'] = token

                    return JsonResponse(res, status=status.HTTP_201_CREATED)
                    # return HttpResponse(request, 'profile.html',{'token': token})  # After Sucessfull returns to the profile page
                    #

                    # cache.set(token, timeout=CACHE_TTL)
                    # return Response(token, status=status.HTTP_201_CREATED)

                    # return HttpResponse(token,{})
                    # return render(request, 'profile.html',
                    #                      {'token': token})  # After Sucessfull returns to the profile page

                    # return HttpResponse(token)
                except Exception as e:  # Invalid
                    result = {'error1': 'please provide an valid email and a password'}
                    return HttpResponse(result)
            else:
                res['message'] = "User is Inactive"
                return JsonResponse(res)
        else:
            res['message'] = 'Username or Password is not correct'  # Invalid login details
            messages.error(request, 'Invalid login details')
            return JsonResponse(res)

    except Exception as e:
        print(e)


#         # res = {'error': 'please provide an valid email and a password'}
#         # return HttpResponse(res)
#
#
#


# @cache_page(CACHE_TTL)


#
# def recipes_view(request):
#     tokens = token
#     return render(request, 'receive.html', {tokens: tokens})


def exit(request):  # For a Logout
    # logout(request)
    return render(request, "home.html")


def fileupload(request):  # Upload a image
    return render(request, 'file_upload.html', {})


def upload(request):  # Displays the uploaded Image i,e Profile Dashboard
    return render(request, 'profile.html', {})


def upload1(request):
    # file = request.FILES['pic']  # Uploading a Pic
    # email = request.POST.get('email')
    upload_profilenew(file, name)


# /***********************************Template for a RestAPI ******************************************************

#
# class CreateUserAPIView(CreateAPIView):
#     serializer_class = CreateNoteSerializer
#     queryset = Notes.objects.all()

#
# class UserCreateAPI(CreateAPIView):             # Registration using Rest framework Using User Model.
#
#     serializer_class=registrationSerializer
#     queryset = User.object.all()


# /**********************************Notes****************************************************************

# class createnote(CreateAPIView):  # Creates a Note using REST API
#     def post(self,request):
#         serializer_class = NoteSerializer
#         notes = CreateNotes.objects.all()
#         res = {}
#         res['data'] = {}
#         res['message'] = 'Something bad happened'
#         res['success'] = False
#         if serializer_class.is_valid():
#             # res['data'] = {}
#             res['message'] = 'Sucessfully Created'
#             res['success'] = True
#             return Response(res,status=204)
#         else:
#             res['message'] = 'Something gets wrong'
#             return Response(res, status=404)

from django.middleware.csrf import get_token


# class createnote(APIView):
#     def post(self, request, format=None):
#         res = {}
#         # res['data'] = serializer.data
#         res['message'] = 'Something added'
#         res['success'] = True
#         print(request.user)
#         try:
#             # notes=CreateNotes.objects.all()
#             # notes1=User.object.filter(id=request.id)
#             # n2=User.id
#             # print('ddfgdfg',n2)
#             n1=CreateNotes.user
#             print(n1)
#             serializer = NoteSerializer(data=request.data) # requested data in a serializer
#             # users=User.objects.get(user=request.user)
#             # user = self.context['request'].user
#             # user_id = self.context['request'].user.id
#             # print(user_id)
#
#             # user=CreateNotes.objects.filter(user.email)
#             # print(user)
#             # # user = None
#             # user = logins(request)
#             # print(user)
#             # # is_exists=CreateNotes.objects.filter
#             # user=serializer.user
#             # check serialized data is valid or not
#             # id=User.object.filter(id=request.id)
#             if serializer.is_valid(): # if valid
#                 # if valid then save it
#                 serializer.save() # save in a db
#                 res['data'] = serializer.data # message of passing data in a SMD format
#                 res['message'] = 'Notes are added in a database'
#                 res['success'] = True
#                 return Response(res, status=status.HTTP_201_CREATED)
#
#
#             else:
#                 res['message'] = 'Unssucess' # Something wrong
#                 res['success'] = False
#
#                 # in response return data in json format
#                 return Response(res, status=status.HTTP_201_CREATED)
#
#         except Exception as e:
#             print(e)


class createnote(APIView):
    def post(self, request, format=None):
        res = {}
        # res['data'] = serializer.data
        res['message'] = 'Something added'
        res['success'] = True
        try:
            # notes=CreateNotes.objects.all()
            serializer = NoteSerializer(data=request.data)
            print(serializer)
            # print(request.data)

            # user=serializer.user
            # check serialized data is valid or not








            if serializer.is_valid():
                # if valid then save it
                serializer.save()
                res['data'] = serializer.data
                res['message'] = 'Notes are added in a database'
                res['success'] = True
                return Response(res, status=200)


            else:
                res['message'] = 'Unssucess'
                res['success'] = False

                # in response return data in json format
                return Response(res, status=204)

        except Exception as e:
            print(e)


class readnote(APIView):  # Read a Note

    """
    Retrieve, update or delete a event instance.
    """

    def get_object(self, pk):  # Get the data of a particular record through the primary key
        try:
            return CreateNotes.objects.get(pk=pk)  # IF the requested pk matches then return the pk of a record
        except Event.DoesNotExist:  # Raise Error, data not found
            raise Http404

    def get(self, request, pk):  # Used GET method to display the record
        res = {}
        res['message'] = 'Something bad happend'
        res['success'] = False

        try:
            if pk is not None:
                event = self.get_object(pk)  # Assign the pk(data) to the event
                serializer = ReadNoteSerializer(event)  # Using pk display the values in a serializer field
                res['message'] = 'Requested Data Display'
                res['success'] = True
                res['data'] = serializer.data
                return Response(res, status=status.HTTP_201_CREATED)  # Display the data

        except Exception as e:
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            res['success'] = False
            return Response(res, status=404)

            # return Response({"message": "Notes with id `{}` is not present.".format(pk)}, status=204)


class deletenote(APIView):  # Delete a Note
    """
    Retrieve, update or delete a event instance.
    """

    def get_object(self, pk):
        try:
            return CreateNotes.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404

    def delete(self, request, pk):
        res = {}
        res['data'] = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is not None:
                note = CreateNotes.objects.get(pk=pk)  # get requested id from a Notes
                if note.trash == False:  # if trash is false, change to true
                    note.trash = True
                    note.save()  # save in a db
                    res['data'] = note.id
                    res['message'] = 'Note has been moved to trash'
                    res['success'] = True
                    return Response(res, status=status.HTTP_201_CREATED)  # Display the data

                    # return Response({"message": "Notes with id `{}` has been moved to Trash.".format(pk)}, status=204)

                else:
                    note.is_deleted = True  # if is_deleted is true
                    note.delete()  # delete it
                    res['data'] = note.id
                    res['message'] = 'Note has been deleted from trash'
                    res['success'] = True
                    return Response(res, status=status.HTTP_201_CREATED)  # Display the data

                # return in response no content and format(pk) displays the
                # return Response({"message": "Notes with id `{}` has been deleted from Trash.".format(pk)}, status=204)
        except Exception as e:
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            res['success'] = False
            return Response(res, status=404)
        # except Exception as e:
        #     return Response({"message": "Notes with id `{}` is not present.".format(pk)}, status=204)


class restorenote(APIView):
    def post(self, request, pk, format=None):
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is not None:
                note = CreateNotes.objects.get(pk=pk)
                a = ReadNoteSerializer(data=request.data)
                if note.trash == True:
                    note.trash = False
                    note.save()

                res['message'] = "Selected Note has been Restored"
                res['success'] = True
                res['data'] = note.id
                return Response(res, status=204)

            else:
                res['message'] = 'Unable to find Note. Missing Note ID'
                return Response(res, status=200)

        except CreateNotes.DoesNotExist:
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return Response(res, status=404)

        except Exception as e:
            print(e)
            return Response(res, status=404)

            # return Response({"message": "Notes with id `{}` has been Restored.".format(pk)}, status=204)
        # except Exception as e:
        #     res[]
        #     return Response({"message": "Notes with id `{}` is not present.".format(pk)}, status=204)


class updatenote(APIView):  # Update a Note

    def put(self, request, pk):  # get all the notes of given requested id(pk)
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            note = CreateNotes.objects.get(pk=pk)
            print('------------------------', note)
            # requested data is serialized and store it in serializer variable
            serializer = ReadNoteSerializer(note, data=request.data)
            # check serialized data is valid or not
            if serializer.is_valid():
                # if valid then save it
                serializer.save()
                res['data'] = serializer.data  # message of passing data in a SMD format
                res['message'] = 'Notes are Updated in a database'
                res['success'] = True
                return Response(res, status=status.HTTP_201_CREATED)
                # in response return data in json format

            else:
                res['message'] = 'Unssucess'  # Something wrong
                res['success'] = False

                # in response return data in json format
                return Response(res, status=status.HTTP_201_CREATED)
            # else return error msg in response
        except CreateNotes.DoesNotExist:
            print('Note doenst exists')
            res['message'] = 'Note doesnt exists'
            return Response(res, status=404)

        except Exception as e:
            print(e)
            return Response(res, status=404)


class archivenote(APIView):  # Delete a Note
    """
    Retrieve, update or delete a event instance.
    """

    # def get_object(self, pk):
    #     try:
    #         return CreateNotes.objects.get(pk=pk)
    #     except Event.DoesNotExist:
    #         raise Http404

    def post(self, request, pk):
        res = {}
        res['data'] = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is not None:
                note = CreateNotes.objects.get(pk=pk)  # get particular note from a id
                if note.is_archived == False:  # if archived is false, change it to true, as to move in a archived
                    note.is_archived = True
                    note.save()  # save in a db
                    # return Response({"message": "Notes with id `{}` has been moved to Archive.".format(pk)}, status=204)
                    res['message'] = "Selected Note has been moved to Archive"
                    res['success'] = True
                    res['data'] = note.id

                    return Response(res, status=204)  # return result


                else:
                    note.is_archived = False
                    note.save()
                # return in response no content and format(pk) displays the
                # return Response({"message": "Notes with id `{}` has been Move to dashboard.".format(pk)}, status=204)
                res['message'] = "Note has been moved to Dashboard"
                res['success'] = False
                res['data'] = note.id
                return Response(res, status=204)

        except CreateNotes.DoesNotExist:  # catch the exception as if the note exists
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return Response(res, status=404)

        except Exception as e:
            print(e)
            return Response(res, status=404)

        # except Exception as e:
        #     return Response({"message": "Notes with id `{}` is not present.".format(pk)}, status=204)


class colornote(APIView):  # Delete a Note
    """
    Retrieve, update or delete a event instance.
    """

    def post(self, request, pk):
        res = {}
        res['data'] = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is not None:
                note = CreateNotes.objects.get(pk=pk)
                # color = request.POST.get('color')
                # get.color = serializers.RegexField(regex=r"^[-\w\s]+[-\w\s]+(?:,[-\w\s]*)*$", required=True)

                note.color = request.POST.get('color')  # request the color from notes model, for change
                note.save()  # save to db
                res['message'] = "Color has been Changed."  # message for change color
                res['success'] = True
                res['data'] = note.id
                return Response(res, status=204)  # return result

            else:
                res['message'] = 'Unable to find Note. Missing Note ID'  # missing id
                return Response(res, status=200)  # return res

        except CreateNotes.DoesNotExist:
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'  # message if note doesnot exists
            return Response(res, status=404)

        except Exception as e:
            print(e)
            return Response(res, status=404)


class ispinned(APIView):  # Delete a Note
    """
    Retrieve, update or delete a event instance.
    """

    # def get_object(self, pk):
    #     try:
    #         return CreateNotes.objects.get(pk=pk)
    #     except Event.DoesNotExist:
    #         raise Http404

    def post(self, request, pk):  #
        res = {}
        res['data'] = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is not None:
                note = CreateNotes.objects.get(pk=pk)  # get a requested pk
                if note.is_pinned == False:  # if not pinned
                    note.is_pinned = True  # change it to pin
                    note.save()  # save in a db
                    res['message'] = "Notes has been Pinned to Top."  # message in a SMD format
                    res['success'] = True
                    res['data'] = note.id
                    return Response(res, status=204)

                else:
                    note.is_pinned = False  # if not pinned, save as it is
                    note.save()
                    res['message'] = "Notes has been Move to Unpinned"
                    res['success'] = False
                    res['data'] = note.id
                return Response(res, status=204)

            else:
                res['message'] = 'Unable to find Note. Missing Note ID'  # message for a missing id
                return Response(res, status=200)

        except CreateNotes.DoesNotExist:  # catch exception if note doesnt exists
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return Response(res, status=404)

        except Exception as e:
            print(e)
            return Response(res, status=404)

        # except Exception as e:
        #     return Response({"message": "Notes with id `{}` is not present.".format(pk)}, status=204)


class copynote(APIView):
    # def get_object(self, pk):
    #     try:
    #         return CreateNotes.objects.get(pk=pk)
    #     except Event.DoesNotExist:
    #         raise Http404

    def post(self, request, pk):
        # get note with given id
        res = {}
        res['data'] = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk:
                note = CreateNotes.objects.get(pk=pk)

                # kwargs = model_to_dict(instance, exclude=['id'])
                # new_instance = CreateNotes.create(**kwargs)

                title = note.title
                description = note.description
                created_time = note.created_time
                remainder = note.remainder
                is_archived = note.is_archived
                is_deleted = note.is_deleted
                color = note.color
                image = note.image
                trash = note.trash
                is_pinned = note.is_pinned
                label = note.label
                # collaborate=note.collaborate
                user = note.user
                newcopy = CreateNotes(title=title, description=description, created_time=created_time,
                                      remainder=remainder, is_archived=is_archived, is_deleted=is_deleted, color=color,
                                      image=image, trash=trash, is_pinned=is_pinned, label=label, user=user)
                # save newcopy to database
                newcopy.save()
                # res['data'] = {' newcopy ': newcopy}
                res['message'] = "Note is Coped "
                res['success'] = True

                return Response(res, status=204)
            else:
                res['message'] = 'Unable to find Note. Missing Note ID'
                return Response(res, status=200)
        except CreateNotes.DoesNotExist:
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return Response(res, status=404)
        except Exception as e:
            print(e)
            return Response(res, status=404)


# **************************************Labels*************************************


#
class create_label(APIView):

    def post(self, request):
        res = {}
        # res['data'] = serializer.data
        res['message'] = 'Something added'
        res['success'] = True
        try:
            # notes=CreateNotes.objects.all()
            serializer = LabelSerializer(data=request.data)
            print("-------", serializer)
            # print(request.data)

            # user=serializer.user
            # check serialized data is valid or not
            if serializer.is_valid():
                # if valid then save it
                serializer.save()
                res['data'] = serializer.data
                res['message'] = 'Labels are added in a database'
                res['success'] = True
                return Response(res, status=200)


            else:
                res['message'] = 'Unssucess'
                res['success'] = False

                # in response return data in json format
                return Response(res, status=204)

        except Exception as e:
            print(e)


class deletelabel(APIView):  # Delete a Note

    def delete(self, request, pk):
        res = {}
        res['data'] = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is not None:
                label = Labels.objects.get(pk=pk)  # get requested id from a Labels

                res['data'] = label.id
                label.delete()
                res['message'] = "Label has been deleted"
                res['success'] = True
                return Response(res, status=200)  # Display the data

            else:
                res['message'] = 'Unsuccess'
                res['success'] = False
                return Response(res, status=status.HTTP_201_CREATED)  # Display the data

        except Exception as e:
            print('Label doesnt exists')
            res['message'] = 'Label doesnt exists'
            res['success'] = False
            return Response(res, status=404)


class updatelabel(APIView):  # Update a Note

    def put(self, request, pk):  # get all the labels of given requested id(pk)
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            label = Labels.objects.get(pk=pk)

            # requested data is serialized and store it in serializer variable
            serializer = LabelSerializer(label, data=request.data)
            # check serialized data is valid or not
            if serializer.is_valid():
                # if valid then save it
                serializer.save()
                res['data'] = serializer.data  # message of passing data in a SMD format
                res['message'] = 'Labels are Updated in a database'
                res['success'] = True
                return Response(res, status=status.HTTP_201_CREATED)
                # in response return data in json format

            else:
                res['message'] = 'Unssucess'  # Something wrong
                res['success'] = False

                # in response return data in json format
                return Response(res, status=status.HTTP_201_CREATED)
            # else return error msg in response
        except CreateNotes.DoesNotExist:
            print('Note doenst exists')
            res['message'] = 'Note doesnt exists'
            return Response(res, status=404)

        except Exception as e:
            print(e)
            return Response(res, status=404)


# class addLabelOnNote(APIView):
#     def addLabelsOnNotes(self,request,pk,pk1):
#         # label_id = request.POST.get('label_id')
#         #
#         # note_id = request.POST.get('note_id')
#         #
#         label_id=LabelSerializer(pk=pk)
#         print("***********", label_id)
#         note_id=CreateNotes.objects.get(pk1=pk1)
#         print("--------", note_id)
#         # print("1212",note)
#         # label = Labels.objects.get(id=label_id)
#         # print("3232",label)
#         # maplabel = MapLabel.objects.filter(note_id=note, label_id=label)
#         # print(maplabel)
#         # if len(maplabel) == 0:
#         #     obj = MapLabel(note_id=note, label_id=label)
#         #     obj.save()
#         #
#         # # label = Labels.objects.get(pk=pk)
#         # print(label)
#         #
#         # notes=CreateNotes.objects.get(pk=pk)
#         # print(notes)


#
# def addLabelOnNote(request):
#     if request.method == 'POST':
#
#         label_id = request.POST.get('label_id')
#         note_id = request.POST.get('note_id')
#         print(label_id)
#         print(note_id)
#
#         note = CreateNotes.objects.get(id=note_id)
#         print(note)
#         label = Labels.objects.get(id=label_id)
#
#         maplabel=MapLabel.objects.filter(note_id=note,label_id=label)
#         print(maplabel)
#         if len(maplabel) == 0:
#             obj = MapLabel(note_id=note, label_id=label)
#             obj.save()
#
#         return redirect('readallnotes')
#     return render(request,'notes/create-note.html')

class addLabelOnNote(APIView):

    def post(self,request,pk):
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            note = CreateNotes.objects.get(pk=pk)
            print("**********", note)

            id = request.POST.get('id')
            label = Labels.objects.get(id=id)
            # label_name = request.POST.get('label_name')
            # print("------------", label_name)
            print("------------", id)
            # label=Labels.objects.get(pk=pk)

            print("**********", label)
            print("**********", label)
            maplabel = MapLabel.objects.filter(note_id=note, label_id=label)
            print("dfgdfgdfg", maplabel)
            # print("dfdsfdsfff",note_id)
            if len(maplabel) == 0:
                obj = MapLabel(note_id=note, label_id=label)
                obj.save()

                res['data'] = note.id  # message of passing data in a SMD format
                res['message'] = 'Labels are added to a particular note'
                res['success'] = True
                return Response(res, status=status.HTTP_201_CREATED)

            else:
                res['message'] = 'Unssucess'  # Something wrong
                res['success'] = False

                # in response return data in json format
                return Response(res, status=status.HTTP_201_CREATED)

        except CreateNotes.DoesNotExist:
            print('Note doenst exists')
            res['message'] = 'Note doesnt exists'
            return Response(res, status=404)

        except Exception as e:
            print(e)
            return Response(res, status=404)

#
class getLabelOnNotes(APIView):
    def post(self,request):
        label_id = request.POST.get('label_id')
        label = MapLabel.objects.filter(label_id=label_id)  # Filter down a queryset based on a model's
        print("fdsf", label)

        return JsonResponse({'label': list(label)})

        # return JsonResponse(label,status=200)
        # Jsondata={
        #     'label': label
        # }
        # # return Jsondata(dumps,status=200)
        # dump = json.dumps(Jsondata)
        # return HttpResponse(dump, content_type="application/json")
        #



#


# ***************************************************************************************************


def showarchive(request):  # Archive Show
    res = {}
    notes = CreateNotes.objects.all().order_by('-created_time')  # Sort the Notes according to the time
    try:
        if notes is not None:
            return render(request, 'notes/index1.html', {'notes': notes})

    except notes.DoesNotExist:
        res['message'] = "No Notes in Archive"
        # res['success']=False
    except Exception as e:
        print(e)
        return HttpResponse(res, status=404)


def trash(request):
    res = {}
    notes = CreateNotes.objects.all().order_by('-created_time')
    try:
        if notes is not None:
            return render(request, 'notes/trash.html', {'notes': notes})
        else:
            return HttpResponse("Trash is Empty")
    except Exception as e:
        res['message'] = "No Notes in Trash"
        # res['success']=False
        print(e)
        return HttpResponse(res, status=404)


def showpinned(request):
    res = {}
    notes = CreateNotes.objects.all().order_by('-created_time')
    try:
        if notes is not None:
            return render(request, 'notes/pinned.html', {'notes': notes})
    except Exception as e:
        res['message'] = "No Pinned Notes"
        # res['success'] = False
        print(e)
        return HttpResponse(res, status=404)


def showlabels(request):
    res = {}
    labels = Labels.objects.all().order_by('-created_time')
    try:
        if labels is not None:
            return render(request, 'notes/showlabels.html', {'labels': labels})
    except Exception as e:
        res['message'] = "No Labels Notes"
        # res['success'] = False
        print(e)
        return HttpResponse(res, status=404)


def table(request):  # Display the contents of the tables using a Jinga Template
    notes = CreateNotes.objects.all().order_by('-created_time')  # Sort the Notes according to the time
    # pin = notes.is_pinned

    return render(request, 'notes/index.html', {'notes': notes})


class PostListAPIView(generics.ListAPIView):  # Viweing the ListAPI Views that
    serializer_class = PageNoteSerializer  # Assigning a Notes serializers fields in a Serializer class
    filter_backends = [SearchFilter, OrderingFilter]
    # search_fields=['title','description']
    pagination_class = PostPageNumberPagination  # Create our own limit of records in a pages

    def get_queryset(self, *args, **kwargs):  # Method for a itrerating of pages
        query_list = CreateNotes.objects.filter().order_by('-created_time')  # Filter down a queryset based on a model's
        # fields, displaying the form to let them do this.

        return query_list


def pratice(request):
    # notes=CreateNotes.objects.all()
    a = 10, 20
    d = [1, 2, 3, 4, 5, 6, 'Hello', 'Shahazad']
    return render(request, 'notes/pratice.html', {'d': d}, {'a', a})

#
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
#
# class MySampleView(APIView):
#     permission_classes = (IsAuthenticated,)
#
# def get(self, request):
#     return Response(data={"status": True})
