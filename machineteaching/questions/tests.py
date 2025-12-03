import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright
from django.conf import settings
from django.contrib.auth.models import User, Group
from .models import (Chapter, Problem, ExerciseSet, OnlineClass, UserLog, Solution, UserLogView,
                     #UserLogError, UserProfile, 
                     Professor, OnlineClass, Language, TestCase as ProblemTestCase,
                     Evaluation, EvaluationProblem, UserEvaluation, UserEvaluationProblem, EvaluationProblemTestCase)
from django.test.utils import override_settings
from django.test import TestCase#, TransactionTestCase
#from django.db import transaction
from datetime import datetime, timedelta
from django.utils import timezone
from django.test import Client
from django.urls import reverse
from unittest.mock import patch, Mock
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import json 

global USER_CLASS

@override_settings(DEBUG=True)
class DjkSampleTestCase(StaticLiveServerTestCase):
    reset_sequences = False

class InterfaceTests(DjkSampleTestCase):

    @classmethod
    def setUpClass(cls): 
        super().setUpClass() 
        cls.playwright = sync_playwright().start() 
        headless = True     # False to show browser while testing
        cls.browser = cls.playwright.chromium.launch(headless=headless) 
        User.objects.create_superuser(username=settings.TEST_SUPERUSER_USER, email=settings.TEST_SUPERUSER_EMAIL, password=settings.TEST_SUPERUSER_PASSWORD)
 
    @classmethod 
    def tearDownClass(cls): 
        cls.browser.close() 
        cls.playwright.stop() 
        super().tearDownClass() 
    
    def about(self, page):
        page.goto(f"{self.live_server_url}/pt-br")
        page.click('.footer-right span:nth-child(3)')
        self.assertEqual('Sobre a pesquisa', page.locator('.about_content h3:first-of-type').text_content())

    def change_language(self, page):
        page.goto(f"{self.live_server_url}/pt-br")
        page.click('.change-language')
        page.wait_for_selector('.landing h1:has-text("Welcome to  Machine Teaching")')
        self.assertEqual('Welcome to  Machine Teaching', page.locator('.landing h1').text_content())
        page.click('.change-language')
        page.wait_for_selector('.landing h1:has-text("Bem-vindo ao Machine Teaching")') 
        self.assertEqual('Bem-vindo ao Machine Teaching',page.locator('.landing h1').text_content())

    def read_terms(self, page):
        page.goto(f"{self.live_server_url}/pt-br")
        page.click('.footer-right span:nth-child(1)')
        self.assertEqual('Termos e condições', page.locator('.bg2 .card h3').text_content())

    def read_privacy(self, page):
        page.goto(f"{self.live_server_url}/pt-br")
        page.click('.footer-right span:nth-child(2)')
        self.assertEqual('Política de privacidade', page.locator('.bg2 .card h3').text_content())

    def register(self, page, class_code, gname, sname, user, password):
        page.goto(f"{self.live_server_url}/pt-br/signup")
        page.fill('form[action="/pt-br/signup"] input[name="first_name"]', gname)
        page.fill('form[action="/pt-br/signup"] input[name="last_name"]', sname)
        page.fill('form[action="/pt-br/signup"] input[name="email"]', user)
        page.fill('form[action="/pt-br/signup"] input[name="class_code"]', class_code)
        page.fill('form[action="/pt-br/signup"] input[name="university"]', 'UFRJ')
        page.fill('form[action="/pt-br/signup"] input[name="registration"]', '123456789')
        page.locator("#id_course").select_option('Astronomia')
        page.fill('form[action="/pt-br/signup"] input[name="password1"]', password)
        page.fill('form[action="/pt-br/signup"] input[name="password2"]', password)
        page.locator('form[action="/pt-br/signup"] input[name="accepted"]').check()
        page.locator('form[action="/pt-br/signup"] input[name="read"]').check()
        page.click('form[action="/pt-br/signup"] button[type="submit"]')

        self.assertEqual("início", page.locator('.content .topbar-left .title').text_content())

    def login(self, page, user, password):
        page.set_default_timeout(0)
        page.goto(f"{self.live_server_url}/pt-br/accounts/login/?next=/pt-br/start")
        page.fill('form[action="/pt-br/accounts/login/"] input[name="username"]', user)
        page.fill('form[action="/pt-br/accounts/login/"] input[name="password"]', password)
        page.click('form[action="/pt-br/accounts/login/"] button[type="submit"]')
        page.goto(f"{self.live_server_url}/pt-br/start")
        self.assertEqual("início", page.locator('.content .topbar-left .title').text_content())

    ### não está sendo usada
    def next(self, page):
        page.goto(f"{self.live_server_url}/pt-br/next")
        self.assertEqual("Problema", page.locator('.content .topbar-left .title').text_content())
    
    def outcomes(self, page):
        page.goto(f"{self.live_server_url}/pt-br/dashboard")
        self.assertEqual("Problemas", page.locator('.layout-content .col.col-6 .col-7 .card h3').text_content())

    def past_chapters(self, page):
        page.goto(f"{self.live_server_url}/pt-br/past_problems")
        self.assertEqual("Problemas passados", page.locator('.content .topbar-left .title').text_content())

    def chapters(self, page):
        page.goto(f"{self.live_server_url}/pt-br/chapters")
        self.assertEqual("Aulas", page.locator('.content .topbar-left .title').text_content())

    def specific_chapter(self, page, id_to_find):
        page.goto(f"{self.live_server_url}/pt-br/chapters/{id_to_find}")
        self.assertEqual("Problemas", page.locator('.layout-content .col.col-7 .card.chapter-list h3').text_content())
    
    def specific_problem(self, page, id_to_find):
        page.goto(f"{self.live_server_url}/pt-br/chapters/{id_to_find}")
        self.assertEqual("Progresso", page.locator('text=Progresso').text_content())
    
    def specific_problem_2(self, page, id_to_find):
        page.goto(f"{self.live_server_url}/pt-br/chapters/{id_to_find}")
        self.assertEqual("Data de entrega", page.locator('text=Entrega').text_content())

    def past_solutions(self, page):
        id_to_find = Problem.objects.first().id
        page.goto(f"{self.live_server_url}/pt-br/problem_solutions/{id_to_find}")
        self.assertEqual("Problema atual", page.locator('text=Problema atual').text_content())

    def create_professor(self, page):
        page.goto(f"{self.live_server_url}/pt-br/admin/")
        page.fill('#id_username', settings.TEST_SUPERUSER_EMAIL)
        page.fill('#id_password', settings.TEST_SUPERUSER_PASSWORD)
        page.click('input[type="submit"]')
        page.click('text=Grupos')
        page.click('text=Adicionar grupo')
        page.fill('#id_name', 'Professor')
        page.click('text=Escolher todos')
        page.click('text=Salvar')
        Professor.objects.create(user=User.objects.get(username=settings.TEST_MANAGER))

    def exercise(self, page):
        id_to_find = Problem.objects.first().id
        page.goto(f"{self.live_server_url}/pt-br/{id_to_find}")
        self.assertEqual("Exercicio_Teste", page.locator('text=Exercicio_Teste Pular >> h3').text_content())
        self.write_code(page)
        self.assertEqual("Casos de teste", page.locator('text=Casos de teste').text_content())
        self.write_terminal(page)
        self.assertEqual("oi", page.locator(("text=oi >> nth=0")).text_content())
    
    
    def write_code(self, page):
        #page.locator("text=xxxxxxxxxx 1#Start your python function here >> div[role='presentation']").click()
        page.keyboard.press("Enter")
        page.keyboard.type("def oi():")
        page.keyboard.press("Enter")
        page.keyboard.type("    return 'oi'")
        page.click('text=Executar')
        time.sleep(5)

    def write_terminal(self, page):
        page.locator("div:nth-child(2) > .CodeMirror > .CodeMirror-scroll > .CodeMirror-sizer > div > .CodeMirror-lines > div > .CodeMirror-code").click()
        page.keyboard.type("print('oi')")
        page.click('text=Executar')
        time.sleep(5)

    def password_reset(self, page):
        page.goto(f"{self.live_server_url}/pt-br/accounts/login/?next=/pt-br/start")
        page.click('text=Esqueceu a senha?')
        page.fill('input#id_email', 'hugofg@dcc.ufrj.br')
        page.click("text=Enviar")
        self.assertEqual("Enviamos por e-mail instruções para redefinir sua senha, se existir uma conta com o e-mail que você digitou. Você deve recebê-las em breve.", page.locator('text=Enviamos por e-mail instruções para redefinir sua senha, se existir uma conta com o e-mail que você digitou. Você deve recebê-las em breve.').text_content().strip())

    def class_dashboard(self, page, id_to_find):  
        page.goto(f"{self.live_server_url}/pt-br/classes/dashboard/{id_to_find}")
        self.assertEqual("Progresso da turma", page.locator('text=Progresso da turma').text_content())

    def logout(self, page):
        page.get_by_text("Olá, Usuário Teste").hover()
        page.click("text=Sair")
        self.assertEqual("Bem-vindo ao Machine Teaching", page.locator('text=Bem-vindo ao Machine Teaching').text_content())

    def create_class(self, page):
        page.goto(f"{self.live_server_url}/pt-br/classes")
        page.fill('form[action="/pt-br/classes"] input[name="name"]', 'Turma_Teste')
        page.click("text=Criar")
        time.sleep(1)
        page.goto(f"{self.live_server_url}/pt-br/classes")
        self.assertEqual("Turma_Teste", page.locator('text=Turma_Teste').text_content())
        return page.locator('.class_code').text_content()

    def create_chapter(self, page):
        page.goto(f"{self.live_server_url}/pt-br/chapters")
        page.fill('form[action="/pt-br/new_chapter"] input[name="label"]', 'Aula_Teste')
        page.fill('form[action="/pt-br/new_chapter"] input[type="date"]', '2024-12-12')
        page.click('form[action="/pt-br/new_chapter"] button[type="submit"]') 
        page.click("text=+ Adicionar problema")

        page.keyboard.press("Enter")
        page.keyboard.press("Enter")        
        page.keyboard.press("Enter")        
        page.keyboard.press("Enter")        

        solution = """def Header_Teste(num):
                return num"""
        time.sleep(1)
        page.keyboard.type(solution)
        page.fill('form[action="/pt-br/new"] input[name="title"]', 'Exercicio_Teste')
        page.fill('form[action="/pt-br/new"] input[name="header"]', 'Header_Teste')
        page.fill('form[action="/pt-br/new"] input[name="order"]', '1')
        page.click("text=Adicionar problema")

    def professor_creates_exam(self, page, id_to_find):
        page.goto(f"{self.live_server_url}/pt-br/classes/manage/{id_to_find}")
        page.click(f"a[href='/pt-br/classes/manage/{id_to_find}/evaluations/new/']")
        
        exam_title = 'Prova Final de Teste'
        page.fill('input[name="title"]', exam_title)
        now = timezone.now()
        start_time = now - timedelta(hours=3)
        end_time = now - timedelta(hours=3) + timedelta(minutes=2)
        page.fill('input[name="start_date"]', start_time.strftime('%Y-%m-%dT%H:%M'))
        page.fill('input[name="end_date"]', end_time.strftime('%Y-%m-%dT%H:%M'))
        page.click('button[type="submit"]:has-text("Criar")')
        
        page.wait_for_selector(f'h3:has-text("{exam_title}")')
        self.assertEqual(exam_title, page.locator('h3').first.text_content())

    def professor_creates_question_in_exam(self, page):
        page.click('a#create_question')
        page.fill('input#id_title', 'Soma')
        page.fill('textarea#id_content', 'Escreva uma função que some dois números.')
        page.click('input#id_locked_problem')
        page.click('input#id_solution_header')
        page.fill('input#id_solution_header', 'soma')
        page.select_option('select#id_language', 'Python')
        page.click('label#solution-label')
        page.keyboard.type('def soma(a, b):')
        page.keyboard.press("Enter")
        page.keyboard.type("    return a + b")
        page.click('label#test-case-label')
        page.keyboard.type("def generate():")
        page.keyboard.press("Enter")
        page.keyboard.type("    return [( 1, 2 )]")
        page.click('button:has-text("Create Question")')        
        page.wait_for_selector(f'.question-item h6:has-text("Soma")')
        self.assertEqual(1, page.locator('.question-item').count())
        page.click('button:has-text("Configure Test Cases")')
        checkbox = page.locator('input.use-tc-checkbox')
        if not checkbox.is_checked():
            checkbox.check()
        page.click('button:has-text("Save Changes")')

    def professor_adds_question_to_exam(self, page):
        page.fill('input[name="q"]', 'Exercicio_Teste')
        page.click('button:has-text("Pesquisar")')
        page.wait_for_selector(f'li:has-text("Exercicio_Teste")')
        page.click(f'li:has-text("Exercicio_Teste") button:has-text("Adicionar")')

        page.wait_for_selector(f'.question-item h6:has-text("Exercicio_Teste")')
        self.assertEqual(2, page.locator('.question-item').count())
        page.click('button:has-text("Confirm")')

    def student_starts_exam(self, page):
        page.wait_for_selector('.modal-dialog', state='visible')
        page.click('a:has-text("Go to Exam")')
        
        page.wait_for_selector('h2:has-text("Prova Final de Teste")')
        page.click('button:has-text("I understand, Start Exam")')
        
        page.wait_for_selector('h3:has-text("Prova Final de Teste")')
        self.assertTrue(page.locator("#countdown-timer").is_visible())

    def student_solves_coding_problem(self, page):
        page.click('a:has-text("Go to Question")')
        
        page.wait_for_selector(f'h4:has-text("Soma")')
        page.locator('.CodeMirror').click()
        page.keyboard.type("def soma(a,b):")
        page.keyboard.press("Enter")
        page.keyboard.type("    return a + b")
        page.click('button#run-code-btn')
        
        page.wait_for_selector('.badge.bg-success')
        self.assertEqual('P', page.locator('.badge.bg-success').text_content())

    def student_submits_exam(self, page):
        page.click('a:has-text("Back to Question List")')
        page.wait_for_selector('button#open-submit-modal-btn')
        page.click('button#open-submit-modal-btn')
        page.locator('input#confirm-unanswered-check').check()
        page.click('button#final-submit-btn')
        
        page.wait_for_selector('h2.text-success')
        self.assertEqual('Exam Submitted Successfully!', page.locator('h2.text-success').text_content())

    def professor_runs_autograder(self, page, class_id):
        id_to_find = Evaluation.objects.first().id
        Evaluation.objects.filter(id = id_to_find).update(start_date=timezone.now() - timedelta(hours=1), end_date=timezone.now() - timedelta(minutes=59)) # Troca a data da prova para o professor poder ver o dashboard
        page.goto(f"{self.live_server_url}/pt-br/evaluations/manage/{id_to_find}/")
        page.click('a:has-text("Grading Dashboard")')
        page.on("dialog", lambda dialog: dialog.accept())
        page.click('button:has-text("Run Auto-Grader")')
        page.wait_for_selector('button:has-text("Auto-Grader Run")')
        

    def professor_manually_grades(self, page,):
        page.click('a:has-text("Grade Submission")')
        page.wait_for_selector('h3:has-text("Usuário Teste")')
        page.click('a:has-text("Grade Question")')
        
        page.wait_for_selector(f'h4:has-text("Soma")')
        page.fill('input[type=range]', '0.75')
        page.fill('textarea[name="feedback"]', 'Bom trabalho!')
        page.click('button:has-text("Salvar")')

    def professor_releases_grades(self, page):
        page.wait_for_selector('h3:has-text("Usuário Teste")')
        page.click('a:has-text("Back to Dashboard")')
        page.wait_for_selector('h2:has-text("Prova Final de Teste")')
        page.click('button:has-text("Release Grades")')
        
        page.wait_for_selector('button:disabled:has-text("Grades Released")')
        self.assertTrue(page.locator('button:disabled:has-text("Grades Released")').is_visible())


    def test_user(self):
        page = self.browser.new_page()
        page.set_default_timeout(10000)

        print("\n      - Testando mudança de linguagem...")
        self.change_language(page)

        print("      - Testando sobre...")
        self.about(page)

        print("      - Testando termos de uso...")
        self.read_terms(page)

        print("      - Testando termos de privacidade...")
        self.read_privacy(page)

        OnlineClass.objects.create(name='turma', start_date='2024-01-01')
        default_class = OnlineClass.objects.get(name='turma').class_code

        print("      - Testando criação de professor e aula...")
        self.register(page, default_class, settings.TEST_GNAME, settings.TEST_SNAME, settings.TEST_MANAGER, settings.TEST_PASSWORD)
        self.create_professor(page)
        self.login(page, settings.TEST_MANAGER, settings.TEST_PASSWORD)
        class_code = self.create_class(page)
        class_id = OnlineClass.objects.get(class_code=class_code).id
        self.create_chapter(page)
        self.logout(page)


        print("      - Testando criação de aluno...")
        self.register(page, class_code, settings.TEST_GNAME, settings.TEST_SNAME, settings.TEST_USER, settings.TEST_PASSWORD)

        print("      - Testando login...")
        self.login(page, settings.TEST_USER, settings.TEST_PASSWORD)

        print("      - Testando resolução de exercício específico...")
        self.exercise(page)

        print("      - Testando entrada do dashboard...")
        self.outcomes(page)

        print("      - Testando vista de capítulos antigos...")
        self.past_chapters( page)

        print("      - Testando vista de todos os capítulos...")
        self.chapters(page)

        print("      - Testando vista de capítulo específico...")
        chapter_id = Chapter.objects.first().id
        self.specific_chapter(page, chapter_id)

        print("      - Testando vista de exercício específico...")
        self.specific_problem(page, chapter_id)
        self.specific_problem_2(page, chapter_id)

        print("      - Testando vista de soluções passadas...")
        self.past_solutions(page)
 
        print("      - Testando troca de senha...")
        self.password_reset(page)

        self.login(page, settings.TEST_MANAGER, settings.TEST_PASSWORD)
        self.class_dashboard(page, class_id)

        print("      - Testando professor criando exame...")
        self.professor_creates_exam(page, class_id)
        
        print("      - Testando professor adicionar questão ao exame...")
        self.professor_creates_question_in_exam(page)
        self.professor_adds_question_to_exam(page)
        self.logout(page)

        print("      - Testando aluno entrando no exame...")
        self.login(page, settings.TEST_USER, settings.TEST_PASSWORD)        
        self.student_starts_exam(page)
        
        print("      - Testando aluno resolvendo questão no exame...")
        self.student_solves_coding_problem(page)
        self.student_submits_exam(page)
        self.logout(page)

        print("      - Testando professor usando auto-grader...")
        self.login(page, settings.TEST_MANAGER, settings.TEST_PASSWORD)
        self.professor_runs_autograder(page, class_id)
        
        print("      - Testando professor corrigindo manualmente...")
        self.professor_manually_grades(page)
        
        print("      - (Professor) Liberando as notas...")
        self.professor_releases_grades(page)

        page.close()

class BackendTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_create_professor(self):
        Group.objects.get_or_create(name='Professor')

        professor_user = User.objects.create(
            username=settings.TEST_MANAGER,
            email=settings.TEST_MANAGER,
            password=settings.TEST_PASSWORD
        )

        professor = Professor.objects.create(user=professor_user)

        self.assertEqual(professor.user.username, settings.TEST_MANAGER)
        
    def test_create_user(self):
        user = User.objects.create(
            username=settings.TEST_USER,
            email=settings.TEST_USER,
            password=settings.TEST_PASSWORD
        )

        self.assertEqual(user.username, settings.TEST_USER)

    def test_chapter_creation(self):
        chapter = Chapter.objects.create(label='Chapter 1')
        self.assertEqual(chapter.label, 'Chapter 1')

    def test_problem_creation(self):
        problem = Problem.objects.create(
            question_type='C',
            title='Test Problem',
            content='Solve this problem',
            options='',
            difficulty='easy',
            hint='Think about loops'
        )
        self.assertEqual(problem.title, 'Test Problem')

    def test_exercise_set_creation(self):
        chapter = Chapter.objects.create(label='Chapter 1')
        problem = Problem.objects.create(
            question_type='C',
            title='Test',
            content='Testing'
        )
        exercise_set = ExerciseSet.objects.create(
            chapter=chapter,
            problem=problem,
            order=1
        )

        self.assertEqual(exercise_set.chapter.label, 'Chapter 1')
        self.assertEqual(exercise_set.problem.title, 'Test')

    def test_online_class_creation(self):
        online_class = OnlineClass.objects.create(
            name='Test Class',
            class_code='ABC123',
            active=True,
            start_date='2023-01-01'
        )

        self.assertEqual(online_class.name, 'Test Class')
        self.assertTrue(online_class.active)

    def test_user_solves_problem(self):
        user = User.objects.create(
            username=settings.TEST_USER,
            email=settings.TEST_USER,
            password=settings.TEST_PASSWORD
        )
        
        problem = Problem.objects.create(
            question_type='C',
            title='Test',
            content='Testing'
        )

        online_class = OnlineClass.objects.create(
            name='Test',
            class_code='ZZZ-ZZZ-ZZZZ',
            active=True,
            start_date='2024-01-01'
        )

        UserLog.objects.create(
            user=user,
            problem=problem,
            solution='print("Hello, world!")',
            outcome='P',
            seconds_in_code=60,
            seconds_in_page=120,
            seconds_to_begin=10,
            solution_lines=1,
            user_class=online_class
        )

        self.assertEqual(UserLog.objects.count(), 1)
        log = UserLog.objects.first()
        self.assertEqual(log.user, user)
        self.assertEqual(log.problem, problem)
        self.assertEqual(log.outcome, 'P')

    def test_evaluation_creation(self):
        online_class = OnlineClass.objects.create(name='Test Class', start_date=datetime.now().date())
        evaluation = Evaluation.objects.create(
            title='Final Exam',
            online_class=online_class,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=2)
        )
        self.assertEqual(Evaluation.objects.count(), 1)
        self.assertEqual(evaluation.title, 'Final Exam')
        self.assertEqual(evaluation.online_class, online_class)

    def test_evaluation_problem_creation(self):
        online_class = OnlineClass.objects.create(name='Test Class', start_date=datetime.now().date())
        evaluation = Evaluation.objects.create(title='Midterm', online_class=online_class, start_date=timezone.now(), end_date=timezone.now())
        problem = Problem.objects.create(title='Test Problem', content='Content')
        eval_problem = EvaluationProblem.objects.create(
            evaluation=evaluation,
            problem=problem,
            order=1,
            weight=2.5
        )
        self.assertEqual(eval_problem.evaluation, evaluation)
        self.assertEqual(eval_problem.problem, problem)
        self.assertEqual(eval_problem.weight, 2.5)

    def test_user_evaluation_session_creation(self):
        user = User.objects.create_user(username='testuser', password='password')
        online_class = OnlineClass.objects.create(name='Test Class', start_date=datetime.now().date())
        evaluation = Evaluation.objects.create(title='Quiz 1', online_class=online_class, start_date=timezone.now(), end_date=timezone.now())
        user_eval = UserEvaluation.objects.create(
            user=user,
            evaluation=evaluation
        )
        self.assertEqual(user_eval.user, user)
        self.assertEqual(user_eval.evaluation, evaluation)
        self.assertFalse(user_eval.submitted)
        self.assertEqual(user_eval.score, 0.0)

    def test_user_evaluation_problem_creation(self):
        user = User.objects.create_user(username='testuser', password='password')
        online_class = OnlineClass.objects.create(name='Test Class', start_date=datetime.now().date())
        evaluation = Evaluation.objects.create(title='Quiz 1', online_class=online_class, start_date=timezone.now(), end_date=timezone.now())
        problem = Problem.objects.create(title='Test Problem', content='Content')
        user_eval = UserEvaluation.objects.create(user=user, evaluation=evaluation)
        eval_problem = EvaluationProblem.objects.create(evaluation=evaluation, problem=problem, order=1)
        
        user_eval_problem = UserEvaluationProblem.objects.create(
            user_evaluation=user_eval,
            evaluation_problem=eval_problem
        )
        self.assertEqual(user_eval_problem.user_evaluation, user_eval)
        self.assertEqual(user_eval_problem.solution, "")
        self.assertIsNone(user_eval_problem.grade)

class EvaluationCoverageTests(TestCase):

    def setUp(self):
        self.online_class = OnlineClass.objects.create(name='Turma de Teste Cobertura', start_date=timezone.now().date())

        self.professor_user = User.objects.create_user(username='prof_eval', email='prof@eval.com', password='123', first_name='Professor')
        self.professor_user.is_staff = True
        self.professor_user.save()
        
        self.professor_group, _ = Group.objects.get_or_create(name='Professor')
        
        content_type_eval = ContentType.objects.get_for_model(Evaluation)
        content_type_prob = ContentType.objects.get_for_model(Problem)
        content_type_logview = ContentType.objects.get_for_model(UserLogView)
        
        perm_add_eval = Permission.objects.get(content_type=content_type_eval, codename='add_evaluation')
        perm_change_eval = Permission.objects.get(content_type=content_type_eval, codename='change_evaluation')
        perm_view_eval = Permission.objects.get(content_type=content_type_eval, codename='view_evaluation')
        perm_view_prob = Permission.objects.get(content_type=content_type_prob, codename='view_problem')
        perm_add_prob = Permission.objects.get(content_type=content_type_prob, codename='add_problem')
        perm_view_logview = Permission.objects.get(content_type=content_type_logview, codename='view_userlogview')

        self.professor_group.permissions.add(
            perm_add_eval, perm_change_eval, perm_view_eval, 
            perm_view_prob, perm_add_prob, perm_view_logview
        )

        self.professor_user.groups.add(self.professor_group)
        self.professor = Professor.objects.create(user=self.professor_user)
        self.professor.prof_class.add(self.online_class)
        self.professor_client = Client()
        self.professor_client.force_login(self.professor_user)

        self.student_user = User.objects.create_user(username='aluno_eval', email='aluno@eval.com', password='123', first_name='Aluno')
        self.student_user.userprofile.user_class = self.online_class
        self.student_user.userprofile.save()
        
        self.student_client = Client()
        self.student_client.force_login(self.student_user)
        
        self.now = timezone.now()
        self.evaluation = Evaluation.objects.create(
            title='Prova de Cobertura',
            online_class=self.online_class,
            start_date=self.now,
            end_date=self.now + timedelta(hours=2)
        )
        
        self.python_lang, _ = Language.objects.get_or_create(name='Python')
        self.problem = Problem.objects.create(title='Soma', content='Faça uma soma', question_type='C')
        self.solution = Solution.objects.create(
            problem=self.problem, 
            content='def soma(a, b): return a + b', 
            header='soma',
            language=self.python_lang
        )
        self.eval_problem = EvaluationProblem.objects.create(
            evaluation=self.evaluation,
            problem=self.problem,
            order=1,
            weight=10.0,
            language=self.python_lang
        )

        self.problem2 = Problem.objects.create(title='Problem 2', content='Content 2', question_type='C', locked_problem=False)
        self.solution2 = Solution.objects.create(problem=self.problem2, content='pass', language=self.python_lang)
            
        self.tc1 = ProblemTestCase.objects.create(problem=self.problem, content='[1, 2]')
        self.tc2 = ProblemTestCase.objects.create(problem=self.problem, content='[3, 4]')

    def test_student_cannot_access_manage_evaluation(self):
        url = reverse('manage_evaluation', args=[self.evaluation.id])
        response = self.student_client.get(url)
 
        self.assertNotEqual(response.status_code, 200)

    def test_professor_cannot_manage_other_class_evaluation(self):
        other_class = OnlineClass.objects.create(name='Outra Turma', start_date=timezone.now().date())
        other_prof_user = User.objects.create_user(username='other_prof', password='123')
        other_prof_user.is_staff = True
        other_prof_user.save()
        other_prof = Professor.objects.create(user=other_prof_user)
        other_prof.prof_class.add(other_class)
        other_prof_client = Client()
        other_prof_client.force_login(other_prof_user)

        url = reverse('manage_evaluation', args=[self.evaluation.id])
        response = other_prof_client.get(url)
        self.assertEqual(response.status_code, 403)


    def test_create_evaluation_invalid_form(self):
        url = reverse('create_evaluation', args=[self.online_class.id])
        form_data = {
            'title': 'Prova Inválida'
        }
        response = self.professor_client.post(url, data=form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Houve um erro no formulário') 
        self.assertFalse(Evaluation.objects.filter(title='Prova Inválida').exists()) 

    def test_student_cannot_start_exam_outside_time(self):
        self.evaluation.start_date = self.now + timedelta(days=1)
        self.evaluation.end_date = self.now + timedelta(days=1, hours=2)
        self.evaluation.save()
        
        url = reverse('start_exam', args=[self.evaluation.id])
        response = self.student_client.post(url)
        
        self.assertRedirects(response, reverse('start')) 
        self.assertFalse(UserEvaluation.objects.filter(user=self.student_user, evaluation=self.evaluation).exists())

    def test_student_cannot_submit_exam_after_grace_period(self):
        user_eval = UserEvaluation.objects.create(user=self.student_user, evaluation=self.evaluation)
        
        with patch('django.utils.timezone.now', return_value=self.now + timedelta(hours=3)):
            url = reverse('submit_exam', args=[user_eval.id])
            response = self.student_client.post(url)
        
        user_eval.refresh_from_db()
        self.assertRedirects(response, reverse('start'))
        self.assertFalse(user_eval.submitted)

    @override_settings(WORKER_NODE_HOST='http://test.worker', WORKER_NODE_PORT='')
    @patch('questions.views.requests.post')
    def test_run_autograder_logic(self, mock_requests_post):
        user_eval = UserEvaluation.objects.create(
            user=self.student_user, 
            evaluation=self.evaluation,
            submitted=True
        )
        uep = UserEvaluationProblem.objects.create(
            user_evaluation=user_eval,
            evaluation_problem=self.eval_problem,
            solution='def soma(a, b): return a + b'
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_response_json = [
            {
                'result': {
                    'isCorrect': True,
                    'test_case': '[1, 2]'
                }
            },
        ]
        mock_response.json.return_value = mock_response_json
        mock_requests_post.return_value = mock_response

        test_case_content = '[1, 2]'
        test_case = ProblemTestCase.objects.create(problem=self.problem, content=test_case_content)
        EvaluationProblemTestCase.objects.create(
            evaluation_problem=self.eval_problem,
            test_case=test_case,
            weight=1.0 
        )

        url = reverse('run_autograder', args=[self.evaluation.id])
        response = self.professor_client.post(url)

        uep.refresh_from_db()
        user_eval.refresh_from_db()
        
        mock_requests_post.assert_called_once()
        
        self.evaluation.refresh_from_db()
        self.assertTrue(self.evaluation.graded)
        
        self.assertEqual(uep.grade, 10.0)
        self.assertEqual(user_eval.score, 10.0)
        self.assertRedirects(response, reverse('grading_dashboard', args=[self.evaluation.id]))

    @override_settings(WORKER_NODE_HOST='http://test.worker', WORKER_NODE_PORT='')
    @patch('questions.views.requests.post')
    def test_autograder_fails_if_no_solution_object_found(self, mock_requests_post):
        UserEvaluation.objects.create(
            user=self.student_user, 
            evaluation=self.evaluation,
            submitted=True
        )
        UserEvaluationProblem.objects.create(
            user_evaluation=UserEvaluation.objects.get(user=self.student_user),
            evaluation_problem=self.eval_problem,
            solution='def soma(a, b): return a + b'
        )
        
        Solution.objects.all().delete()
        self.assertEqual(Solution.objects.count(), 0)

        url = reverse('run_autograder', args=[self.evaluation.id])
        response = self.professor_client.post(url)
        
        uep = UserEvaluationProblem.objects.get(evaluation_problem=self.eval_problem)
        self.assertIsNone(uep.grade)
        self.assertRedirects(response, reverse('grading_dashboard', args=[self.evaluation.id]))
        
        mock_requests_post.assert_not_called()

    
    def test_export_grades_csv(self):
        UserEvaluation.objects.create(
            user=self.student_user, 
            evaluation=self.evaluation,
            submitted=True,
            score=9.5
        )
        
        url = reverse('export_grades_csv', args=[self.evaluation.id])
        response = self.professor_client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        content = response.content.decode('utf-8')
        self.assertIn('Student Name,Email,Final Score', content)
        self.assertIn(f'{self.student_user.get_full_name()},{self.student_user.email},9.50', content)

    def test_create_evaluation_happy_path(self):
        url = reverse('create_evaluation', args=[self.online_class.id])
        form_data = {
            'title': 'Prova Válida',
            'start_date': (self.now).strftime('%Y-%m-%dT%H:%M'),
            'end_date': (self.now + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
        }
        response = self.professor_client.post(url, data=form_data)
        
        self.assertTrue(Evaluation.objects.filter(title='Prova Válida').exists())
        eval_id = Evaluation.objects.get(title='Prova Válida').id
        self.assertRedirects(response, reverse('manage_evaluation', args=[eval_id]))

    def test_start_exam_happy_path_and_existing_session(self):
        url = reverse('start_exam', args=[self.evaluation.id])
        response = self.student_client.post(url)
        
        self.assertTrue(UserEvaluation.objects.filter(user=self.student_user, evaluation=self.evaluation).exists())
        ue_id = UserEvaluation.objects.get(user=self.student_user).id
        
        self.assertRedirects(response, reverse('take_exam', args=[ue_id]))

        response_again = self.student_client.post(url)
        self.assertRedirects(response_again, reverse('take_exam', args=[ue_id]))

    def test_solve_and_save_progress(self):
        ue = UserEvaluation.objects.create(user=self.student_user, evaluation=self.evaluation)
        uep = UserEvaluationProblem.objects.create(user_evaluation=ue, evaluation_problem=self.eval_problem)

        url_solve = reverse('solve_evaluation_problem', args=[uep.id])
        response_get = self.student_client.get(url_solve)
        self.assertEqual(response_get.status_code, 200)
        self.assertContains(response_get, self.problem.title)

        url_save = reverse('save_evaluation_progress', args=[uep.id])
        solution_data = {'solution': 'def soma(a, b): return a+b'}
        response_post = self.student_client.post(
            url_save, 
            data=json.dumps(solution_data), 
            content_type='application/json'
        )
        self.assertEqual(response_post.status_code, 200)
        self.assertEqual(response_post.json(), {'status': 'success'})
        
        uep.refresh_from_db()
        self.assertEqual(uep.solution, solution_data['solution'])

    def test_professor_grades_and_releases_grades(self):
        ue = UserEvaluation.objects.create(user=self.student_user, evaluation=self.evaluation, submitted=True)
        uep = UserEvaluationProblem.objects.create(user_evaluation=ue, evaluation_problem=self.eval_problem, solution='code')

        url_grade = reverse('grade_evaluation_problem', args=[uep.id])
        
        response_get = self.professor_client.get(url_grade)
        self.assertEqual(response_get.status_code, 200)

        grade_data = {
            'grade': '8.5',
            'feedback': 'Bom trabalho'
        }
        response_post = self.professor_client.post(url_grade, data=grade_data)
        self.assertRedirects(response_post, reverse('grade_student_submission', args=[ue.id]))
        
        uep.refresh_from_db()
        ue.refresh_from_db()
        self.assertEqual(uep.grade, 8.5)
        self.assertEqual(ue.score, 8.5)

        url_release = reverse('release_grades', args=[self.evaluation.id])
        response_release = self.professor_client.post(url_release)
        self.assertRedirects(response_release, reverse('grading_dashboard', args=[self.evaluation.id]))
        
        self.evaluation.refresh_from_db()
        self.assertTrue(self.evaluation.show_grades)

    def test_manage_evaluation_add_question(self):
        url = reverse('manage_evaluation', args=[self.evaluation.id])
        
        add_data = {
            'add_question': 1,
            'problem_id': self.problem2.id
            }
        self.professor_client.post(url, data=add_data)
        self.assertEqual(self.evaluation.evaluationproblem_set.count(), 2)
        self.assertTrue(EvaluationProblem.objects.filter(problem=self.problem2, evaluation=self.evaluation).exists())
    
    def test_manage_evaluation_add_question_twice(self):
        url = reverse('manage_evaluation', args=[self.evaluation.id])
        
        add_data = {
            'add_question': 1,
            'problem_id': self.problem2.id
            }
        
        self.professor_client.post(url, data=add_data)
        self.assertEqual(self.evaluation.evaluationproblem_set.count(), 2)
        
        response = self.professor_client.post(url, data=add_data)
        self.assertRedirects(response, f"{url}?q=")

    def test_manage_evaluation_remove_question(self):
        url = reverse('manage_evaluation', args=[self.evaluation.id])
        remove_data = {'remove_question': self.eval_problem.id}
        response = self.professor_client.post(url, data=remove_data)
        self.assertRedirects(response, reverse('manage_evaluation', args=[self.evaluation.id]))
        self.assertEqual(self.evaluation.evaluationproblem_set.count(), 0)

    def test_manage_evaluation_update_weights(self):
        url = reverse('manage_evaluation', args=[self.evaluation.id])
        update_data = {
            'update_weights': 1,
            f'weight-{self.eval_problem.id}': '5.0',
            f'language-{self.eval_problem.id}': self.python_lang.id
        }
        response = self.professor_client.post(url, data=update_data)
        self.eval_problem.refresh_from_db()
        self.assertEqual(self.eval_problem.weight, 5.0)
        self.assertRedirects(response, reverse('manage_class', args=[self.evaluation.online_class.id]))

    def test_manage_evaluation_update_weights_invalid(self):
        url = reverse('manage_evaluation', args=[self.evaluation.id])
        update_data = {
            'update_weights': 1,
            f'weight-{self.eval_problem.id}': 'not-a-float',
        }
        response = self.professor_client.post(url, data=update_data)
        self.eval_problem.refresh_from_db()
        self.assertRedirects(response, reverse('manage_class', args=[self.evaluation.online_class.id]))
        self.assertEqual(self.eval_problem.weight, 10.0)

    def test_manage_evaluation_cancel(self):
        future_eval = Evaluation.objects.create(
            title='Prova Futura',
            online_class=self.online_class,
            start_date=self.now + timedelta(days=1),
            end_date=self.now + timedelta(days=2)
        )
        url = reverse('manage_evaluation', args=[future_eval.id])
        
        cancel_data = {'cancel_evaluation': 1}
        response = self.professor_client.post(url, data=cancel_data)
        future_eval.refresh_from_db()
        self.assertTrue(future_eval.cancelled)
        self.assertRedirects(response, reverse('manage_class', args=[self.online_class.id]))

        self.evaluation.start_date = self.now - timedelta(days=1)
        self.evaluation.save()
        url_started = reverse('manage_evaluation', args=[self.evaluation.id])
        response_started = self.professor_client.post(url_started, data=cancel_data)
        self.evaluation.refresh_from_db()
        self.assertFalse(self.evaluation.cancelled)
        self.assertRedirects(response_started, reverse('manage_class', args=[self.online_class.id]))


    def test_create_evaluation_problem_get_and_post(self):
        url = reverse('create_evaluation_problem', args=[self.evaluation.id])
        
        response_get = self.professor_client.get(url)
        self.assertEqual(response_get.status_code, 200)

        form_data = {
            'title': 'Nova Questão de Código',
            'content': 'Enunciado...',
            'question_type': 'C',
            'solution_header': 'minha_funcao',
            'solution_content': 'def minha_funcao(a): return a',
            'language': self.python_lang.id,
            'test_case_generator': 'def generate(): return [[1]]'
        }
        response_post = self.professor_client.post(url, data=form_data)
        self.assertRedirects(response_post, reverse('manage_evaluation', args=[self.evaluation.id]))
        
        self.assertTrue(Problem.objects.filter(title='Nova Questão de Código').exists())
        new_problem = Problem.objects.get(title='Nova Questão de Código')
        self.assertTrue(Solution.objects.filter(problem=new_problem, header='minha_funcao').exists())
        self.assertTrue(EvaluationProblem.objects.filter(problem=new_problem, evaluation=self.evaluation).exists())
        self.assertTrue(ProblemTestCase.objects.filter(problem=new_problem).exists())
        self.assertTrue(EvaluationProblemTestCase.objects.filter(evaluation_problem__problem=new_problem).exists())
    
    def test_create_evaluation_problem_post_text(self):
        url = reverse('create_evaluation_problem', args=[self.evaluation.id])
        form_data = {
            'title': 'Nova Questão de Texto',
            'content': 'Enunciado...',
            'question_type': 'T',
            'language': self.python_lang.id
        }
        self.professor_client.post(url, data=form_data)
        self.assertTrue(Problem.objects.filter(title='Nova Questão de Texto', question_type='T').exists())

    def test_create_evaluation_problem_invalid_form_data(self):
        url = reverse('create_evaluation_problem', args=[self.evaluation.id])
        form_data = {
            'title': 'Questão Inválida',
            'content': 'Enunciado...',
            'question_type': 'C',
            'language': self.python_lang.id
        }
        response = self.professor_client.post(url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Problem.objects.filter(title='Questão Inválida').exists())
        form_in_context = response.context['form']
        self.assertFalse(form_in_context.is_valid())
        self.assertIn('solution_header', form_in_context.errors)
        self.assertIn('Este campo é obrigatório para questões de código.', form_in_context.errors['solution_header'][0])

    def test_create_evaluation_problem_invalid_generator(self):
        url = reverse('create_evaluation_problem', args=[self.evaluation.id])
        form_data = {
            'title': 'Nova Questão de Código',
            'content': 'Enunciado...',
            'question_type': 'C',
            'solution_header': 'minha_funcao',
            'solution_content': 'def minha_funcao(a): return a',
            'language': self.python_lang.id,
            'test_case_generator': 'def generate(): return "isto-nao-e-uma-lista"'
        }
        response = self.professor_client.post(url, data=form_data)
        self.assertEqual(response.status_code, 302)

    def test_configure_testcases_post_only(self):
        url = reverse('configure_testcases', args=[self.eval_problem.id])
        
        post_data = {
            'selected_tc': [self.tc1.id, self.tc2.id],
            'hidden_tc': [self.tc2.id]
        }
        response_post = self.professor_client.post(url, data=post_data)
        self.assertRedirects(response_post, reverse('manage_evaluation', args=[self.evaluation.id]))

        self.assertTrue(EvaluationProblemTestCase.objects.filter(evaluation_problem=self.eval_problem, test_case=self.tc1, hidden=False).exists())
        self.assertTrue(EvaluationProblemTestCase.objects.filter(evaluation_problem=self.eval_problem, test_case=self.tc2, hidden=True).exists())

    def test_grade_by_question_views(self):
        ue = UserEvaluation.objects.create(user=self.student_user, evaluation=self.evaluation, submitted=True)
        UserEvaluationProblem.objects.create(user_evaluation=ue, evaluation_problem=self.eval_problem, grade=5.0, solution='code')

        url_list = reverse('grade_evaluation_question_list', args=[self.evaluation.id])
        response_list = self.professor_client.get(url_list)
        self.assertEqual(response_list.status_code, 200)

        url_q = reverse('grade_question_submission', args=[self.eval_problem.id])
        response_q = self.professor_client.get(url_q)
        self.assertEqual(response_q.status_code, 200)
        self.assertContains(response_q, '5')
    
    def test_take_exam_with_random_sort(self):
        self.evaluation.random_sort = True
        self.evaluation.save()

        ue = UserEvaluation.objects.create(user=self.student_user, evaluation=self.evaluation)
        uep = UserEvaluationProblem.objects.create(user_evaluation=ue, evaluation_problem=self.eval_problem)

        url_take_exam = reverse('take_exam', args=[ue.id])
        response_take = self.student_client.get(url_take_exam)
        self.assertEqual(response_take.status_code, 200)
        
        url_solve = reverse('solve_evaluation_problem', args=[uep.id])
        response_solve = self.student_client.get(url_solve)
        self.assertEqual(response_solve.status_code, 200)

    def test_submit_exam_happy_path(self):
        user_eval = UserEvaluation.objects.create(user=self.student_user, evaluation=self.evaluation)
        url = reverse('submit_exam', args=[user_eval.id])
        response = self.student_client.post(url)
        
        user_eval.refresh_from_db()
        self.assertTrue(user_eval.submitted)
        self.assertRedirects(response, reverse('submission_confirmation'))

    def test_submit_exam_already_submitted(self):
        user_eval = UserEvaluation.objects.create(user=self.student_user, evaluation=self.evaluation, submitted=True)
        url = reverse('submit_exam', args=[user_eval.id])
        response = self.student_client.post(url)
        
        self.assertRedirects(response, reverse('start'))

    def test_create_evaluation_problem_post_c_language(self):
        url = reverse('create_evaluation_problem', args=[self.evaluation.id])
        
        c_lang, _ = Language.objects.get_or_create(name='C')
        
        form_data = {
            'title': 'Nova Questão de C',
            'content': 'Enunciado...',
            'question_type': 'C',
            'solution_header': 'minhaFuncao',
            'solution_content': 'int minhaFuncao(int a) { return a; }',
            'language': c_lang.id,
        }
        response_post = self.professor_client.post(url, data=form_data)
        
        self.assertRedirects(response_post, reverse('manage_evaluation', args=[self.evaluation.id]))
        self.assertTrue(Problem.objects.filter(title='Nova Questão de C').exists())
        
        new_solution = Solution.objects.get(problem__title='Nova Questão de C')
        self.assertEqual(new_solution.return_type, 'int')

    def test_create_evaluation_problem_permission_denied(self):
        other_prof_user = User.objects.create_user(username='other_prof', password='123', is_staff=True)
        other_prof_client = Client()
        other_prof_client.force_login(other_prof_user)
        url = reverse('create_evaluation_problem', args=[self.evaluation.id])
        
        response_get = other_prof_client.get(url)
        self.assertEqual(response_get.status_code, 403)

        response_post = other_prof_client.post(url, data={})
        self.assertEqual(response_post.status_code, 403)

    def test_create_evaluation_problem_bad_c_header(self):
        url = reverse('create_evaluation_problem', args=[self.evaluation.id])
        c_lang, _ = Language.objects.get_or_create(name='C')
        form_data = {
            'title': 'Bad C Header',
            'content': '...',
            'question_type': 'C',
            'solution_header': 'non_existent_header',
            'solution_content': 'int main() { return 0; }',
            'language': c_lang.id,
        }
        self.professor_client.post(url, data=form_data)
        self.assertTrue(Problem.objects.filter(title='Bad C Header').exists())
        new_solution = Solution.objects.get(problem__title='Bad C Header')
        self.assertEqual(new_solution.return_type, 'int main() { return 0; }')
        
    def test_take_exam_permission_denied(self):
        ue = UserEvaluation.objects.create(user=self.student_user, evaluation=self.evaluation)
        other_student = User.objects.create_user(username='other_student', password='123')
        other_student_client = Client()
        other_student_client.force_login(other_student)

        url = reverse('take_exam', args=[ue.id])
        response = other_student_client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_take_exam_already_submitted(self):
        ue = UserEvaluation.objects.create(user=self.student_user, evaluation=self.evaluation, submitted=True)
        url = reverse('take_exam', args=[ue.id])
        response = self.student_client.get(url)
        self.assertRedirects(response, reverse('start'))