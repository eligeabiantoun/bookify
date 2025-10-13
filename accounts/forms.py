from django import forms
from .models import User

pwd_help = "Min 8 chars, at least 1 letter and 1 digit."


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput, 
        label="Password", 
        help_text=pwd_help
    )
    password2 = forms.CharField(
    widget=forms.PasswordInput, 
    label="Confirm Password"
    )
    role = forms.ChoiceField(
        choices=User.Roles.choices,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_role"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "role"]


    def clean_password1(self):
        p = self.cleaned_data.get("password1", "")
        if len(p) < 8 or not any(c.isalpha() for c in p) or not any(c.isdigit() for c in p):
            raise forms.ValidationError(pwd_help)
        return p

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned
    
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
