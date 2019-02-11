
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
    path('', TemplateView.as_view(template_name='home.html'), name='home'), # for a home page
    url(r'^$', views.signup),
    url(r'^signup/$', views.signup, name='signup'),

    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate,
        name='activate'),


    url(r'^log_me/$', views.log_me, name='log_me'),
    path('log_user/', views.logins, name='log_user'),
#    path('upload_profile/',views.upload_profile,name='upload_profile'),

    path('fileupload/',views.fileupload, name='fileupload'),
    path('upload_profilenew/',views.upload_profilenew, name='upload_profilenew'),
    path('upload/',views.upload,name='upload'),
#upload_profile

    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin/', admin.site.urls),    # for a admin login

    path('logout/',views.exit,name='logout'),

    path('createnote/', views.createnote.as_view(), name='createnote'),
    path('readnote/<int:pk>/',views.readnote.as_view(), name='readnote'),
    path('deletenote/<int:pk>/',views.deletenote.as_view(), name='deletenote'),
    path('updatenote/<int:pk>/',views.updatenote.as_view(),name='updatenote'),
    # path('deleteenote/<int:pk>', views.deleteenote, name='deleteenote'),


    # url(r'^notes/', include(('Notes.urls','Notes'),namespace='Notes')),



#log_me
    # url(r'^register/',include('users.urls')),
    # url(r'^register1/', include('users.urls')),
    # url(r'^$', 'home', name='home'),
    # url(r'^user/', include(('users.urls','users'),namespace='users')),  # create model
    # url(r'^temail/',include('users.urls')),
    # url(r'^log_me/',include('users.urls')),
    # url(r'^log_me/', include('users.urls')),

    #path('log_me/', views.log_me, name='log_me'),
    # url('^', include('django.cont
    # rib.auth.urls')),
    #path('log_user/', views.logins, name='log_user'),
] #url(r'^login_use/', include('users.urls')),

# urlpatterns=format_suffix_patterns(urlpatterns)
