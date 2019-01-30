
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.views.generic import TemplateView
# from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    # url(r'^$', 'home', name='home'),
    path('admin/', admin.site.urls),
    url(r'^user/', include(('users.urls','users'),namespace='users')),
]

# urlpatterns=format_suffix_patterns(urlpatterns)
