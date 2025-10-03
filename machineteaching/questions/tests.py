import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright
from django.conf import settings
from django.contrib.auth.models import User, Group
from .models import (Chapter, Problem, ExerciseSet, OnlineClass, UserLog,
                     #UserLogError, UserProfile, 
                     Professor, OnlineClass, Language, 
                     Evaluation, EvaluationProblem, UserEvaluation, UserEvaluationProblem)
from django.test.utils import override_settings
from django.test import TestCase#, TransactionTestCase
#from django.db import transaction
from datetime import datetime, timedelta
from django.utils import timezone

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
        page.click('button[type="submit"]:has-text("Create")')
        
        page.wait_for_selector(f'h3:has-text("{exam_title}")')
        self.assertEqual(exam_title, page.locator('h3').first.text_content())

    def professor_creates_question_in_exam(self, page):
        page.click('a#create_question')
        page.fill('input#id_title', 'Soma')
        page.fill('textarea#id_content', 'Escreva uma função que some dois números.')
        page.click('input#id_locked_problem')
        page.click('input#id_solution_header')
        page.fill('input#id_solution_header', 'soma')
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
        page.click('button:has-text("Search")')
        page.wait_for_selector(f'li:has-text("Exercicio_Teste")')
        page.click(f'li:has-text("Exercicio_Teste") button:has-text("Add")')

        page.wait_for_selector(f'.question-item h6:has-text("Exercicio_Teste")')
        self.assertEqual(2, page.locator('.question-item').count())
        page.click('button:has-text("Confirm")')
        self.assertEqual("Exams", page.locator('text=Exams').text_content())

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
        page.click('button:has-text("Save")')

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