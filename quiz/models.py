from django.conf import settings
from django.db import models


class Classe(models.Model):
    nom = models.CharField(max_length=100)
    enseignant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    etudiants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="classes",
        blank=True
    )

    def __str__(self):
        return self.nom


class Quiz(models.Model):
    """Un quiz créé par un enseignant et associé à une classe."""
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    classe = models.ForeignKey(
        Classe, on_delete=models.CASCADE, related_name="quizzes"
    )
    enseignant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"groups__name": "Enseignant"},
        related_name="quizzes"
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre


class Question(models.Model):
    """Une question (QCM) appartenant à un quiz."""
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="questions"
    )
    texte = models.TextField()

    def __str__(self):
        return f"Q{self.id} – {self.quiz.titre}"


class Choice(models.Model):
    """Un choix (réponse possible) pour une question."""
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    texte = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{'✔' if self.is_correct else '✘'} {self.texte}"


class QuizSession(models.Model):
    """Une tentative d’un·e étudiant·e sur un quiz."""
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="sessions"
    )
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="sessions"
    )
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0)

    class Meta:
        constraints = [
            # => un·e même étudiant·e ne peut avoir qu’une seule session :
            models.UniqueConstraint(
                fields=["quiz", "etudiant"],
                name="unique_quiz_attempt_per_student"
            )
        ]

    def __str__(self):
        return f"{self.etudiant} / {self.quiz} – {self.score:.1f}%"
