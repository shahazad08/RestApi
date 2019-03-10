import json
import jwt
from django.views.decorators.http import require_POST
from rest_framework.filters import OrderingFilter
from django.shortcuts import render
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import resolve
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect
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
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView  # Used for a create-only endpoints, provides a post method handler
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework.views import APIView  # Taking the views of REST framework Request & Response
from django.contrib.auth import logout
from .tokens import account_activation_token
from django.urls import reverse
from .forms import SignupForm
from .serializers import NoteSerializer, ReadNoteSerializer, PageNoteSerializer
from rest_framework.decorators import api_view
from .models import User, CreateNotes, Labels, MapLabel
from django.conf import settings
from .upload import upload_profilenew
from rest_framework import generics  # For a List API use a generics
from .paginate import PostLimitOffsetPagination, PostPageNumberPagination  # Creating our own no. of records in a Pages
from rest_framework.filters import SearchFilter  # it allows users to filter down a queryset based on a model's
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.core.cache.backends.base import DEFAULT_TIMEOUT  # Setting a time for a cache to store
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from .custom_decorators import custom_login_required
from django.utils.decorators import method_decorator

def home(request):
    return render(request, "home.html", {})  # home page

def log_me(request):
    return render(request, 'user_login.html', {})

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
            return JsonResponse('Please confirm your email address to complete the registration',safe=False)
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

class Registerapi(CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        res = {"message": "something bad happened",
               "data": {},
               "success": False}
        print(request.data)
        email = request.data['email']
        print(email)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        # date_joined=request.data['date_joined']
        password = request.POST.get('password')

        if email and password is not "":
            user = User.object.create_user(email=email, first_name=first_name, last_name=last_name, password=password)
            print("******", email)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            message = render_to_string('activate.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your account...'
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            res['message'] = "registered Successfully...Please activate your Account"
            res['success'] = True
            return JsonResponse(res)
        else:
            # res['message'] = "Account allready exists"
            # res['success'] = True
            return JsonResponse(res)

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))  # UserId for a decoding
        user = User.object.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):  # if its a valid token
        user.is_active = True  # User is Active
        user.save()
        return render(request, 'user_login.html')
    else:
        return HttpResponse('Activation link is invalid!')

@api_view(['POST'])
@require_POST
def logins(request):
    res = {}
    res['message'] = 'Something bad happend'
    res['success'] = False

    print('**********************************loginsssss***************************')
    try:
        email = request.POST.get('email')  # Get Email
        password = request.POST.get('password')  # Get Password
        if email is None:
            raise Exception("Email is required")
        if password is None:
            raise Exception("Password is required")
        user = authenticate(email=email, password=password)
        print("User Name", user)
        if user:  # If it is a User
            if user.is_active:  # If a User is active
                login(request, user)  # Login maintains a request and a user
                try:
                    return render(request, 'profile.html')  # After Sucessfull returns to the profile page
                except Exception as e:  # Invalid
                    result = {'error1': 'please provide an valid email and a password'}
                    return JsonResponse(result)
            else:
                res['message'] = "User is Inactive"
                return JsonResponse(res)
        else:
            res['message'] = 'Username or Password is not correct'  # Invalid login details
            messages.error(request, 'Invalid login details')
            return JsonResponse(res)
    except Exception as e:
        print(e)

#/********************************Authorization Header*********************************************************
def authorize(request):
    print(request.META.get('HTTP_AUTHORIZATION'))
    token = request.META.get('HTTP_AUTHORIZATION')
    token_split = token.split(' ')
    token_get = token_split[1]
    print("My Token:", token_get)

    token_decode = jwt.decode(token_get, "secret_key", algorithms=['HS256'])
    eid = token_decode.get('email')
    user_id = User.object.get(email=eid)
    print("Email", eid)
    print ("User id", user_id.id)
    print(token_decode)
    return user_id.id

#/***********************************************************************************************
def exit(request):  # For a Logout
    # logout(request)
    return render(request, "home.html")

def upload1(request):
    upload_profilenew(file, name)


class createnotes(APIView):
    @method_decorator(custom_login_required)
    def dispatch(self,request):
        res={}
        auth_user=request.user.id
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            color = request.POST.get('color')
            label = request.POST.get('label')
            collaborate = request.POST.get('collaborate')
            notes = CreateNotes(title=title, description=description, color=color, label=label, user_id=auth_user)
            print('***Notes****', notes)
            if title != "" and description != "":
                notes.save()
                res['message'] = 'Notes are added in a database'
                res['success'] = True
                res['data'] = notes.id
                return JsonResponse(res, status=200)
            if collaborate != "":
                print("ff", notes.collaborate.add(auth_user))
                notes.save()
                res['message'] = 'Unssucesss'
                res['success'] = False
                return JsonResponse(res, status=204)
        except Exception as e:
            res['message'] = 'Unssucess'
            return JsonResponse(res, status=204)

class create(APIView):      # Create Note Using Serializer
    serializer_class = NoteSerializer
    ''' title=title,
        description=description
        '''
    def post(self, request):
        res = {}
        res['message'] = 'Something added'
        res['success'] = True
        try:
            serializer = NoteSerializer(data=request.data)
            print(serializer)
            if serializer.is_valid():
                serializer.save()
                res['data'] = serializer.data
                res['message'] = 'Notes are added in a database'
                res['success'] = True
                return JsonResponse(res, status=200)
            else:
                res['message'] = 'Unssucesss'
                res['success'] = False
                return JsonResponse(res, status=204)
        except Exception as e:
            print(e)

# @custom_login_required
# def createcollaborator(request, pk):  # get the require pk
#     a_user = authorize(request)
#     res = {}
#     res['message'] = 'Bad Happend'
#     res['success'] = False
#     try:
#         if pk:
#             note = CreateNotes.objects.get(pk=pk)  # get the required id of a note
#             print('------------------------', note)
#             note_user = note.user.id  # Get the Note User ID
#             note_id=note.id
#             print("NI",note_id)
#             print("Note User ID", note_user)
#             collaborate = request.POST.get('collaborate')  # Accept a id of a new user
#             print(collaborate)
#             user = User.object.get(id=collaborate)  # get the details of a user through id
#             values = CreateNotes.collaborate.through.objects.filter(
#                 user_id=a_user).values()  # display the users which are collaborated with the users
#             val=CreateNotes.collaborate.through.objects.filter(createnotes_id=note.id,user_id=user.id).values()
#             print("bl", val)
#             print('values', values)
#
#             if note_user == user.id: # If note user_id and collaborate user is same
#                 res['message'] = 'Cannot Collaborate to the same User'
#                 res['success'] = False
#                 return JsonResponse(res, status=404)
#             elif CreateNotes.collaborate.through.objects.filter(user_id=user.id, createnotes_id=note.id): # Checking of a same user id and create note id for as if its exist user or not
#                 res['message'] = 'User Allready Exists'
#                 res['success'] = False
#                 return JsonResponse(res,status=404)
#             else:
#                 print("user", user.id)
#                 note.collaborate.add(user)  # adds the user to the note
#                 note.save()  # save the note
#                 res['message'] = 'Success'
#                 res['success'] = True
#                 res['data'] = note.id
#                 # print("sss", exist)
#                 return JsonResponse(res, status=200)
#     except Exception as e:
#         print('User doent exists')
#         res['message'] = 'User doesnt exists'
#         print(e)
#         return JsonResponse(res, status=404)





class createcollaborator(APIView):
    @method_decorator(custom_login_required)
    def dispatch(self,request):  # get the require pk
        a_user = request.user
        res = {}
        res['message'] = 'Bad Happend'
        res['success'] = False
        try:
            id=request.POST.get('id')
            if id:
                note = CreateNotes.objects.get(pk=id)  # get the required id of a note
                print('------------------------', note)
                note_user = note.user.id  # Get the Note User ID
                note_id = note.id
                print("NI", note_id)
                print("Note User ID", note_user)
                collaborate = request.POST.get('collaborate')  # Accept a id of a new user
                print(collaborate)
                user = User.object.get(id=collaborate)  # get the details of a user through id
                values = CreateNotes.collaborate.through.objects.filter(
                    user_id=a_user).values()  # display the users which are collaborated with the users
                val = CreateNotes.collaborate.through.objects.filter(createnotes_id=note.id, user_id=user.id).values()
                print("bl", val)
                print('values', values)

                if note_user == user.id:  # If note user_id and collaborate user is same
                    res['message'] = 'Cannot Collaborate to the same User'
                    res['success'] = False
                    return JsonResponse(res, status=404)
                elif CreateNotes.collaborate.through.objects.filter(user_id=user.id,
                                                                    createnotes_id=note.id):  # Checking of a same user id and create note id for as if its exist user or not
                    res['message'] = 'User Allready Exists'
                    res['success'] = False
                    return JsonResponse(res, status=404)
                else:
                    print("user", user.id)
                    note.collaborate.add(user)  # adds the user to the note
                    note.save()  # save the note
                    res['message'] = 'Success'
                    res['success'] = True
                    res['data'] = note.id
                    # print("sss", exist)
                    return JsonResponse(res, status=200)
        except Exception as e:
            print('User doent exists')
            res['message'] = 'User doesnt exists'
            print(e)
            return JsonResponse(res, status=404)



#
# @custom_login_required
# def deletecollaborator(request,pk):
#     res = {}
#     res['message'] = 'User Not Exist'
#     res['success'] = False
#     try:
#         if pk:
#             note = CreateNotes.objects.get(pk=pk)  # get the required id of a note
#             print('------------------------', note)
#             auth_user = note.user.id # Use vairable b as a Note User
#             collaborate = request.POST.get('collaborate')  # Accept a id of a new user
#             print(collaborate)
#             user = User.object.get(id=collaborate)  # get the details of a user through id
#             if auth_user == user.id:
#                 res['message'] = 'Cannot Collaborate to the same User'
#                 res['success'] = False
#                 return JsonResponse(res, status=400)
#             else:
#                 res['message'] = 'Success'
#                 res['success'] = True
#                 res['data'] = note.id
#                 note.collaborate.remove(user)  # adds the user to the note
#                 note.save()
#                 return JsonResponse(res, status=200)
#     except CreateNotes.DoesNotExist:  # if user not exists
#         print('User doent exists')
#         res['message'] = 'User doesnt exists'
#         return JsonResponse(res, status=404)

class deletecollaborator(APIView):
    @method_decorator(custom_login_required)
    def dispatch(self,request, pk):
        # auth_user=request.user.id
        res = {}
        res['message'] = 'User Not Exist'
        res['success'] = False
        try:
            if pk:
                note = CreateNotes.objects.get(pk=pk)  # get the required id of a note
                print('------------------------', note)
                auth_user = note.user.id  # Use vairable b as a Note User
                collaborate = request.POST.get('collaborate')  # Accept a id of a new user
                print(collaborate)
                user = User.object.get(id=collaborate)  # get the details of a user through id
                if auth_user == user.id:
                    res['message'] = 'Cannot Collaborate to the same User'
                    res['success'] = False
                    return JsonResponse(res, status=400)
                else:
                    res['message'] = 'Success'
                    res['success'] = True
                    res['data'] = note.id
                    note.collaborate.remove(user)  # adds the user to the note
                    note.save()
                    return JsonResponse(res, status=200)
        except Exception as e:  # if user not exists
            print('User doent exists')
            res['message'] = 'User doesnt exists'
            return JsonResponse(res, status=404)


# @custom_login_required
# def checking_decorator(request):
#     return JsonResponse("Works")

# @custom_login_required
# def getnote(request):
#     res = {}
#     a_user = authorize(request)
#     try:
#         if a_user:
#             read_notes = CreateNotes.objects.filter(user=a_user).values()  # display the notes of a particular user
#             print("****", read_notes)
#             values = CreateNotes.collaborate.through.objects.filter(user_id=a_user).values()  # display the users which are collaborated with the users
#             print("Values", values)
#             collab = []  # blank collaborator array
#             for i in values:  # assigned the values in i which are collaborated with the  particular user
#                 collab.append(i['createnotes_id'])  # append with respect to the note id
#             collab_notes = CreateNotes.objects.filter(id__in=collab).values().order_by('-created_time')  # id__in indicates to take all the values
#             print("collab Notes -------------", collab_notes)
#             merged = read_notes | collab_notes  # as to merging the 2 query sets into one
#             print("***", merged)
#             l = []  # Converting the query sets to a json format
#             for i in merged:
#                 l.append(i)
#             return JsonResponse(l, safe=False)
#         else:
#             res['message'] = "Invalid User"
#             res['sucess'] = False
#             return JsonResponse(res, status=404)
#     except Exception as e:
#         res['message']="User Not Exist"
#         res['sucess']=False
#         return JsonResponse(res, status=404)




class getnote(APIView):
    @method_decorator(custom_login_required)
    def dispatch(self,request):
        res = {}
        a_user = request.user.id
        try:
            if a_user:
                read_notes = CreateNotes.objects.filter(user=a_user).values()  # display the notes of a particular user
                print("****", read_notes)
                values = CreateNotes.collaborate.through.objects.filter(
                    user_id=a_user).values()  # display the users which are collaborated with the users
                print("Values", values)
                collab = []  # blank collaborator array
                for i in values:  # assigned the values in i which are collaborated with the  particular user
                    collab.append(i['createnotes_id'])  # append with respect to the note id
                collab_notes = CreateNotes.objects.filter(id__in=collab).values().order_by(
                    '-created_time')  # id__in indicates to take all the values
                print("collab Notes -------------", collab_notes)
                merged = read_notes | collab_notes  # as to merging the 2 query sets into one
                print("***", merged)
                l = []  # Converting the query sets to a json format
                for i in merged:
                    l.append(i)
                return JsonResponse(l, safe=False)
            else:
                res['message'] = "Invalid User"
                res['sucess'] = False
                return JsonResponse(res, status=404)
        except Exception as e:
            res['message'] = "User Not Exist"
            res['sucess'] = False
            return JsonResponse(res, status=404)




class deletenote(APIView):  # Delete a Note
    """
    Retrieve, update or delete a event instance.
    """
    """
    """
    @method_decorator(custom_login_required)
    def dispatch(self,request,*args, **kwargs):
        print("dsf",request.user)
        auth_user=request.user.id
        print("Authentication User",auth_user)
        res = {}
        res['data'] = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id=request.POST.get('id')
            if id:
                note = CreateNotes.objects.get(pk=id)  # get requested id from a Note
                note_user=note.user.id
                print("Note User", note_user)
                if auth_user==note_user:
                    if note.trash == False:  # if trash is false, change to true
                        note.trash = True
                        note.save()  # save in a db
                        res['data'] = note.id
                        res['message'] = 'Note has been moved to trash'
                        res['success'] = True
                        return JsonResponse(res, status=status.HTTP_201_CREATED)  # Display the data
                    else:
                        note.is_deleted = True  # if is_deleted is true
                        note.delete()  # delete it
                        res['data'] = note.id
                        res['message'] = 'Note has been deleted from trash'
                        res['success'] = True
                        return JsonResponse(res, status=status.HTTP_201_CREATED)  # Display the data
                else:
                    res['message'] = 'Invalid User'
                    res['success'] = False
                    return JsonResponse(res, status=status.HTTP_201_CREATED)
        except Exception as e:
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            res['success'] = False
            return JsonResponse(res, status=404)


class restorenote(APIView):
    @method_decorator(custom_login_required)
    def dispatch(self, request):
        auth_user = request.user.id
        print("Authentication User", auth_user)
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id = request.POST.get('id')
            if id:
                note = CreateNotes.objects.get(pk=id)
                note_user = note.user.id
                print("Note User", note_user)
                if auth_user==note_user:
                    if note.trash == True:
                        note.trash = False
                        note.save()
                        res['message'] = "Selected Note has been Restored"
                        res['success'] = True
                        res['data'] = note.id
                        return JsonResponse(res, status=204)
                    else:
                        res['message'] = 'Unable to find Note. Missing Note ID'
                        return JsonResponse(res, status=200)
                else:
                    res['message'] = "Invalid User"
                    res['success'] = False
                    return JsonResponse(res, status=204)
        except CreateNotes.DoesNotExist:
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)



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
                return JsonResponse(res, status=status.HTTP_201_CREATED)
            # else return error msg in response
        except CreateNotes.DoesNotExist:
            print('Note doenst exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)

        except Exception as e:
            print(e)
            return JsonResponse(res, status=404)



class archivenote(APIView):  # Delete a Note
    """
    Retrieve, update or delete a event instance.
    """

    @method_decorator(custom_login_required)
    def dispatch(self, request):
        auth_user=request.user.id
        res = {}
        res['data'] = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id=request.POST.get('id')
            if id:
                note = CreateNotes.objects.get(pk=id)  # get particular note from a id
                note_user=note.user.id
                if auth_user==note_user:
                    if note.is_archived == False:  # if archived is false, change it to true, as to move in a archived
                        note.is_archived = True
                        note.save()  # save in a db
                        res['message'] = "Selected Note has been moved to Archive"
                        res['success'] = True
                        res['data'] = note.id
                        return JsonResponse(res, status=204)  # return result
                    else:
                        note.is_archived = False
                        note.save()
                        res['message'] = "Note has been moved to Dashboard"
                        res['success'] = False
                        res['data'] = note.id
                        return JsonResponse(res, status=204)
                else:
                    res['message'] = "Invalid User"
                    res['success'] = False
                    return JsonResponse(res, status=204)


        except CreateNotes.DoesNotExist:  # catch the exception as if the note exists
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)



class colornote(APIView):  # Delete a Note
    """
    Retrieve, update or delete a event instance.
    """
    @method_decorator(custom_login_required)
    def dispatch(self, request):
        auth_user = request.user.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id = request.POST.get('id')
            if id:
                note = CreateNotes.objects.get(pk=id)
                note_user=note.user.id
                if auth_user==note_user:
                    note.color = request.POST.get('color')  # request the color from notes model, for change
                    note.save()  # save to db
                    res['message'] = "Color has been Changed."  # message for change color
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=204)  # return result

                else:
                    res['message'] = "Invalid User"  # message for change color
                    res['success'] = False
                    return JsonResponse(res, status=204)  # return result
            else:
                res['message'] = 'Unable to find Note. Missing Note ID'  # missing id
                return JsonResponse(res, status=200)  # return res

        except CreateNotes.DoesNotExist:
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'  # message if note doesnot exists
            return JsonResponse(res, status=404)


class ispinned(APIView):  # Delete a Note
    """
    Retrieve, update or delete a event instance.
    """
    @method_decorator(custom_login_required)
    def dispatch(self, request):
        auth_user=request.user.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id=request.POST.get('id')
            if id:
                note = CreateNotes.objects.get(pk=id)  # get a requested pk
                note_user=note.user.id
                if auth_user==note_user:
                    if note.is_pinned == False:  # if not pinned
                        note.is_pinned = True  # change it to pin
                        note.save()  # save in a db
                        res['message'] = "Notes has been Pinned to Top."  # message in a SMD format
                        res['success'] = True
                        res['data'] = note.id
                        return JsonResponse(res, status=200)
                    else:
                        note.is_pinned = False  # if not pinned, save as it is
                        note.save()
                        res['message'] = "Notes has been Move to Unpinned"
                        res['success'] = False
                        res['data'] = note.id
                        return JsonResponse(res, status=204)
                else:
                    res['message'] = "Invalid User"
                    res['success'] = False
                    return JsonResponse(res, status=404)
            else:
                res['message'] = 'Unable to find Note. Missing Note ID'  # message for a missing id
                return JsonResponse(res, status=404)
        except CreateNotes.DoesNotExist:  # catch exception if note doesnt exists
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)


class copynote(APIView):

    @method_decorator(custom_login_required)
    def dispatch(self, request):
        auth_user=request.user.id
        res = {}        # get note with given id
        # res['data'] = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            id=request.POST.get('id')
            if id:
                note = CreateNotes.objects.get(pk=id) # Accept a note pk
                note_user=note.user.id
                print("NI",note.id)
                if auth_user==note_user:
                    note.id = None  # create pk as a none
                    note.save()
                    res['message'] = "Note is Coped "
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=204)
                else:
                    res['message'] = 'Unable to find Note. Missing Note ID'
                    res['success'] = False
                    return JsonResponse(res, status=404)
            else:
                res['message'] = 'Invalid User'
                res['success'] = False
                return JsonResponse(res, status=404)
        except CreateNotes.DoesNotExist:
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)
        except Exception as e:
            print(e)
            return JsonResponse(res, status=404)


@custom_login_required
def create_label(request):
    a_user = request.user_id.id
    res = {}
    res['message'] = 'Something bad happend'
    res['success'] = True
    try:
        label_name = request.POST.get('label_name')
        labels = Labels(label_name=label_name, user_id=a_user)
        note_user = labels.user_id
        print("Note",note_user)
        if a_user==note_user:
            print('-------', labels)
            if label_name != "":
                labels.save()
                res['data'] = labels.id
                res['message'] = 'Labels are added in a database'
                res['success'] = True
                return JsonResponse(res, status=200)
            else:
                res['message'] = 'Unssucess'
                res['success'] = False  # in response return data in json format
                return JsonResponse(res, status=400)
        else:
            res['message'] = 'Invalid User'
            res['success'] = False  # in response return data in json format
            return JsonResponse(res, status=204)
    except Exception as e:
        res['message'] = 'Unssucess'
        res['success'] = False  # in response return data in json format
        return JsonResponse(res, status=404)


@custom_login_required
def deletelabel(request,pk):  # Delete a Note
    a_user=request.user_id.id
    res = {}
    print('test user', request.user_id  )
    # res['data'] = {}
    res['message'] = 'Something bad happened'
    res['success'] = False
    try:
        if pk:
            label = Labels.objects.get(pk=pk)  # get requested id from a Labels
            user=label.user_id
            if a_user==user:
                res['data'] = label.id
                label.delete()
                res['message'] = "Label has been deleted"
                res['success'] = True
                return JsonResponse(res, status=200)  # Display the data
            else:
                res['message'] = "Invalid User"
                res['success'] = False
                return JsonResponse(res, status=200)  # Display the data
        else:
            res['message'] = 'Unsuccess'
            res['success'] = False
            return JsonResponse(res, status=status.HTTP_201_CREATED)  # Display the data
    except Exception as e:
        print('Label doesnt exists')
        res['message'] = 'Label doesnt exists'
        res['success'] = False
        return JsonResponse(res, status=404)


class updatelabel(APIView):  # Update a Note
    @method_decorator(custom_login_required)
    def dispatch(self, request, pk):  # get all the labels of given requested id(pk)
        auth_user=request.user.id
        print("au",auth_user)
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk:
                label = Labels.objects.get(pk=pk)
                label_user=label.user_id
                print("ds",label_user)
                if auth_user==label_user:
                    serializer = LabelSerializer(label, data=request.data)
        # check serialized data is valid or not
                    if serializer.is_valid():
                        # if valid then save it
                        serializer.save()
                        res['data'] = serializer.data  # message of passing data in a SMD format
                        res['message'] = 'Labels are Updated in a database'
                        res['success'] = True
                        return JsonResponse(res, status=status.HTTP_201_CREATED)
            # in response return data in json format

                    else:
                        res['message'] = 'Unssucess'  # Something wrong
                        res['success'] = False
    # in response return data in json format
                        return Response(res, status=status.HTTP_201_CREATED)

                else:
                    res['message'] = 'Invalid User'  # Something wrong
                    res['success'] = False
        # in response return data in json format
                    return Response(res, status=status.HTTP_201_CREATED)

    # else return error msg in response

        except CreateNotes.DoesNotExist:
            print('Note doenst exists')
            res['message'] = 'Note doesnt exists'
            return Response(res, status=404)
# except Exception as e:
# print(e)
# return Response(res, status=404)



# class updatelabel(APIView):  # Update a Note
#     @method_decorator(custom_login_required)
#     def dispatch(self, request):  # get all the labels of given requested id(pk)
#         auth_user=request.user.id
#         print('au',auth_user)
#         res = {}
#         res['message'] = 'Something bad happened'
#         res['success'] = False
#         try:
#             id=request.POST.get('id')
#             if id:
#                 label = Labels.objects.get(pk=id)
#                 print("lm",label.label_name)
#                 # label_user=label.user_id
#                 user = label.user_id
#                 print("u",user)
#                 # print("lu",label_user)
#                 if auth_user == user:
#                     label.label_name = request.POST.get('label_name')
#                     if label.label_name != "":
#                         label.id=label_name
#                         print("koko",label.id.label_name)
#                         print("Ser",label_name)
#                         print("li",label.id)
#                         label.save()
#                         res['message'] = 'Labels are Updated in a database'
#                         res['success'] = True
#                         return JsonResponse(res, status=status.HTTP_201_CREATED)
#                     else:
#                         res['message'] = 'Unssucess'  # Something wrong
#                         res['success'] = False
#                         return JsonResponse(res, status=status.HTTP_201_CREATED)
#                 else:
#                     res['message'] = 'Invalid User'  # Something wrong
#                     res['success'] = False
#                     return JsonResponse(res, status=status.HTTP_201_CREATED)
#             else:
#                 res['message'] = 'Missing ID'  # Something wrong
#                 res['success'] = False
#                 return JsonResponse(res, status=status.HTTP_201_CREATED)
#
#         except CreateNotes.DoesNotExist:
#             print('Note doenst exists')
#             res['message'] = 'Note doesnt exists'
#             return JsonResponse(res, status=404)
#
#         except Exception as e:
#             print(e)
#             return JsonResponse(res, status=404)
#



# class addLabelOnNote(APIView):
#     @method_decorator(custom_login_required)
#     def dispatch(self, request, pk):
#         res = {}
#         res['message'] = 'Something bad happened'
#         res['success'] = False
#         try:
#             if pk:
#                 note = CreateNotes.objects.get(pk=pk)  # reterieve the pk of a particular note
#                 id = request.POST.get('id')  # reterive the id of a particular label
#                 label = Labels.objects.get(id=id)
#                 print("**********", label)
#                 maplabel = MapLabel.objects.filter(note_id=note, label_id=label)  # filter the note and label
#                 print("....", maplabel)
#                 if len(maplabel) == 0:  # if maplabel field is empty
#                     obj = MapLabel(note_id=note, label_id=label)  # assigned the notes and a label using model by creating the oject
#                     obj.save()  # save the object
#                     res['data'] = note.id  # message of passing data in a SMD format
#                     res['message'] = 'Labels are added to a particular note'
#                     res['success'] = True
#                     return JsonResponse(res, status=status.HTTP_201_CREATED)
#             else:
#                 res['message'] = 'Unssucess'  # Something wrong
#                 res['success'] = False
#                 # in response return data in json format
#                 return JsonResponse(res, status=status.HTTP_201_CREATED)
#         except CreateNotes.DoesNotExist:
#             print('Note doenst exists')
#             res['message'] = 'Note doesnt exists'
#             return JsonResponse(res, status=404)
#         except Exception as e:
#             print(e)
#             return JsonResponse(res, status=404)



class addLabelOnNote(APIView):
    @method_decorator(custom_login_required)
    def dispatch(self, request, pk):
        auth_user=request.user.id
        print("au",auth_user)
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk:
                note = CreateNotes.objects.get(pk=pk)  # reterieve the pk of a particular note
                note_user=note.user.id
                print("nu",note_user)
                if auth_user==note_user:
                    id = request.POST.get('id')  # reterive the id of a particular label
                    label = Labels.objects.get(id=id)
                    print("**********", label)
                    maplabel = MapLabel.objects.filter(note_id=note, label_id=label)  # filter the note and label
                    print("....", maplabel)
                    if len(maplabel) == 0:  # if maplabel field is empty
                        obj = MapLabel(note_id=note,
                           label_id=label)  # assigned the notes and a label using model by creating the oject
                        obj.save()  # save the object
                        res['data'] = note.id  # message of passing data in a SMD format
                        res['message'] = 'Labels are added to a particular note'
                        res['success'] = True
                        return JsonResponse(res, status=status.HTTP_201_CREATED)
                    else:
                        res['message'] = 'Unssucess'  # Something wrong
                        res['success'] = False
                        return JsonResponse(res, status=status.HTTP_201_CREATED)
                else:
                    res['message'] = 'Invalid User'  # Something wrong
                    res['success'] = False
                    return JsonResponse(res, status=status.HTTP_201_CREATED)

        except CreateNotes.DoesNotExist:
            print('Note doenst exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)
# except Exception as e:
# print(e)
# return JsonResponse(res, status=404)


class getLabelOnNotes(APIView):
    @method_decorator(custom_login_required)
    def dispatch(self, request):
        auth_user = request.user.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            label_id = request.POST.get('label_id')
            label = MapLabel.objects.filter(label_id=label_id).values()  # Filter down a queryset based on a model's
            print("fdsf", label)
            note_obj = CreateNotes.objects.filter(id=id)
            return JsonResponse({'label': label})
        except Exception as e:
            print(e)


class removeLabelonNote(APIView):
    @method_decorator(custom_login_required)
    def dispatch(self, request, pk):
        auth_user = request.user.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk:
                note = CreateNotes.objects.get(pk=pk)  # reterieve the pk of a particular note
                note_user = note.user.id
                print("**********", note)
                if auth_user == note_user:
                    id = request.POST.get('id')  # reterive the id of a particular label
                    label = Labels.objects.get(id=id)
                    print("------------", id)
                    print("**********", label)
                    maplabel = MapLabel.objects.filter(note_id=note, label_id=label)  # filter the note and label
                    print("....", maplabel)
                    res['data'] = note.id
                    maplabel.delete()
        # message of passing data in a SMD format
                    res['message'] = 'Labels are remove to a requested note'
                    res['success'] = True
                    return JsonResponse(res, status=status.HTTP_201_CREATED)

                else:
                    res['message'] = 'No Notes'
                    res['success'] = False
                    return JsonResponse(res, status=status.HTTP_201_CREATED)

            else:
                res['message'] = 'Invalid User'  # Something wrong
                res['success'] = False
                return JsonResponse(res, status=status.HTTP_201_CREATED)

        except CreateNotes.DoesNotExist:
            print('Note doenst exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)

        except Exception as e:
            print(e)
            return JsonResponse(res, status=404)

# ***************************************************************************************************


def showarchive(request):  # Archive Show
    res = {}
    notes = CreateNotes.objects.all().order_by('-created_time')  # Sort the Notes according to the time
    try:
        if notes:
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
        if notes:
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
        if labels:
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
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False

        try:
            query_list = CreateNotes.objects.filter().order_by(
                '-created_time')  # Filter down a queryset based on a model's
            # fields, displaying the form to let them do this.
            return query_list
        except Exception as e:
            res['message'] = 'Empty'
            res['success'] = False

            return JsonResponse(res, status=404)

class remainder(APIView):
    def post(self,request):
        auth_user=authorize(request)
        try:
            if auth_user:
                print("user",auth_user)  # if request made from User.
                remainder_col = CreateNotes.objects.filter(user=auth_user).values()  # Gets all notes  for particular user.
                print("rv",remainder_col)
                dates = []  # list to store only dates of every Note.
                for i in remainder_col:
                    if i['remainder']:  # if reminder column has some value
                        # convert and append the date to the list
                        dates.append(datetime.datetime.strptime(i['remainder'], "%Y-%m-%d"))
                j = datetime.datetime.today()  # stores today's date
                remind_dates = []  # list to store the dates for which reminder is in 5 days.
                for i in dates:
                    if (i - j).days <= 5:  # calculates the difference and stores the value to list
                        remind_dates.append(i)
                print("RM",remind_dates)
                new_list = []  # list elements has some unwanted values and in Str format
                for i in remind_dates:
                    i = datetime.datetime.strftime(i, "%Y-%m-%d")
                    i = i[:10]  # convert and slice to remove unwanted details
                    new_list.append(i)
                data = CreateNotes.objects.filter(user=request.user, reminder__in=new_list).values('title', 'remainder')
                json_list = []  # get all notes with reminder # QuerySet to JSON
                for i in data:
                    json_list.append(i)
                return JsonResponse(json_list, safe=False)
            else:
                res['message'] = 'Unsuccess'
                res['success'] = False
                return JsonResponse(res,status=204)
        except Exception:
            res['message'] = 'Not Found'
            res['success'] = False
            return JsonResponse(res,status=404)

# @custom_login_required
def get_all_notes(request):
    element=request.POST.get('email')
    print(element)
    ele=request.POST['id']
    print('Elements',ele)
    items= CreateNotes.objects.filter(pk=ele).values()
    print(items)
    auth_user = authorize(request)
    print("User Got it",auth_user)
    return HttpResponse(items)



def apilogin(request):
    res = {}
    res['message'] = 'Something bad happend'
    res['success'] = False

    print('**********************************API Login***************************')
    try:
        email = request.POST.get('email')  # Get Email
        password = request.POST.get('password')  # Get Password
        if email is None:
            raise Exception("Email is required")
        if password is None:
            raise Exception("Password is required")
        user = authenticate(email=email, password=password)
        print("User Name", user)
        if user:  # If it is a User
            if user.is_active:  # If a User is active
                login(request, user)  # Login maintains a request and a user
                try:  # The claims in a JWT are encoded as a JSON object that is digitally signed using
                    # JSON Web Signature (JWS) and/or encrypted using JSON Web Encryption (JWE)
                    payload = {
                        # 'id': User.id,
                        'email': email,
                        'password': password,
                    }
                    token_encode = jwt.encode(payload, "secret_key", algorithm='HS256').decode('utf-8')
                    res['message'] = "Login Sucessfull"
                    res['success'] = True
                    res['data'] = token_encode
                    return JsonResponse(res, status=status.HTTP_201_CREATED)
                except Exception as e:  # Invalid
                    result = {'error1': 'please provide an valid email and a password'}
                    return JsonResponse(result)
            else:
                res['message'] = "User is Inactive"
                return JsonResponse(res)
        else:
            res['message'] = 'Username or Password is not correct'  # Invalid login details
            messages.error(request, 'Invalid login details')
            return JsonResponse(res)
    except Exception as e:
        print(e)


