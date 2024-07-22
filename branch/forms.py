from django import forms
from django.forms import ModelForm

from .models import Branch


class BranchForm(ModelForm):
    class Meta:
        model = Branch
        fields = (
            'name', 'number',)
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(BranchForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

        # self.fields['title'].widget.attrs.update({
        #     'class': 'input'
        # })
