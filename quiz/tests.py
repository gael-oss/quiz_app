from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import Classe, Quiz, Question, Choice, QuizSession

class AccessControlTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Création des groupes
        cls.teacher_group = Group.objects.create(name='Enseignant')
        cls.student_group = Group.objects.create(name='Etudiant')
        # Utilisateurs
        cls.teacher = User.objects.create_user(username='prof', password='pw')
        cls.teacher.groups.add(cls.teacher_group)
        cls.student = User.objects.create_user(username='etudiant', password='pw')
        cls.student.groups.add(cls.student_group)

    def setUp(self):
        self.client = Client()

    def test_teacher_dashboard_access(self):
        url = reverse('quiz:teacher_dashboard')
        # Anonyme → redirection vers login
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Étudiant → 403 Forbidden
        self.client.login(username='etudiant', password='pw')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        # Enseignant → 200 OK
        self.client.logout()
        self.client.login(username='prof', password='pw')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_student_dashboard_access(self):
        url = reverse('quiz:student_dashboard')
        # Anonyme → 302
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Enseignant → 403
        self.client.login(username='prof', password='pw')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        # Étudiant → 200
        self.client.logout()
        self.client.login(username='etudiant', password='pw')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class CRUDViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher_group = Group.objects.create(name='Enseignant')
        cls.teacher = User.objects.create_user(username='prof2', password='pw')
        cls.teacher.groups.add(cls.teacher_group)

    def setUp(self):
        self.client = Client()
        self.client.login(username='prof2', password='pw')

    def test_class_crud(self):
        # Création
        response = self.client.post(reverse('quiz:class_create'), {'nom': 'ClasseTest'})
        self.assertRedirects(response, reverse('quiz:class_list'))
        self.assertTrue(Classe.objects.filter(nom='ClasseTest').exists())
        classe = Classe.objects.get(nom='ClasseTest')
        # Modification
        response = self.client.post(reverse('quiz:class_edit', args=[classe.pk]), {'nom': 'ClasseModif'})
        self.assertRedirects(response, reverse('quiz:class_list'))
        classe.refresh_from_db()
        self.assertEqual(classe.nom, 'ClasseModif')
        # Suppression
        response = self.client.post(reverse('quiz:class_delete', args=[classe.pk]))
        self.assertRedirects(response, reverse('quiz:class_list'))
        self.assertFalse(Classe.objects.filter(pk=classe.pk).exists())

    def test_csv_export(self):
        response = self.client.get(reverse('quiz:teacher_session_export'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="sessions.csv"', response['Content-Disposition'])

class QuizFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Groupes et utilisateurs
        teacher_group = Group.objects.create(name='Enseignant')
        student_group = Group.objects.create(name='Etudiant')
        teacher = User.objects.create_user(username='tflow', password='pw')
        teacher.groups.add(teacher_group)
        student = User.objects.create_user(username='sflow', password='pw')
        student.groups.add(student_group)
        # Classe et quiz
        cls.classe = Classe.objects.create(nom='FlowClass', enseignant=teacher)
        cls.quiz = Quiz.objects.create(
            titre='FlowQuiz',
            description='',
            classe=cls.classe,
            enseignant=teacher
        )
        # Question et choix
        question = Question.objects.create(quiz=cls.quiz, texte='1+1=?')
        Choice.objects.create(question=question, texte='1', is_correct=False)
        Choice.objects.create(question=question, texte='2', is_correct=True)

    def setUp(self):
        self.client = Client()

    def test_quiz_pass_and_result(self):
        # Connexion étudiant
        self.client.login(username='sflow', password='pw')
        # Passage du quiz
        correct_choice = Choice.objects.get(is_correct=True)
        response = self.client.post(
            reverse('quiz:quiz_take', args=[self.quiz.pk]),
            {f'question_{correct_choice.question.pk}': correct_choice.pk}
        )
        # Vérifier redirection vers résultat
        session = QuizSession.objects.get(quiz=self.quiz, etudiant__username='sflow')
        self.assertRedirects(response, reverse('quiz:quiz_result', args=[session.pk]))
        # Vérifier score et historique
        response = self.client.get(reverse('quiz:student_session_list'))
        self.assertContains(response, f"{session.score:.2f}")
