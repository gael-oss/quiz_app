# quiz/views.py
import csv
import datetime
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db import transaction, IntegrityError
from django.db.models import Avg
from django.forms import inlineformset_factory
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    Http404,
)
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    View,
)

from .forms import RegistrationForm
from .models import Classe, Quiz, QuizSession, Question, Choice

# ------------------------------------------------------------------
# Mixins utilitaires
# ------------------------------------------------------------------
class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Enseignant").exists()


class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Etudiant").exists()


def error_403(request, exception=None):
    """Page 403 personnalisée."""
    return render(request, "403.html", status=403)


# ------------------------------------------------------------------
# Fonctions d’aide
# ------------------------------------------------------------------
def _role_flags(request):
    """Ajoute is_teacher / is_student au contexte."""
    return {
        "is_teacher": (
            request.user.is_authenticated
            and request.user.groups.filter(name="Enseignant").exists()
        ),
        "is_student": (
            request.user.is_authenticated
            and request.user.groups.filter(name="Etudiant").exists()
        ),
    }


# ------------------------------------------------------------------
# Pages publiques
# ------------------------------------------------------------------
def home(request):
    return render(request, "quiz/home.html", _role_flags(request))


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.save()

            group = Group.objects.get(name=form.cleaned_data["role"])
            user.groups.add(group)
            login(request, user)
            messages.success(request, "Inscription réussie !")
            return redirect(
                "quiz:teacher_dashboard"
                if group.name == "Enseignant"
                else "quiz:student_dashboard"
            )
    else:
        form = RegistrationForm()

    return render(
        request,
        "registration/register.html",
        {"form": form, **_role_flags(request)},
    )


# ------------------------------------------------------------------
# Tableaux de bord
# ------------------------------------------------------------------
@login_required
def teacher_dashboard(request):
    if not request.user.groups.filter(name="Enseignant").exists():
        return HttpResponseForbidden()

    ctx = {
        **_role_flags(request),
        "total_quiz": Quiz.objects.filter(enseignant=request.user).count(),
        "total_classes": Classe.objects.filter(enseignant=request.user).count(),
    }
    return render(request, "quiz/teacher_dashboard.html", ctx)


@login_required
def student_dashboard(request):
    if not request.user.groups.filter(name="Etudiant").exists():
        return HttpResponseForbidden()
    return render(request, "quiz/student_dashboard.html", _role_flags(request))


# ------------------------------------------------------------------
# CRUD Classes
# ------------------------------------------------------------------
class ClassForm(forms.ModelForm):
    etudiants = forms.ModelMultipleChoiceField(
        queryset=Group.objects.get(name="Etudiant").user_set.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 1}),
    )

    class Meta:
        model = Classe
        fields = ["nom", "etudiants"]


class ClassListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Classe
    template_name = "quiz/teacher/class_list.html"
    context_object_name = "classes"

    def get_queryset(self):
        return Classe.objects.filter(enseignant=self.request.user)

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), **_role_flags(self.request)}


class ClassCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Classe
    form_class = ClassForm
    template_name = "quiz/teacher/class_form.html"
    success_url = reverse_lazy("quiz:class_list")

    def form_valid(self, form):
        form.instance.enseignant = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), **_role_flags(self.request)}


class ClassUpdateView(ClassCreateView, UpdateView):
    pass


class ClassDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Classe
    template_name = "quiz/teacher/class_confirm_delete.html"
    success_url = reverse_lazy("quiz:class_list")


# ------------------------------------------------------------------
# CRUD Quiz
# ------------------------------------------------------------------
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["titre", "description", "classe"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["classe"].queryset = Classe.objects.filter(enseignant=user)


class QuizListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Quiz
    template_name = "quiz/teacher/quiz_list.html"
    context_object_name = "quizzes"

    def get_queryset(self):
        return Quiz.objects.filter(enseignant=self.request.user)

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), **_role_flags(self.request)}


class QuizCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = "quiz/teacher/quiz_form.html"
    success_url = reverse_lazy("quiz:quiz_list")

    def get_form(self, *args, **kwargs):
        return QuizForm(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.enseignant = self.request.user
        return super().form_valid(form)

  #  get_context_data = QuizListView.get_context_data


class QuizUpdateView(QuizCreateView, UpdateView):
    pass


class QuizDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Quiz
    template_name = "quiz/teacher/quiz_confirm_delete.html"
    success_url = reverse_lazy("quiz:quiz_list")


# ------------------------------------------------------------------
# CRUD Questions / Choices
# ------------------------------------------------------------------
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["texte"]


ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    fields=("texte", "is_correct"),
    extra=5,  # ← 5 choix possibles
    can_delete=True,
    widgets={"texte": forms.TextInput(attrs={"size": 40})},
)


class QuestionListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    template_name = "quiz/teacher/question_list.html"
    context_object_name = "questions"

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(
            Quiz, pk=self.kwargs["quiz_pk"], enseignant=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.quiz.questions.all()

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "quiz": self.quiz,
            **_role_flags(self.request),
        }


class QuestionCreateView(LoginRequiredMixin, TeacherRequiredMixin, View):
    template_name = "quiz/teacher/question_form.html"

    def get_quiz(self, quiz_pk):
        return get_object_or_404(Quiz, pk=quiz_pk, enseignant=self.request.user)

    def get(self, request, quiz_pk):
        quiz = self.get_quiz(quiz_pk)
        return render(
            request,
            self.template_name,
            {
                "quiz": quiz,
                "q_form": QuestionForm(),
                "c_formset": ChoiceFormSet(),
                **_role_flags(request),
            },
        )

    def post(self, request, quiz_pk):
        quiz = self.get_quiz(quiz_pk)
        q_form = QuestionForm(request.POST)
        c_formset = ChoiceFormSet(request.POST)
        if q_form.is_valid() and c_formset.is_valid():
            question = q_form.save(commit=False)
            question.quiz = quiz
            question.save()
            c_formset.instance = question
            c_formset.save()
            messages.success(request, "Question ajoutée.")
            return redirect("quiz:question_list", quiz_pk=quiz.id)
        return render(
            request,
            self.template_name,
            {
                "quiz": quiz,
                "q_form": q_form,
                "c_formset": c_formset,
                **_role_flags(request),
            },
        )


class QuestionUpdateView(LoginRequiredMixin, TeacherRequiredMixin, View):
    template_name = "quiz/teacher/question_form.html"

    def get_question(self, pk):
        return get_object_or_404(
            Question, pk=pk, quiz__enseignant=self.request.user
        )

    def get(self, request, pk):
        question = self.get_question(pk)
        return render(
            request,
            self.template_name,
            {
                "quiz": question.quiz,
                "q_form": QuestionForm(instance=question),
                "c_formset": ChoiceFormSet(instance=question),
                **_role_flags(request),
            },
        )

    def post(self, request, pk):
        question = self.get_question(pk)
        q_form = QuestionForm(request.POST, instance=question)
        c_formset = ChoiceFormSet(request.POST, instance=question)
        if q_form.is_valid() and c_formset.is_valid():
            q_form.save()
            c_formset.save()
            messages.success(request, "Question mise à jour.")
            return redirect("quiz:question_list", quiz_pk=question.quiz.id)
        return render(
            request,
            self.template_name,
            {
                "quiz": question.quiz,
                "q_form": q_form,
                "c_formset": c_formset,
                **_role_flags(request),
            },
        )


class QuestionDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Question
    template_name = "quiz/teacher/question_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "quiz:question_list", kwargs={"quiz_pk": self.object.quiz.id}
        )


# ------------------------------------------------------------------
# Interface Étudiant
# ------------------------------------------------------------------
class StudentQuizListView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    model = Quiz
    template_name = "quiz/student/student_quiz_list.html"
    context_object_name = "quizzes"

    def get_queryset(self):
        qs = Quiz.objects.filter(classe__in=self.request.user.classes.all())
        done = QuizSession.objects.filter(
            etudiant=self.request.user
        ).values_list("quiz_id", flat=True)
        return qs.exclude(id__in=done)

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), **_role_flags(self.request)}


class QuizTakeView(LoginRequiredMixin, StudentRequiredMixin, DetailView):
    model = Quiz
    template_name = "quiz/student/quiz_take.html"
    context_object_name = "quiz"

    # -- 1) Interdire de passer un quiz déjà fait --------------------------
    def dispatch(self, request, *args, **kwargs):
        self.quiz = self.get_object()  # mémorisé pour post()
        existing = (
            QuizSession.objects.filter(quiz=self.quiz, etudiant=request.user)
            .order_by("-date_fin", "-date_debut")
            .first()
        )
        if existing:
            messages.info(request, "Vous avez déjà passé ce quiz.")
            return redirect("quiz:quiz_result", pk=existing.pk)
        return super().dispatch(request, *args, **kwargs)

    # -- 2) Soumission ------------------------------------------------------
    def post(self, request, *args, **kwargs):
        total = self.quiz.questions.count()
        correct = sum(
            1
            for q in self.quiz.questions.all()
            if (rep := request.POST.get(f"question_{q.pk}"))
            and q.choices.filter(pk=int(rep), is_correct=True).exists()
        )
        score = (correct / total) * 100 if total else 0

        # transaction pour éviter toute course critique
        with transaction.atomic():
            session, created = QuizSession.objects.get_or_create(
                quiz=self.quiz,
                etudiant=request.user,
                defaults={
                    "date_debut": datetime.datetime.now(),
                    "date_fin": datetime.datetime.now(),
                    "score": score,
                },
            )

        if created:
            messages.success(
                request, f"Quiz « {self.quiz.titre} » soumis ! Score : {score:.2f} %"
            )

            # -------- e-mail facultatif -------------
            site = Site.objects.get_current()
            subject = render_to_string(
                "emails/quiz_result_subject.txt", {"quiz": self.quiz}
            ).strip()
            html_msg = render_to_string(
                "emails/quiz_result_body.html",
                {
                    "session": session,
                    "quiz": self.quiz,
                    "site_url": f"http://{site.domain}",
                },
            )
            send_mail(
                subject,
                "",
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                html_message=html_msg,
            )

        return redirect("quiz:quiz_result", pk=session.pk)


class QuizResultView(LoginRequiredMixin, StudentRequiredMixin, DetailView):
    model = QuizSession
    template_name = "quiz/student/quiz_result.html"
    context_object_name = "session"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.etudiant != self.request.user:
            raise Http404("Résultat inaccessible")
        return obj


class StudentSessionListView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    model = QuizSession
    template_name = "quiz/student/student_session_list.html"
    context_object_name = "sessions"
    paginate_by = 5

    def get_queryset(self):
        qs = QuizSession.objects.filter(etudiant=self.request.user)
        quiz_filter = self.request.GET.get("quiz")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        if quiz_filter:
            qs = qs.filter(quiz__pk=quiz_filter)
        if date_from:
            qs = qs.filter(date_debut__date__gte=date_from)
        if date_to:
            qs = qs.filter(date_debut__date__lte=date_to)
        return qs.order_by("-date_debut")

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **_role_flags(self.request),
            "quizzes": Quiz.objects.filter(classe__in=self.request.user.classes.all()),
            "filter_vals": {
                "quiz": self.request.GET.get("quiz", ""),
                "date_from": self.request.GET.get("date_from", ""),
                "date_to": self.request.GET.get("date_to", ""),
            },
        }


# ------------------------------------------------------------------
# Sessions Enseignant + export CSV
# ------------------------------------------------------------------
class TeacherSessionListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = QuizSession
    template_name = "quiz/teacher/session_list.html"
    context_object_name = "sessions"
    paginate_by = 20

    def get_queryset(self):
        return QuizSession.objects.filter(
            quiz__enseignant=self.request.user
        ).order_by("-date_debut")

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), **_role_flags(self.request)}


class TeacherSessionExportCSV(LoginRequiredMixin, TeacherRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="sessions.csv"'
        writer = csv.writer(response)
        writer.writerow(["Quiz", "Étudiant", "Date début", "Date fin", "Score (%)"])

        for s in QuizSession.objects.filter(
            quiz__enseignant=request.user
        ).order_by("-date_debut"):
            writer.writerow(
                [
                    s.quiz.titre,
                    s.etudiant.username,
                    s.date_debut.strftime("%Y-%m-%d %H:%M"),
                    s.date_fin.strftime("%Y-%m-%d %H:%M") if s.date_fin else "",
                    f"{s.score:.2f}",
                ]
            )
        return response
