from django import forms
from .models import User

pwd_help = "Min 8 chars, at least 1 letter and 1 digit."

# Only allow these two roles on signup
ROLE_CHOICES = [
    (User.Roles.CUSTOMER, "Customer"),
    (User.Roles.OWNER, "Owner"),
]


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-sm"}),
        label="Password",
        help_text=pwd_help
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-sm"}),
        label="Confirm Password"
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_role"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "role"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "last_name": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "email": forms.EmailInput(attrs={"class": "form-control form-control-sm"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add uniform placeholder text (optional)
        self.fields["first_name"].widget.attrs.setdefault("placeholder", "First name")
        self.fields["last_name"].widget.attrs.setdefault("placeholder", "Last name")
        self.fields["email"].widget.attrs.setdefault("placeholder", "you@example.com")
        self.fields["password1"].widget.attrs.setdefault("placeholder", "Password")
        self.fields["password2"].widget.attrs.setdefault("placeholder", "Confirm password")

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
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control form-control-sm"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-sm"})
    )
