__author__ = 'Antonio-PC'
# -*- encoding: utf-8 -*-

import string
import urllib2
from urlparse import urlparse
import django
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models import Q
from django.db.models.query import RawQuerySet
from django.forms import ImageField
from django.templatetags.static import static
from pip._vendor import requests
from ajax import models as models_ajax
from bson import ObjectId
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from webapp.models import Profile, Comment, Step, Picture, Experience,  SetUp
from ajax.models import UploadedImage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views
from webapp.forms import NewAccountForm,EditAccountForm,ExperienceForm,SearchExperienceForm,AddComment

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseNotAllowed
from django.shortcuts import render


from django.forms.util import ErrorList
import time, datetime

from social.pipeline.partial import partial
from django.shortcuts import redirect

from django.utils.translation import ugettext as _

#Para el correo
from django.core.mail import send_mail
from django.template import loader

#Para el hash con md5
import hashlib

#full-text
from pymongo import *

# -*- encoding: utf-8 -*-


def main(request):
    if request.user.is_authenticated():

        experiences = Experience.objects.all().order_by('-creation_date')
    return render(request, 'webapp/main.html')


def experiences(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404

    is_owner = False
    if request.user.username == username:
        is_owner = True

    experiences_list = Experience.objects.raw_query({'author_id': ObjectId(user.id)}).order_by('-creation_date')
    return render(request, 'webapp/experiences.html', {'experiences': experiences_list, 'is_owner': is_owner})


