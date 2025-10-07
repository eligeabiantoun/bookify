from django import forms
from .models import User

pwd_help = "Min 8 chars, at least 1 letter and 1 digit."

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, help_text=pwd_help)
    role = forms.ChoiceField(choices=[(User.Roles.CUSTOMER,"Customer"), (User.Roles.OWNER,"Owner")])
    class Meta:
        model = User
        fields = ["first_name","last_name","email","password","role"]
    def clean_password(self):
        p = self.cleaned_data["password"]
        if len(p) < 8 or not any(c.isalpha() for c in p) or not any(c.isdigit() for c in p):
            raise forms.ValidationError(pwd_help)
        return p

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
