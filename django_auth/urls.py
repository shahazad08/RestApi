
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from rest_framework.decorators import api_view

admin.autodiscover()
# from rest_framework.urlpatterns import format_suffix_patterns
# from users import views
from users import views
from django.contrib import auth
urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # for a home page
    url(r'^$', views.signup),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate,
        name='activate'),

    url(r'^log_me/$', views.log_me, name='log_me'),
    path('log_user/', views.logins, name='log_user'),

    #    path('upload_profile/',views.upload_profile,name='upload_profile'),

    path('fileupload/', views.fileupload, name='fileupload'),
    path('upload_profilenew/', views.upload_profilenew, name='upload_profilenew'),
    path('upload/', views.upload, name='upload'),
    # upload_profile

    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin/', admin.site.urls),  # for a admin login

    path('logout/', views.exit, name='logout'),

    # *****************************Notes Urls********************************************

    path('createnote/', views.createnote.as_view(), name='createnote'),  # For Create
    path('readnote/<int:pk>/', views.readnote.as_view(), name='readnote'),  # Read
    path('deletenote/<int:pk>/', views.deletenote.as_view(), name='deletenote'),  # Delete with PK
    path('updatenote/<int:pk>/', views.updatenote.as_view(), name='updatenote'),  # Update with Pk
    path('archivenote/<int:pk>/', views.archivenote.as_view(), name='archivenote'),  # Update with Pk

    path('restorenote/<int:pk>/', views.restorenote.as_view(), name='restorenote'),  # Update with Pk
    path('colornote/<int:pk>/', views.colornote.as_view(), name='colornote'),  # Update with Pk
    path('ispinned/<int:pk>/', views.ispinned.as_view(), name='ispinned'),  # Update with Pk
    path('showpinned/', views.showpinned, name='showpinned'),  # Update with Pk

    path('copynote/<int:pk>/', views.copynote.as_view(), name='copynote'),  # Update with Pk

    path('table/', views.table, name='table'),  # Displays the Table data in a front view using jinga template

    path('showarchive/', views.showarchive, name='showarchive'),
    # Displays the Table data in a front view using jinga template
    path('trash/', views.trash, name='trash'),  # Displays the Table data in a front view using jinga template

    path('pratice/', views.pratice, name='pratice'),

    path('page/', views.PostListAPIView.as_view(), name='page'),  # Paginate



    path('create_label/', views.create_label.as_view(), name='create_label'),  # Createlabel

    path('deletelabel/<int:pk>/', views.deletelabel.as_view(), name='deletelabel'),  # Deletelabel

    path('updatelabel/<int:pk>/', views.updatelabel.as_view(), name='updatelabel'),  # Updatelabel

    # path('addLabelOnNote/', views.addLabelOnNote, name='addLabelOnNote'),  # Updatelabel



    path('addLabelOnNote/<int:pk>/', views.addLabelOnNote.as_view(), name='addLabelOnNote'),  # Displays the Labels data in a front view using jinga template

    path('getLabelOnNotes/', views.getLabelOnNotes.as_view(), name='getLabelOnNotes'),  # Displays the Labels data in a front view using jinga template










    # path('mysampleview/', MySampleView.as_view(), name=mysampleview)

    # path('create_label/', views.create_label.as_view(), name='create_label'),    # Paginate

    # path('token/',views. recipes_view,name='token'),
    path('showlabels/', views.showlabels, name='showlabels'),  # Displays the Labels data in a front view using jinga template









    # path('mysampleview/', MySampleView.as_view(), name=mysampleview)

    # path('create_label/', views.create_label.as_view(), name='create_label'),    # Paginate

    # path('token/',views. recipes_view,name='token'),

]

