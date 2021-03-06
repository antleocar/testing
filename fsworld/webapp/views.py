# -*- encoding: utf-8 -*-
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

from webapp.models import Profile, Comment, Picture, Experience,  Step, Activation
from ajax.models import UploadedImage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views
from webapp.forms import NewAccountForm,EditAccountForm,ExperienceForm, SearchExperienceForm, SearchProfileForm, AddComment

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseNotAllowed
from django.shortcuts import render


#Para el hash con md5
import hashlib


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

        experiences = Experience.objects.all().order_by('-creation_date')

        return render(request, 'webapp/main.html', {'experiences': experiences[:9]})

@login_required
def new_experience(request):

    if request.method == 'POST':

        form = ExperienceForm(request.POST)
        if form.is_valid:
            experience = store_experience(form, request.user)
            if experience:
                return HttpResponseRedirect(reverse('experience', kwargs={'experience_id': experience.id}))
    else:
        form = ExperienceForm()

    return render(request, 'webapp/newexperience.html', {'form': form})

@login_required
def edit_experience(request, experience_id):
    user = request.user
    e = Experience.objects.get(id=ObjectId(experience_id))

    if e.author != user:
        return HttpResponse('Unauthorized', status=401)
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid:

            experience = store_experience(form, request.user, e)
            if experience:
                return HttpResponseRedirect(reverse('experience', kwargs={'experience_id': experience.id}))  # Redirect after POST

    else:

        form = ExperienceForm.get_filled_form(e)
        return render(request, 'webapp/newexperience.html', {'form': form, 'edit': True})


def store_experience(form, user, experience=None):
    if form.is_valid():

        data = form.cleaned_data

        title = data['title']
        type_of_fishing = data['type_of_fishing']
        description = data['description']
        main_picture = data['main_picture_id']
        pictures_id_list = form.get_pictures_ids_list()
        aparejos = form.get_aparejos_list()
        steps = form.get_steps_list()
        notes = data['notes']
        difficult = data['difficult']
        tags = []
        tags_all = data['tags']

        if tags_all:
            tags = tags_all.split(",")


        imagen_principal = UploadedImage.objects.get(id=main_picture).image

        if not experience:
            experience = Experience()

        experience.title = title
        experience.type_of_fishing = type_of_fishing
        experience.description = description
        experience.aparejos = aparejos
        experience.notes = notes
        experience.tags = tags
        experience.difficult = difficult
        experience.main_image = imagen_principal
        u = user


        step_list = list()
        for step in steps:
            if "picture" in step:
                picture = UploadedImage.objects.get(id=step["picture"]).image
                step_object = Step(text=step['text'], image=picture)
            else:
                step_object = Step(text=step['text'])

            step_list.append(step_object)
        experience.steps = step_list


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


def search_experience(request):
    results_experiences = dict()
    if request.method == 'GET':
        form = SearchExperienceForm(request.GET)
        if form.is_valid():
            data = form.cleaned_data
            query = dict()
            queryFullText = ""
            if data['difficult'] != "":
                query["difficult"] = data['difficult']
            if data['srchterm'] != "":
                queryFullText = queryFullText + data['srchterm']
            if queryFullText != "":
                query["$text"] = {"$search": queryFullText}

            results_experiences = Experience.objects.raw_query(query)

    return render(request, 'webapp/search_experience_result.html', {'matches_experience': results_experiences, 'results': len(results_experiences), 'form': form})


def search_profile(request):
    '''results_profiles = dict()
    if request.method == 'GET':
        form = SearchProfileForm(request.GET)
        if form.is_valid():
            data = form.cleaned_data
            query = dict()
            queryFullText = ""
            if data['srchterm'] != "":
                queryFullText = queryFullText + data['srchterm']
            if queryFullText != "":
                query["$text"] = {"$search": queryFullText}

            results_profiles = Profile.objects.raw_query(query)

    return render(request, 'webapp/search.html', {'matches_profile': results_profiles, 'results': len(results_profiles), 'form': form})'''

    if request.method == "POST":
        search_text = request.POST['search_text']

    else:
        search_text = ''

    results_profiles = Profile.objects.filter(display_name__contains=search_text)
    return render(request,'webapp/search.html', {'matches_profile': results_profiles, 'results': len(results_profiles)})



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
        if form.is_valid():
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


                if avatar_id != u'':
                    p.avatar = avatar.image

                p.user.is_active = False
                p.user.save()
                p.clean()
                p.save()



                if avatar_id != u'':
                    avatar.persist = True
                    avatar.save()

                #return render(request, 'webapp/main', {'profile': p.user.username})  # Redirect after POST
                return HttpResponseRedirect(reverse('newaccount_done', kwargs={'username': p.user.username}))
                #return render(request, 'webapp/main.html')

    else:
        form = NewAccountForm()

    return render(request, 'webapp/newaccount.html', {'form': form})


@login_required
def modification_account(request, username):

    if request.method == 'POST':
        form = EditAccountForm(request.POST)
        if form.is_valid():
            valid = True
            data = form.cleaned_data
            password = data['password']
            password_repeat = data['password_repeat']
            display_name = data['display_name']
            location = data['location']
            avatar_id = data['avatar_id']

            if password:
                if not password == password_repeat:
                    errors = form._errors.setdefault("password_repeat", ErrorList())
                    output = _("Passwords don't match")
                    errors.append(unicode(output))
                    valid = False

            u = request.user
            p = u.profile.get()
            p.display_name = display_name
            p.location = location

            if password:
                u.set_password(password)

            avatar = None
            if avatar_id:
                avatar = models_ajax.UploadedImage.objects.get(id=avatar_id)
                if avatar.image:
                    p.avatar = avatar.image


            if valid:
                u.save()
                p.clean()
                p.save()

                if avatar:
                    avatar.persist = True
                    avatar.save()


                if request.user.is_authenticated():


                    return HttpResponseRedirect(reverse('main'))

    else:
        u = request.user
        p = u.profile.get()
        data = {
            'username': u.username,
            'email': u.email,
            'display_name': p.display_name,
            'location': p.location,
            }
        if p.avatar:
            data['avatar_url']=p.avatar.url
        else:
            data['avatar_url']=p.avatar.url
        form = EditAccountForm(initial=data)

    return render(request, 'webapp/newaccount.html', {'form': form, 'edit': True})


def new_account_done(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404


    if user.is_active:
        return HttpResponseRedirect(reverse('main'))

    ts = time.time()
    now_datetime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    while True:

        hash = hashlib.md5()
        hash.update(username)
        hash.update(str(now_datetime))
        hash.digest()
        if not Activation.objects.filter(code=hash.hexdigest()).exists():
            break

    a = Activation(user=user, code=hash.hexdigest(), date=now_datetime)
    a.save()


    context = {
            'site': request.get_host(),
            'user': user,
            'username': username,
            'token': a.code,
            'secure': request.is_secure(),
        }


    #return HttpResponseRedirect(reverse('activate'), kwargs ={'code': context.__getattribute__('code')})

    body = loader.render_to_string("email/activation_email.txt", context).strip()
    #subject = loader.render_to_string("email/activation_email_subject.txt", context).strip()
    #send_mail(subject, body, "fsworldfsworld@gmail.com", [user.email])

    #enviar el mail.
    return render(request, 'webapp/newaccount_done.html', activate_account(request,a.code)) #pasar profile para mostrar datos en pantallas


def activate_account(request, code):
    try:
        a = Activation.objects.get(code=code)
    except Activation.DoesNotExist:
        raise Http404

    if a.user.is_active:
        return HttpResponseRedirect(reverse('main'))

    a.user.is_active = True
    a.user.save()

    messages.success(request, _("Tu cuenta ha sido correctamente activada.Prueba a loguearte ahora."))
    return HttpResponseRedirect(reverse('login'))


def experience(request, experience_id):

    following = None
    if request.user.is_authenticated():

        my_profile = request.user.profile.get()
        following = my_profile.following

    experience = Experience.objects.get(id=experience_id)

    total_votos = len(experience.positives) + len(experience.negatives)
    porcentaje_positivos = 50
    porcentaje_negativos = 50
    if total_votos != 0:
        porcentaje_positivos = (len(experience.positives) / float(total_votos))*100
        porcentaje_negativos = (len(experience.negatives) / float(total_votos))*100

    num = experience.difficult
    difficult = "Dificil"
    if num>=0 and num<=1:
        difficult = "Facil"
    elif num>=2 and num<=3:
        difficult = "Media"


    return render(request, 'webapp/experience_template.html', {'experience': experience, 'total_votos': total_votos,'difficult_value': difficult,
                                                           'por_pos': int(porcentaje_positivos), 'por_neg': int(porcentaje_negativos),
                                                           'following': following})


def following(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404

    is_owner = False
    if request.user.username == username:
        is_owner = True

    user_profile = Profile.objects.get(user=user)
    tag = _("Seguidos")
    return render(request, 'webapp/following.html',
                  {'follows': user_profile.following, 'profile': user_profile, 'tag': tag, 'is_owner': is_owner})


def followers(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404

    is_owner = False
    if request.user.username == username:
        is_owner = True

    followers_list = Profile.objects.raw_query({'following.user_id': ObjectId(user.id)})
    user_profile = Profile.objects.get(user=user)
    tag = _("Seguidores")
    return render(request, 'webapp/following.html',
                  {'follows': followers_list, 'profile': user_profile, 'tag': tag, 'is_owner': is_owner})


@login_required
def comment(request, experience_id):
    if request.method == 'POST':
        u = request.user
        profile = u.profile.get()
        form = AddComment(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            c = Comment(text=text, create_date=datetime.datetime.now(), user_own=u, )
            e = Experience.objects.get(id=experience_id)
            e.comments.append(c)
            e.save()
    return HttpResponseRedirect(reverse('experience', args=(experience_id,)))


@login_required
def ban_comment(request, experience_id, comment_id):
    if request.method == 'GET':
        u = request.user
        if u.is_staff:
            e = Experience.objects.get(id=experience_id)
            e.comments[int(comment_id)].is_banned = True
            e.save()
    return HttpResponseRedirect(reverse('experience', args=(experience_id,)))


@login_required
def unban_comment(request, experience_id, comment_id):
    if request.method == 'GET':
        u = request.user
        if u.is_staff:
            e = Experience.objects.get(id=experience_id)
            e.comments[int(comment_id)].is_banned = False
            e.save()
    return HttpResponseRedirect(reverse('experience', args=(experience_id,)))


def terms_and_conditions(request):
    return render(request, 'webapp/terms_and_conditions.html')


def contact(request):
    return render(request, 'webapp/contact.html')