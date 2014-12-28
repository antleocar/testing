import json
import django
from ajax.models import UploadedImage
from django import forms
from django.utils.translation import ugettext_lazy as _
from models import Experience, Profile, Step


class NewAccountForm(forms.Form):

    username = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    password_repeat = forms.CharField(widget=forms.PasswordInput)
    display_name = forms.CharField(max_length=50, required=True)
    location = forms.CharField(max_length=50, required=False)
    avatar_url = forms.URLField(required=False)
    avatar_id = forms.CharField(max_length=200, required=False)

    def __init__(self, *args, **kwargs):
        super(NewAccountForm, self).__init__(*args, **kwargs)


class ExperienceForm(forms.Form):

    DIFFICULT = [(1, _("Facil")), (2, _("Media")), (3, _("Dificil"))]
    difficult = forms.ChoiceField(choices=DIFFICULT, required=False)
    title = forms.CharField(max_length=50, required=False)
    type_of_fishing = forms.CharField(max_length=50, required=False)
    main_picture_id = forms.CharField(required=True)

    pictures_ids_json = forms.CharField(required=False)
    description = forms.CharField(required=False)
    aparejos_json = forms.CharField(required=True)
    steps_json = forms.CharField(required=True)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    tags = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ExperienceForm, self).__init__(*args, **kwargs)

    def get_aparejos_list(self):
        try:
            json_data = self.cleaned_data['aparejos_json']
            data = json.loads(json_data)
            return data
        except AttributeError:
            return None
        except KeyError:
            return None

    def get_pictures_ids_list(self):
        try:
            json_data = self.cleaned_data['pictures_ids_json']
            if json_data:
                data = json.loads(json_data)
                return data
        except AttributeError:
            return None
        except KeyError:
            return None
        return None

    def get_steps_list(self):
        try:
            json_data = self.cleaned_data['steps_json']
            data = json.loads(json_data)
            return data
        except AttributeError:
            return None
        except KeyError:
            return None

    @staticmethod
    def get_filled_form(e):
        data = {
            'title': e.title,
            'type_of_fishing': e.type_of_fishing,
            'description': e.description,
            'main_picture_id': UploadedImage.objects.get(image=e.main_image).id,
            'notes': e.notes,
            'difficult': e.difficult,
            'tags': ",".join(e.tags),
        }

        #aparejos
        aparejos_list = e.aparejos
        data['aparejos_json'] = json.dumps(aparejos_list)

        #pictures
        pictures_ids_list = list()
        for pic in e.pictures:
            pictures_ids_list.append(UploadedImage.objects.get(image=pic.image).id)
        data['pictures_ids_json'] = json.dumps(pictures_ids_list)

        #steps
        steps_list = list()
        for step in e.steps:
            if step.image:
                steps_list.append({"text": step.text, "picture": UploadedImage.objects.get(image=step.image).id})
            else:
                steps_list.append({"text": step.text})
        data['steps_json'] = json.dumps(steps_list)

        return ExperienceForm(data)


class EditAccountForm(NewAccountForm):
    def __init__(self, *args, **kwargs):
        super(EditAccountForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields['email'].required = False
        self.fields['password'].required = False
        self.fields['password_repeat'].required = False


class AddComment(forms.Form):
    text = forms.CharField(required=True)


class SearchExperienceForm(forms.Form):
    DIFFICULT = [(1, _("Facil")), (2, _("Media")), (3, _("Dificil"))]
    srchterm = forms.CharField(max_length=100, required=False)
    difficult = forms.ChoiceField(choices=DIFFICULT, required=False)

    def __init__(self, *args, **kwargs):
        super(SearchExperienceForm, self).__init__(*args, **kwargs)


