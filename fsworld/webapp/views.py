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
django.contrib.auth.forms.UserCreationForm
from webapp.models import Profile, Comment, Picture, Experience,  SetUp
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


#full-text
from pymongo import *

# -*- encoding: utf-8 -*-


def main(request):
    if request.user.is_authenticated():

        experiences = Experience.objects.all().order_by('-creation_date')
    return render(request, 'webapp/main.html')

@login_required
def new_experience(request):
    #TODO if user is authenticated redirect to main
    if request.method == 'POST':
        # else -> render respone with the obtained form, with errors and stuff
        form = ExperienceForm(request.POST)
        if form.is_valid:  # else -> render respone with the obtained form, with errors and stuff
            experience = store_experience(form, request.user)
            if experience:
                return HttpResponseRedirect(reverse('experience', kwargs={'experience_id': experience.id}))  # Redirect after POST
    else:
        form = ExperienceForm()

    return render(request, 'webapp/newexperience.html', {'form': form})


def store_experience(form, user, experience=None, parent=None):
    if form.is_valid():
        # Extract the data from the form and create the User and Profile instance
        data = form.cleaned_data

        # Basic information
        title = data['title']
        description = data['description']
        main_picture = data['main_picture_id']
        pictures_id_list = form.get_pictures_ids_list()
        setups = form.get_setups_list()
        notes = data['notes']
        tags = []
        tags_all = data['tags']

        if tags_all:
            tags = tags_all.split(",")

        # Genera la experience

        imagen_principal = UploadedImage.objects.get(id=main_picture).image

        if not experience:
            experience = Experience()

        experience.title = title
        experience.description = description
        experience.notes = notes
        experience.tags = tags
        experience.main_image = imagen_principal
        u = user

        # setups is a list of dict
        setup_list = list()
        for setup in setups:
            if "picture" in setup:
                picture = UploadedImage.objects.get(id=setup["picture"]).image
                setup_object = SetUp(text=setup['text'],type_of_fishing=setup['type_of_fishing'], difficult=setup['difficult'],
                                     enumerate=setup['enumerate'], image=picture)
            else:
                setup_object = SetUp(text=setup['text'],type_of_fishing=setup['type_of_fishing'])

            setup_list.append(setup_object)
        experience.setups = setup_list

        # pictures_id_list is a list of ids
        pictures_list = list()
        if pictures_id_list:
            for pic in pictures_id_list:
                if pic:
                    picture = Picture(image=UploadedImage.objects.get(id=pic).image)
                    pictures_list.append(picture)

        experience.pictures = pictures_list
        experience.author = u
        experience.clean()
        experience.save()
        return experience
    else:
        return None


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


def login_user(request):
    # Usa la Authentication View:
    # https://docs.djangoproject.com/en/1.5/topics/auth/default/#module-django.contrib.auth.views
    return views.login(request, 'webapp/login.html')


def logout_user(request):

    return views.logout(request, next_page=reverse('main'))


def search_profile(request, terms):
    if request.method == 'GET':

        client = MongoClient()

        results_profiles = Profile.objects.raw_query({"$text": {"$search": terms}})

        return render(request, 'webapp/search_person_result.html', {'matches_profile': results_profiles})


def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    user_profile = Profile.objects.get(user=user)
    experiences = Experience.objects.raw_query({'author_id': ObjectId(user.id)})
    followers_list = Profile.objects.raw_query({'following.user_id': ObjectId(user.id)})
    is_owner = False
    if request.user.username == username:
        is_owner = True

    # Compruebo si está en mi lista de seguidos
    is_following = False
    if request.user.is_authenticated() and user.id != request.user.id:
        my_profile = request.user.profile.get()

        following_now = my_profile.following
        for f in following_now:
            if f.user.id == user.id:
                is_following = True

    return render(request, 'webapp/profile.html',
                  {'profile': user_profile, 'following': is_following, 'followers_list': followers_list,
                   'experiences': experiences, 'is_owner': is_owner})


def new_account(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('main'))

    if request.method == 'POST':
        form = NewAccountForm(request.POST)
        if form.is_valid():  # else -> render respone with the obtained form, with errors and stuff
            # Extract the data from the form and create the User and Profile instance
            data = form.cleaned_data
            username = data['username']
            email = data['email']
            password = data['password']
            password_repeat = data['password_repeat']
            display_name = data['display_name']
            location = data['location']

            avatar_id = data['avatar_id']
            if avatar_id != u'':
                avatar = models_ajax.UploadedImage.objects.get(id=avatar_id)

            if not password == password_repeat:
                errors = form._errors.setdefault("password_repeat", ErrorList())
                output = _("Passwords don't match")
                errors.append(unicode(output))

            elif User.objects.filter(username=username).count():
                errors = form._errors.setdefault("username", ErrorList())
                output = _("Username alerady taken")
                errors.append(unicode(output))

            try:
                valid_email = User.objects.get(email=email)
            except:
                valid_email = False

            if valid_email:
                errors = form._errors.setdefault("email", ErrorList())
                output = _("Email alerady exists")
                errors.append(unicode(output))

            else:
                u = User.objects.create_user(username, email, password)
                p = Profile(display_name=display_name, user=u,
                            location=location, username=username)

                #avatar.image.name = str(p.id) + '.png' # No vale así, hay que copiar el archivo en otro
                if avatar_id != u'':
                    p.avatar = avatar.image

                p.user.is_active = False
                p.user.save()
                p.clean()
                p.save()

                #Generar el codigo y meterlo en la BD.

                if avatar_id != u'':
                    avatar.persist = True
                    avatar.save()

                return render(request, 'webapp/main', {'profile': p.user.username})  # Redirect after POST
                #return HttpResponseRedirect(reverse('newaccount_done', kwargs={'username': p.user.username}))
                #return render(request, 'webapp/main.html')

    else:
        form = NewAccountForm()

    return render(request, 'webapp/newaccount.html', {'form': form})


def experience(request, experience_id):

    following = None
    if request.user.is_authenticated():
        #username = request.user.username
        #user = User.objects.get(username=username)
        my_profile = request.user.profile.get()
        following = my_profile.following

    experience = Experience.objects.get(id=experience_id)

    total_votos = len(experience.positives) + len(experience.negatives)
    porcentaje_positivos = 50
    porcentaje_negativos = 50
    if total_votos != 0:
        porcentaje_positivos = (len(experience.positives) / float(total_votos))*100
        porcentaje_negativos = (len(experience.negatives) / float(total_votos))*100




    return render(request, 'webapp/experience_template.html', {'experience': experience, 'total_votos': total_votos,
                                                           'por_pos': int(porcentaje_positivos), 'por_neg': int(porcentaje_negativos),
                                                           'following': following})

def terms_and_conditions(request):
    return render(request, 'webapp/terms_and_conditions.html')


def contact(request):
    return render(request, 'webapp/contact.html')