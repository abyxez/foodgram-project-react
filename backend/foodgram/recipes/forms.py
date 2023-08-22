from django.forms import ModelForm
from recipes.models import Tag


class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'
