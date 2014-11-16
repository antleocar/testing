import json
import django
from ajax.models import UploadedImage
from django import forms
from django.utils.translation import ugettext_lazy as _
from models import Experience, Profile, SetUp


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

    title = forms.CharField(max_length=50, required=False)
    main_picture_id = forms.CharField(required=True)
    pictures_ids_json = forms.CharField(required=False)
    description = forms.CharField(required=False)
    setups_json = forms.CharField(required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    tags = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ExperienceForm, self).__init__(*args, **kwargs)

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

    def get_setups_list(self):
        try:
            json_data = self.cleaned_data['setups_json']
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
            'description': e.description,
            'main_picture_id': UploadedImage.objects.get(image=e.main_image).id,
            'notes': e.notes,
            'tags': ",".join(e.tags),
                    }

        #pictures
        pictures_ids_list = list()
        for pic in e.pictures:
            pictures_ids_list.append(UploadedImage.objects.get(image=pic.image).id)
        data['pictures_ids_json'] = json.dumps(pictures_ids_list)

        #setups
        setups_list = list()
        for setup in e.setups:
            if setup.image:
                DIFFICULT = [(1, _("Easy")), (2, _("Medium")), (3, _("Hard"))]
                difficult = forms.ChoiceField(choices=DIFFICULT, required=False)
                setups_list.append({"text": setup.text, "difficult": setup.difficult,
                                    "type_of_fishing": setup.type_of_fishing,"picture": UploadedImage.objects.get(image=setup.image).id})
            else:
                setups_list.append({"text": setup.text, "type_of_fishing": setup.type_of_fishing})
        data['steps_json'] = json.dumps(setups_list)

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
    def __init__(self, *args, **kwargs):
        super(SearchExperienceForm, self).__init__(*args, **kwargs)


