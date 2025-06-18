# quiz_app/urls.py

from django.contrib import admin
from django.urls import path, include
from quiz.views import home, error_403
from quiz.views_auth import LogoutGetAllowedView

urlpatterns = [
    # Page d'accueil
    path('', home, name='home'),

    # Routes de l'application "quiz"
    path('quiz/', include(('quiz.urls', 'quiz'), namespace='quiz')),

    # Interface d'administration
    path('admin/', admin.site.urls),

    # Authentification Django (login, gestion de mot de passe)
    path('accounts/', include('django.contrib.auth.urls')),

    # Logout autorisé par GET
    path('accounts/logout/', LogoutGetAllowedView.as_view(), name='logout'),
]

# Handler personnalisé pour les 403 Forbidden
handler403 = error_403
