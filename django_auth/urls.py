from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from rest_framework.decorators import api_view
admin.autodiscover()
from users import views
from django.contrib import auth
from rest_framework_swagger.views import get_swagger_view
schema_view = get_swagger_view(title='API')

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # for a home page
    url(r'^$', views.signup),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^register/$', views.Registerapi.as_view(), name='register'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate,
        name='activate'),
    url(r'^log_me/$', views.log_me, name='log_me'),

    path('log_user/', views.logins, name='log_user'),
    path('upload_profilenew/', views.upload_profilenew, name='upload_profilenew'),



    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),



    path('admin/', admin.site.urls),  # for a admin login
    path('logout/', views.exit, name='logout'),
    path('createnotes/', views.createnotes, name='createnotes'),  # For Create
    path('readnote/<int:pk>/', views.readnote.as_view(), name='readnote'),  # Read
    path('deletenote/', views.deletenote.as_view(), name='deletenote'),  # Delete with PK
    path('updatenote/<int:pk>/', views.updatenote.as_view(), name='updatenote'),  # Update with Pk
    path('archivenote/', views.archivenote.as_view(), name='archivenote'),  # Update with Pk
    path('restorenote/', views.restorenote.as_view(), name='restorenote'),  # Update with Pk
    path('colornote/<int:pk>/', views.colornote.as_view(), name='colornote'),  # Update with Pk
    path('ispinned/<int:pk>/', views.ispinned.as_view(), name='ispinned'),  # Update with Pk
    path('showpinned/', views.showpinned, name='showpinned'),  # Update with Pk
    path('copynote/<int:pk>/', views.copynote.as_view(), name='copynote'),  # Update with Pk
    path('table/', views.table, name='table'),  # Displays the Table data in a front view using jinga template
    path('showarchive/', views.showarchive, name='showarchive'),
    # Displays the Table data in a front view using jinga template
    path('trash/', views.trash, name='trash'),  # Displays the Table data in a front view using jinga template
    path('page/', views.PostListAPIView.as_view(), name='page'),  # Paginate
    path('create_label/', views.create_label, name='create_label'),  # Createlabel
    path('deletelabel/<int:pk>/', views.deletelabel, name='deletelabel'),  # Deletelabel
    path('updatelabel/<int:pk>/', views.updatelabel.as_view(), name='updatelabel'),  # Updatelabel
    path('addLabelOnNote/<int:pk>/', views.addLabelOnNote.as_view(), name='addLabelOnNote'),
    # Displays the Labels data in a front view using jinga template
    path('getLabelOnNotes/', views.getLabelOnNotes.as_view(), name='getLabelOnNotes'),
    # Displays the Labels data in a front view using jinga template
    path('removeLabelonNote/<int:pk>/', views.removeLabelonNote.as_view(), name='removeLabelonNote'),
    # Displays the Labels data in a front view using jinga template
    url(r'^docs/', schema_view),
    path('getnote/', views.getnote, name='getnote'),
    path('authorize/', views.authorize, name='authorize'),
    path('showlabels/', views.showlabels, name='showlabels'),
    path('create/', views.create.as_view(), name='create'),
    path('createcollaborator/<int:pk>/', views.createcollaborator, name='createcollaborator'),
    path('deletecollaborator/<int:pk>/', views.deletecollaborator, name='deletecollaborator'),
    path('remainder/', views.remainder.as_view(), name='remainder'),
    #checking_decorator
    path('checking_decorator/', views.checking_decorator, name='checking_decorator'),
    #get_all_notes
    path('api/get_all_notes/', views.get_all_notes, name='get_all_notes'),
    path('api/login/', views.apilogin, name='login'),

]
