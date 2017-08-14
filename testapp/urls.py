from django.conf.urls import url
from django.http import HttpResponse
from django.views.generic import View


try:
    from django.conf.defaults import patterns
except ImportError:
    patterns = list


class HelloWorld(View):

    def get(self, request):
        return HttpResponse('Hello, world!')


urlpatterns = [
    url(r'^$', HelloWorld.as_view(), name='hello'),
]
