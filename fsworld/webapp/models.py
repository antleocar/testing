__author__ = 'Antonio-PC'

import django
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import IntegerField, ForeignKey, CharField, TextField, DateTimeField
from djangotoolbox.fields import EmbeddedModelField, ListField
from django.core.exceptions import ValidationError
from datetime import datetime
from django_mongodb_engine.contrib import MongoDBManager


# Validators

def validate_tags(tags):
    if len(tags) > 10:
        raise ValidationError("Max number of tags is 10")


def validate_last_login(last_login):
    if type(last_login) is not datetime:
        raise ValidationError(u'last login type must be date')
    if last_login is None:
        raise ValidationError(u'last login cannot be None')
    date = datetime.today()
    if last_login > date:
        raise ValidationError(u'last_login date cannot be after current date')


def validate_past_date(date):
    now = datetime.now()
    if now > date:
        raise ValidationError(u'date cannot be future')


def validate_difficult(difficult):
    if difficult <= 0 or difficult >= 4:
        raise ValidationError("Difficult must be in range 1 to 3")


class Experience(models.Model):
    title = CharField(max_length=50, blank=False)
    description = TextField(blank=False)
    creation_date = DateTimeField(auto_now_add=True)
    modification_date = DateTimeField(auto_now_add=True, null=True)
    aparejos = ListField(blank=False)
    type_of_fishing = CharField(max_length=50, blank=True)
    notes = TextField(null=True)
    difficult = IntegerField(null=True, validators=[validate_difficult])
    tags = ListField(null=True, validators=[validate_tags])
    #embedded
    author = ForeignKey(User)
    pictures = ListField(EmbeddedModelField('Picture'))
    comments = ListField(EmbeddedModelField('Comment'), blank=True)
    steps = ListField(EmbeddedModelField('Step'), null=False)
    positives = ListField(EmbeddedModelField('Vote'))
    negatives = ListField(EmbeddedModelField('Vote'))
    objects = MongoDBManager()

    def __str__(self):
        return self.title


class Activation(models.Model):
    user = models.ForeignKey(User, related_name="activation", unique=True)
    code = models.CharField(max_length=100) #hash del usuario y la fecha
    date = models.DateTimeField()


class Profile(models.Model):
    display_name = models.CharField(max_length=50, blank=False)
    #Past
    modification_date = models.DateTimeField(null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True)
    location = models.CharField(max_length=50, blank=False)
    user = models.ForeignKey(User, related_name="profile", unique=True)
    following = ListField(EmbeddedModelField('Following'))
    karma = models.IntegerField(default=6)
    username = models.CharField(max_length=50, blank=False)
    objects = MongoDBManager()

    def __str__(self):
        return str(self.display_name)

    def get_experiences(self):
        return Experience.objects.filter(author=self.user)


class Vote(models.Model):
    date = models.DateField(validators=[validate_past_date])
    user = ForeignKey(User)

    def __eq__(self, other):
        return self.user is other.user and self.date == other.date


class Step(models.Model):
    text = models.TextField(blank=False)
    image = models.ImageField(upload_to="images/experience/", null=True)


class Picture(models.Model):
    image = models.ImageField(upload_to="images/", null=False)


class Comment(models.Model):
    text = models.TextField(blank=False)
    create_date = models.DateTimeField()
    user_own = ForeignKey(User)
    is_banned = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Following(models.Model):
    display_name = models.CharField(max_length=50, blank=False)
    username = models.CharField(max_length=50, blank=False)
    user = models.ForeignKey(User)

    @staticmethod
    def create_following(user):
        return Following(display_name=user.profile.get().display_name, username=user.username, user=user)
