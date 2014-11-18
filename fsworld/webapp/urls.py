__author__ = 'Antonio-PC'

from django.conf.urls import patterns, url
from webapp import views


urlpatterns = patterns('',


    url(r'^$', views.main, name='main'),

    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^account/new/$', views.new_account, name='newaccount'),
    url(r'^newaccount_done/(?P<username>.+)/$', views.new_account_done, name='newaccount_done'),
    url(r'^account/activate/(?P<code>.+)/$', views.activate_account, name='activate'),


    url(r'^profile/(?P<username>[.\w]+)/$', views.profile, name='profile'),

    url(r'^profile/(?P<username>[.\w]+)/experiences/$' , views.experiences, name='experiences'),

    url(r'^newexperience', views.new_experience, name='newexperience'),
    url(r'^experience/(?P<experience_id>\w+)/$' , views.experience, name='experience'),
    url(r'^about/contact/$', views.contact, name='contact'),
    url(r'^about/terms/$', views.terms_and_conditions, name='terms_and_conditions'),

    url(r'^search/person/(?P<terms>.+)$' , views.search_profile, name='search_person'),




)