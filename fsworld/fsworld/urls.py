from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fsworld.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('webapp.urls')),
    url(r'^ajax/', include('ajax.urls')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^password/', include('password_reset.urls')),


)
