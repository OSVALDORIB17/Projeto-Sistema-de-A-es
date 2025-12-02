from django import forms
from django.contrib.auth import forms
from .models import Users

class UserChangeForm(forms.UserChangeForm):
    class Meta(forms.UserChangeForm):
        model = Users
        fields = "__all__"

class UserCreationForm(forms.UserCreationForm):
    class Meta(forms.UserCreationForm.Meta):
        model = Users