# quiz/urls.py
from django.urls import path
from . import views

app_name = "quiz"

urlpatterns = [
    # --------------------------------------------------
    # ACCUEIL & INSCRIPTION
    # --------------------------------------------------
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),

    # --------------------------------------------------
    # TABLEAU DE BORD – ENSEIGNANT
    # --------------------------------------------------
    path("teacher/dashboard/", views.teacher_dashboard, name="teacher_dashboard"),

    # ---------- Classes (CRUD)
    path("teacher/classes/", views.ClassListView.as_view(), name="class_list"),
    path("teacher/classes/create/", views.ClassCreateView.as_view(), name="class_create"),
    path("teacher/classes/<int:pk>/edit/", views.ClassUpdateView.as_view(), name="class_edit"),
    path("teacher/classes/<int:pk>/delete/", views.ClassDeleteView.as_view(), name="class_delete"),

    # ---------- Quiz (CRUD)
    path("teacher/quizzes/", views.QuizListView.as_view(), name="quiz_list"),
    path("teacher/quizzes/create/", views.QuizCreateView.as_view(), name="quiz_create"),
    path("teacher/quizzes/<int:pk>/edit/", views.QuizUpdateView.as_view(), name="quiz_edit"),
    path("teacher/quizzes/<int:pk>/delete/", views.QuizDeleteView.as_view(), name="quiz_delete"),

    # ---------- Questions (CRUD) liées à un quiz
    # liste + ajout d’une question
    path(
        "teacher/quizzes/<int:quiz_pk>/questions/",
        views.QuestionListView.as_view(),
        name="question_list",
    ),
    path(
        "teacher/quizzes/<int:quiz_pk>/questions/create/",
        views.QuestionCreateView.as_view(),
        name="question_create",
    ),
    # modification / suppression d’une question existante
    path(
        "teacher/questions/<int:pk>/edit/",
        views.QuestionUpdateView.as_view(),
        name="question_edit",
    ),
    path(
        "teacher/questions/<int:pk>/delete/",
        views.QuestionDeleteView.as_view(),
        name="question_delete",
    ),

    # ---------- Sessions enseignant & export CSV
    path("teacher/sessions/", views.TeacherSessionListView.as_view(), name="teacher_session_list"),
    path("teacher/sessions/export/", views.TeacherSessionExportCSV.as_view(), name="teacher_session_export"),

    # --------------------------------------------------
    # TABLEAU DE BORD – ÉTUDIANT
    # --------------------------------------------------
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    path("student/quizzes/", views.StudentQuizListView.as_view(), name="student_quiz_list"),

    # ---------- Passer un quiz & voir le résultat
    path("student/quizzes/<int:pk>/take/", views.QuizTakeView.as_view(), name="quiz_take"),
    path("student/quizzes/session/<int:pk>/result/", views.QuizResultView.as_view(), name="quiz_result"),

    # ---------- Historique des sessions étudiant
    path("student/sessions/", views.StudentSessionListView.as_view(), name="student_session_list"),
]
