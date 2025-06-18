from django.contrib import admin
from .models import Classe, Quiz, Question, Choice, QuizSession

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'enseignant')
    search_fields = ('nom',)
    list_filter = ('enseignant',)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('titre', 'classe', 'enseignant', 'date_creation')
    search_fields = ('titre', 'description')
    list_filter = ('classe', 'enseignant')

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'texte_court')
    search_fields = ('texte',)
    list_filter = ('quiz',)
    inlines = [ChoiceInline]

    def texte_court(self, obj):
        return obj.texte[:50] + ('…' if len(obj.texte) > 50 else '')
    texte_court.short_description = 'Texte (abrégé)'

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('texte_court', 'question', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('texte',)

    def texte_court(self, obj):
        return obj.texte[:50] + ('…' if len(obj.texte) > 50 else '')
    texte_court.short_description = 'Texte (abrégé)'

@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'etudiant', 'score', 'date_debut', 'date_fin')
    list_filter = ('quiz', 'etudiant')
    search_fields = ('etudiant__username',)
