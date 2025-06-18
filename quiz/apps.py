from django.apps import AppConfig
from django.db.models.signals import post_migrate

class QuizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz'
    verbose_name = "Application de Quiz"

    def ready(self):
        from django.contrib.auth.models import Group

        def create_roles(sender, **kwargs):
            """
            Crée les groupes 'Enseignant' et 'Etudiant' après chaque migration.
            """
            roles = ['Enseignant', 'Etudiant']
            for role in roles:
                Group.objects.get_or_create(name=role)

        post_migrate.connect(create_roles, sender=self)
