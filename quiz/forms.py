from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Adresse e-mail",
        help_text=""  # on supprime l'aide par défaut
    )
    ROLE_CHOICES = (
        ('Enseignant', 'Enseignant'),
        ('Etudiant', 'Étudiant'),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, required=True, label="Vous êtes",
        help_text=""
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Username
        self.fields['username'].help_text = (
            "Requis • 150 caractères max • Lettres, chiffres et @ . + - _"
        )

        # Password1
        self.fields['password1'].help_text = (
            "Au moins 8 caractères, pas totalement numérique"
        )

        # Password2
        self.fields['password2'].help_text = "Confirmez le mot de passe"

