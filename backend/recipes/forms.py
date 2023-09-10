from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, ModelForm

from recipes.models import Tag


class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'


class AmountIngredientFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        has_at_least_one_ingredient = False

        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                ingredient = form.cleaned_data.get('ingredient')
                if ingredient is None:
                    raise ValidationError('Обязательное поле.')
                has_at_least_one_ingredient = True
        if not has_at_least_one_ingredient:
            raise ValidationError(
                'Нужен хотя бы один ингредиент.'
                )
