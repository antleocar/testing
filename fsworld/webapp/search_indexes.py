__author__ = 'AntPc'

from haystack import indexes
import datetime
from webapp.models import Profile


class ProfileIndex(indexes.SearchIndex, indexes.Indexable):
    display_name=indexes.CharField(document=True, use_template=True)
    location =indexes.CharField(model_attr='location')
    username =indexes.CharField(model_attr='username')

    def get_model(self):
        return Profile

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
