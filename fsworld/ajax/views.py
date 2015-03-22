# coding=utf-8
from ajax.forms import ImageUploadForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render
from django.core.files import File
from ajax.models import UploadedImage
import json
from webapp.models import Following
from webapp.models import Experience, Vote
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist


def test(request):
    return render(request, 'ajax/follow.html', )


def upload_picture(request):
    f = request.FILES['image']
    img = UploadedImage(image=f)
    img.save()
    return HttpResponse(json.dumps({"id": img.id, "url": img.image.url}))


def follow(request):

    me = request.user
    if not me.is_authenticated():
        return HttpResponse(json.dumps({"message": "No está logueado"}), status=403)
    my_profile = me.profile.get()


    username = request.POST['username']
    if not username:
        return HttpResponse(json.dumps({"message": "Debe especificar un usuario a seguir por su nombre"}), status=400)
    elif username == me.username:
        return HttpResponse(json.dumps({"message": "No puedes seguirte a ti mismo"}), status=400)
    try:
        who = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"message": "Nombre usuario inválido"}), status=400)


    following_now = my_profile.following
    for f in following_now:
        if f.user.id == who.id:
            return HttpResponse(json.dumps({"message": "Ya lo estás siguiendo " + who.username}), status=400)

    # Lo añado a mi lista
    following_now.append(Following.create_following(who))
    my_profile.save()

    # Y respondo con un ok

    return HttpResponse(json.dumps({"message": "OK"}), status=200)


def unfollow(request):
    # Saco el usuario actual, y me aseguro de que esté logueado
    me = request.user
    if not me.is_authenticated():
        return HttpResponse(json.dumps({"message": "El usuario no está logueado"}), status=403)
    my_profile = me.profile.get()


    username = request.POST['username']
    if not username:
        return HttpResponse(json.dumps({"message": "Debe especificar un usuario a seguir por su nombre"}), status=400)
    try:
        who = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"message": "Nombre usuario inválido"}), status=400)


    following_now = my_profile.following
    for f in following_now:
        if f.user.id == who.id:
            # Dejo de seguirlo
            following_now.remove(f)
            my_profile.save()
            return HttpResponse(json.dumps({"message": "OK"}), status=200)

    return HttpResponse(json.dumps({"message": "No estás siguiendo a" + who.username}), status=400)


def vote_experience(request):

    ppal = request.user
    if not ppal.is_authenticated():
        return HttpResponse(json.dumps({"message":"El usuario no está logueado"}), status=403)


    experience_id = request.POST['experience']
    if not experience_id:
        return HttpResponse(json.dumps({"message": "Debes especificar una experiencia para poder votarla"}), status=400)

    try:
        experience = Experience.objects.get(id=experience_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"message": "Experiencia inválida"}), status=400)

    # Compruebo que se ha especificado un tipo de voto valido y construyo un nuevo voto con el
    vote_type = request.POST['type']
    if not vote_type:
        return HttpResponse(json.dumps({"message": "Debes especificar un tipo de voto(positivo o negativo)"}), status=400)
    if vote_type != u'positive' and vote_type != u'negative':
        return HttpResponse(json.dumps({"message": "Debes especificar un voto válido(positivo o negativo)"}), status=400)

    new_vote = Vote(user=ppal, date=datetime.now())


    found = False

    if not found:
        for vote in experience.positives:
            if vote.user == ppal:
                if vote_type == u'positive':
                    return HttpResponse(json.dumps({"message": "Ya está votada"}), status=200)
                else:
                    experience.positives.remove(vote)
                    found = True
                    break

    if not found:
        for vote in experience.negatives:
            if vote.user == ppal:
                if vote_type == u'negative':
                    return HttpResponse(json.dumps({"message": "Ya está votada"}), status=200)
                else:
                    experience.negatives.remove(vote)
                    break


    if vote_type == u'positive':
        experience.positives.append(new_vote)
        experience.save()
    else:
        experience.negatives.append(new_vote)
        experience.save()

    return HttpResponse(json.dumps({"message": "OK"}), status=201)


def experience_votes(request, experience_id):
    if experience_id == u'':
        return HttpResponse(json.dumps({"message": "ERROR: debes especificar el identificador de la experiencia"}), status=400)

    experience = Experience.objects.get(id=experience_id)

    total_votos = len(experience.positives) + len(experience.negatives)
    porcentaje_positivos = 50
    porcentaje_negativos = 50
    if total_votos != 0:
        porcentaje_positivos = (len(experience.positives) / float(total_votos))*100
        porcentaje_negativos = (len(experience.negatives) / float(total_votos))*100

    context= {"positives": len(experience.positives),
              "negatives": len(experience.negatives),
              "total": total_votos,
              "por_pos": porcentaje_positivos,
              "por_neg": porcentaje_negativos}

    return HttpResponse(json.dumps(context), status=200)
