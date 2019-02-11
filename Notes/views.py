# from django.shortcuts import render
#
# # Create your views here.
# from rest_framework.generics import CreateAPIView
# from .serializers import Notes
# from rest_framework.response import Response
#
# # from django_auth.Notes.models import Notes
# from django_auth.Notes.serializers import CreateNoteSerializer, ReadNoteSerializer, UpdateNoteSerializer, \
#     DeleteNoteSerializer
# from .models import Notes
#
#
#
#
# #     serializer = UserSerializer(data=user)
# #     serializer.is_valid(raise_exception=True)
# #     serializer.save()
# #     return Response(serializer.data, status=status.HTTP_201_CREATED)
#
# class CreateUserAPIView(CreateAPIView):
#     serializer_class = CreateNoteSerializer()
#     queryset = Notes.objects.all()
#
#
#
#     # def post(self,request):
#     #     serializer_class = CreateNoteSerializer(data=request.data)
#     #     queryset = Notes.objects.all()
#     #
#     #
#     #     if serializer_class.is_valid():
#     #         serializer_class.save()
#     #         return Response(serializer_class.data)
#
#
#
#
#
# class ReadSerializerView(CreateAPIView):
#     serializer_class = ReadNoteSerializer
#     queryset = Notes.objects.all()
#
# class UpdateSerializer(CreateAPIView):
#     serializer_class = UpdateNoteSerializer
#     queryset = Notes.objects.all()
#
# class DeleteSerializer(CreateAPIView):
#     serializer_class = DeleteNoteSerializer
#     queryset = Notes.objects.all()
#
#
#
#
#
#
#
#
#
#
#
#
#
