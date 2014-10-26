__author__ = 'Antonio-PC'

from django.conf.urls import patterns, url
from webapp import views


urlpatterns = patterns('',


    url(r'^$', views.main, name='main'),

    url(r'^profile/(?P<username>[.\w]+)/experiences/$' , views.experiences, name='experiences'),




)