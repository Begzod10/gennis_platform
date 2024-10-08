from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'username', 'password1', 'password2']
        labels = {
            'first_name': 'Name',
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class_': 'input'})
            field.widget.attrs.update({'classes': 'input'})



class ProfileForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'surname', 'username',
                  'father_name', 'profile_img', 'birth_date', 'phone', 'comment', 'age', 'observer', ]

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class_': 'input'})
            field.widget.attrs.update({'classes': 'input'})
