from django.test import RequestFactory
from django.urls import reverse
from . models import User

class TestViews:
    def login_detail(self):
        path=reverse()