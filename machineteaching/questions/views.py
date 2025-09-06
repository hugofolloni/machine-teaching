# from django.http import Http404, JsonResponse
import logging
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.messages import success, error
#from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models.functions import Lower
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
# import random
import json
import time
import random
import zipfile
from io import BytesIO
from datetime import datetime
from statistics import mean
from questions.models import (Problem, Solution, UserLog, UserProfile,
                              Professor, OnlineClass, UserLogView, Chapter,
                              Deadline, ExerciseSet, Recommendations, Comment, Language, TestCase, Evaluation, EvaluationProblem, UserEvaluation, EvaluationProblemTestCase, UserEvaluationProblem)
from questions.forms import (UserLogForm, SignUpForm, OutcomeForm, ChapterForm,
                             ProblemForm, SolutionForm, PageAccessForm, InteractiveForm,
                             EditProfileForm, NewClassForm, DeadlineForm, CommentForm, EvaluationForm, EvaluationProblemForm, GradeSubmissionForm)
from questions.serializers import RecommendationSerializer, ProblemSerializer
from questions.get_problem import get_problem
from questions.get_dashboards import student_dashboard, class_dashboard, manager_dashboard, predict_drop_out, time_to_finish_exercise, get_time_to_finish_chapter_in_days
from questions.get_dashboards import *
from questions.strategies import STRATEGIES_FUNC
from questions.get_dashboards1 import get_dashboards, get_class_dashboards
import csv
from django.conf import settings
from django.core.mail import send_mail
from functools import wraps
from .models import Collaborator, ChapterLink
from django.views.decorators.clickjacking import xframe_options_exempt
from .utils import supported_languages
import urllib
import requests
import google.auth.transport.requests
import google.oauth2.id_token
import os
from django.db import transaction
from django.views.decorators.http import require_POST
import json


LOGGER = logging.getLogger(__name__)


# Custom decorator, has to be in views.py file because it creates a circular import
def must_be_yours(model=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # user = request.user
            # print user.id
            pk = kwargs["id"]
            obj = model.objects.get(pk=pk)
            # Must be yours or from your student
            is_professor = Professor.objects.filter(user=request.user)
            LOGGER.info("Logged user is professor: %s" % bool(is_professor))
            # Test if user is professor and if student is in his/her class
            user_professor = is_professor and (obj.user.userprofile.user_class in is_professor[0].prof_class.all())
            LOGGER.info("Logged user is student professor: %s" % bool(user_professor))
            if not (obj.user == request.user) and not user_professor:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('start')
    return render(request, 'index.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('email').lower()
            user.save()
            user.refresh_from_db()  # load the instance created by the signal
            LOGGER.debug(form.cleaned_data.get('professor'))
            # Deprecated: student is now related to class, not to professor
            # Kept in model for backwards compatibility
            # professor = Professor.objects.get(pk=int(form.cleaned_data.get(
            #     'professor')))
            # user.userprofile.professor = professor
            user.userprofile.programming = form.cleaned_data.get('programming')
            user.userprofile.accepted = True
            user.userprofile.read = True
            user_class = OnlineClass.objects.get(
                class_code=form.cleaned_data.get('class_code'))
            user.userprofile.user_class = user_class
            user.userprofile.course = form.cleaned_data.get('course')
            user.userprofile.university = form.cleaned_data.get('university')
            user.userprofile.registration = form.cleaned_data.get('registration')
            user.userprofile.save()
            username = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('start')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'title':_('Create account'),'form': form})


# @permission_required('questions.can_add_problem', raise_exception=True)
@login_required
def show_problem(request, problem_id):
    #try:
    context = get_problem(problem_id)
    
    problem = problem_id
    exercise_sets = ExerciseSet.objects.filter(problem=problem)
    chapters = [es.chapter for es in exercise_sets]
    links = []
    for chapter in chapters:
        links.extend(chapter.link.all())

    context['links'] = links

    #except Problem.DoesNotExist:
        #raise Http404("Problem does not exist")
    return render(request, 'questions/show_problem.html', context)

#@login_required
#def get_start_problem(request):
    ## View to define starting problem. For the moment, let's always start with
    ## the same problem
    #try:
        #context = get_problem(679)
    #except Problem.DoesNotExist:
        #raise Http404("Problem does not exist")
    #return render(request, 'questions/show_problem.html', context)

@login_required
def get_random_problem(request):
    problem = Problem.objects.random()
    solution = Solution.objects.filter(problem=problem, language=Language.objects.get(name='Python'))[0]
    return render(request, 'questions/show_problem.html', {'problem': problem,
                                                           'solution': solution})

@login_required
def get_next_problem(request):
    if request.user.userprofile.sequential:
        strategy = 'sequential'
    else:
        strategy = 'random'
        # TODO: Temp hack while EER strategy is not updated with new clusters and problems
        ## strategy = request.user.userprofile.strategy
    problem_id = STRATEGIES_FUNC[strategy](request.user)
    LOGGER.debug("Got problem %s", problem_id)
    if not problem_id:
        return render(request, 'questions/finished.html', {'title': _('Finished')})
    context = get_problem(problem_id)
    return render(request, 'questions/show_problem.html', context)

@login_required
def save_user_log(request):
    if request.POST['language'] not in supported_languages:
        return JsonResponse({'status': 'failed', 'message': 'Language not supported'})
    request.POST = request.POST.copy()  #Criando uma cópia de request.POST, pois ele é imutável
    lang_id = Language.objects.get(name=request.POST['language']).id
    request.POST['language'] = str(lang_id)
    form = UserLogForm(request.POST)
    LOGGER.debug("Log received for user %s with outcome %s: %s",
                 request.user,
                 request.POST['outcome'],
                 request.POST['solution'])
    if form.is_valid():
        log = form.save(commit=False)
        log.user = request.user
        log.user_class = request.user.userprofile.user_class
        log.save()
        return JsonResponse({'status': 'success'})
    # LOGGER.debug("Log failed: %s", form.errors)
    LOGGER.debug("Log failed")
    return JsonResponse({'status': 'failed'})

#Método para enviar o código submetido para o worker-node
@login_required
def submit_code(request):
    if request.method == "POST":
        form_data = request.POST.dict()
        files = request.FILES
        
        audience = settings.WORKER_NODE_HOST + settings.WORKER_NODE_PORT
        endpoint = audience + "/multi_process"
        worker_node_url = settings.WORKER_NODE_HOST + settings.WORKER_NODE_PORT + "/multi_process"
        #logging.info(f"audience: {audience}\nendpoint: {endpoint}")
        try:
            lang = form_data['prog_lang']
            test_cases_to_run = []

            if 'evaluation_problem_id' in form_data:
                eval_problem = get_object_or_404(EvaluationProblem, id=form_data['evaluation_problem_id'])
                problem = eval_problem.problem
                public_test_cases = eval_problem.evaluationproblemtestcase_set.filter(hidden=False)
                test_cases_to_run = [json.loads(ptc.test_case.content) for ptc in public_test_cases]

            else: 
                problem_id = form_data['problem_id']
                problem = Problem.objects.get(pk=problem_id)
                all_test_cases = TestCase.objects.filter(problem=problem)
                try:
                    test_cases_to_run = [json.loads(tc.content) for tc in all_test_cases]
                except json.decoder.JSONDecodeError:
                    test_cases_to_run = [tc.content for tc in all_test_cases]
                    form_data['custom_test_cases'] = True

            form_data['test_cases'] = json.dumps(test_cases_to_run)
            form_data['problem_id'] = problem.id 

            solution = Solution.objects.filter(problem=problem, language__name=lang, ignore=False).first()
            if not solution:
                return JsonResponse({"error": "No valid solution found for this problem/language."}, status=400)

            form_data['professor_code'] = solution.content
            form_data['func'] = solution.header
            form_data['return_type'] = solution.return_type

            if os.getenv('ENVIRONMENT') == 'prod':
                auth_req = google.auth.transport.requests.Request()
                id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
                headers = { 'Authorization': f'Bearer {id_token}' }
                response = requests.post(endpoint, data=form_data, files=files, headers=headers)
            else:
                response = requests.post(endpoint, data=form_data, files=files)
                
            response.raise_for_status()
            return JsonResponse(response.json(), safe=False)

        except Exception as e:
            LOGGER.error(f"Unexpected exception in submit_code: {e}")
            return JsonResponse({"error": "An unexpected server error occurred.", "details": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

@login_required
def get_past_problems(request):
    logs = UserLog.objects.filter(user=request.user, 
    user_class=request.user.userprofile.user_class).order_by('-timestamp')
    passed = logs.filter(outcome='P').values_list('problem_id', flat=True
                                                  ).distinct()
    skipped = logs.filter(outcome='S').values_list('problem_id', flat=True
                                                  ).distinct()
    failed = logs.filter(outcome='F').values_list('problem_id', flat=True
                                                  ).distinct()

    log_problems = logs.values_list('problem', flat=True)
    problems = []
    for pk in log_problems:
        if pk not in problems:
            problems.append(pk)

    past_problems = []
    if len(problems):
        for problem_id in problems:
            if problem_id in passed:
                outcome = 'P'
            elif problem_id in failed:
                outcome = 'F'
            else:
                outcome = 'S'
            problem = Problem.objects.get(id=problem_id)
            exerciseset = ExerciseSet.objects.filter(problem=problem).values_list('chapter', flat=True)
            onlineclass = request.user.userprofile.user_class
            available_chapters = Deadline.objects.filter(onlineclass=onlineclass
                                                ).values_list('chapter', flat=True)
            problem_chapter = ''
            for chapter in exerciseset:
                if chapter in available_chapters:
                    problem_chapter = Chapter.objects.get(id=chapter)
                else:
                    problem_chapter = ''
            problem_logs = logs.filter(problem=problem)
            comments = Comment.objects.filter(userlog__in=problem_logs).count()
            last = problem_logs.values_list('timestamp', flat=True)[0]
            last = timezone.localtime(last)
            past_problems.append({'problem': problem,
                                  'chapter': problem_chapter,
                                  'comments': comments, 
                                  'last_submission': last, 
                                  'outcome': outcome, 
                                  'attempts': len(problem_logs)})
    return render(request, 'questions/past_problems.html', {
        'title': _('Past problems'), 'problems': past_problems, 'user': request.user})

@permission_required('questions.view_userlogview', raise_exception=True)
@login_required
def get_student_logs(request, id, chapter=None, problem=None):
    user = User.objects.get(pk=id)
    LOGGER.debug("Getting logs for user %s", user)
    logs = UserLog.objects.filter(
        user_id=id, user_class=user.userprofile.user_class).order_by('-timestamp')
    if chapter:
        logs = logs.filter(problem__chapter=chapter)
    if problem:
        logs = logs.filter(problem=problem)
    return render(request, 'questions/student_logs.html', {
        'title': user.first_name+' '+user.last_name, 'past_problems': logs, 'student': user})

@login_required
def get_chapter_problems(request):
    onlineclass = request.user.userprofile.user_class
    LOGGER.debug("Online class: %s" % onlineclass)
    available_chapters = Deadline.objects.filter(onlineclass=onlineclass
                                                ).values_list('chapter',
                                                              flat=True).order_by('-deadline')
    LOGGER.debug("Available chapters: %s" % available_chapters)
    chapters = []
    problems = []
    for i in range(0,len(available_chapters),3):
        chapter = Chapter.objects.get(pk=available_chapters[i])
        chapters.append(chapter)
        problems.append(ExerciseSet.objects.filter(chapter=chapter).order_by('order','-id'))
    col_1 = list(zip(chapters,problems))
    chapters = []
    problems = []
    for i in range(1,len(available_chapters),3):
        chapter = Chapter.objects.get(pk=available_chapters[i])
        chapters.append(chapter)
        problems.append(ExerciseSet.objects.filter(chapter=chapter).order_by('order','-id'))
    col_2 = list(zip(chapters,problems))
    chapters = []
    problems = []
    for i in range(2,len(available_chapters),3):
        chapter = Chapter.objects.get(pk=available_chapters[i])
        chapters.append(chapter)
        problems.append(ExerciseSet.objects.filter(chapter=chapter).order_by('order','-id'))
    col_3 = list(zip(chapters,problems))
    # Get exercise where student passed
    userlog = UserLog.objects.filter(
        user=request.user,
        timestamp__gte=request.user.userprofile.user_class.start_date)
    passed = userlog.filter(outcome='P').values_list('problem_id', flat=True
                                              ).distinct()
    skipped = userlog.filter(outcome='S').values_list('problem_id', flat=True
                                              ).distinct()
    failed = userlog.filter(outcome='F').values_list('problem_id', flat=True
                                              ).distinct()
    return render(request, 'questions/chapters.html', {
        'title': _('Chapters'),
        'chapters': [col_1,col_2,col_3],
        'passed': passed,
        'skipped': skipped,
        'failed': failed,
        # 'available_chapters': available_chapters
        })

def get_past_solutions(request, problem_id):
    LOGGER.debug("Getting solutions for problem %s", problem_id)
    problem = Problem.objects.get(id=problem_id)
    logs = UserLog.objects.filter(user=request.user,
                                  problem=problem,
                                  user_class=request.user.userprofile.user_class).order_by('-timestamp')
    solutions = []
    for log in logs:
        comments = Comment.objects.filter(userlog=log)
        solutions.append({'log':log,'comments':comments})
    return render(request, 'questions/problem_solutions.html', {'problem': problem, 'solutions': solutions})


@login_required
def show_chapter(request, chapter):
    chapter = Chapter.objects.get(pk=chapter)
    LOGGER.debug("Chapter: %s" % chapter)
    problems = ExerciseSet.objects.filter(chapter=chapter).order_by('order', '-id')
    LOGGER.debug("Chapter problems: %s" % problems)
    onlineclass = request.user.userprofile.user_class
    LOGGER.debug("Online class: %s" % onlineclass)
    # Get farthest deadline
    deadline = Deadline.objects.filter(onlineclass=onlineclass,
                                       chapter=chapter).order_by('-deadline')
    if deadline:
        deadline = deadline[0].deadline
    else:
        deadline = 0
    LOGGER.debug("Deadline: %s" % deadline)

    errors = get_error_type_per_chapter(User.objects.filter(userprofile__user_class=onlineclass),
                                                            [chapter],onlineclass)
    main_errors = errors

    # Get exercise where student passed
    userlog = UserLog.objects.filter(
        user=request.user,
        timestamp__gte=request.user.userprofile.user_class.start_date)
    passed = userlog.filter(outcome='P').values_list('problem_id', flat=True
                                              ).distinct()
    skipped = userlog.filter(outcome='S').values_list('problem_id', flat=True
                                              ).distinct()
    failed = userlog.filter(outcome='F').values_list('problem_id', flat=True
                                              ).distinct()
    if request.method == 'POST':
        problem_ids = str(list(request.POST['ids'])[0])
        for index, pk in enumerate(problem_ids.split(','), start=1):
            exerciseset = ExerciseSet.objects.get(chapter=chapter, problem=int(pk))
            exerciseset.order = index
            exerciseset.save()
        return HttpResponse('')
    return render(request, 'questions/show_chapter.html', {
        'title': chapter,
        'chapter': chapter,
        'deadline': deadline,
        'problems': problems,
        'errors': main_errors,
        'passed': passed,
        'skipped': skipped,
        'failed': failed
        })

@permission_required('questions.view_userlogview', raise_exception=True)
@login_required
def new_chapter(request):
    chapter = None
    if request.method == "POST":
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.save()
            date = form.cleaned_data['deadline'].strftime('%Y-%m-%d 23:59:59')
            deadline = Deadline(chapter=chapter, deadline=date)
            deadline.save()
            classes = OnlineClass.objects.filter(professor__user=request.user)
            for item in classes:
                deadline.onlineclass.add(item)
            deadline.save()
            return redirect('show_chapter', chapter=chapter.id)
    else:
        form = ChapterForm()
    return redirect('chapters')

@login_required
def show_outcome(request):
    outcomes = []
    onlineclass = None
    if request.method == 'POST':
        form = OutcomeForm(request.POST, user=request.user)
        if form.is_valid():
            onlineclass = form.cleaned_data['onlineclass']
            chapter = form.cleaned_data['chapter']
            # Get class problems
            problems_all = Problem.objects.filter(chapter=chapter).order_by(
                    'title', 'id')
            problems = list(problems_all.values_list('id', flat=True))
            # Get latest student outcome for every student in class
            students = UserLogView.objects.filter(
                user_class_id=onlineclass,
                problem_id__in=problems
            ).order_by(Lower('user__first_name').asc(),
                       Lower('user__last_name').asc(),
                       'user_id',
                       'problem__title',
                       'problem_id').values('user_id',
                                            'user__first_name',
                                            'user__last_name',
                                            'problem_id',
                                            'final_outcome',
                                            'timestamp')
            # For each student in class, let's organize it in a table
            start = time.time()
            if students.count():
                current_student = students[0]["user_id"]
                student_name = "%s %s" % (students[0]["user__first_name"],
                                          students[0]["user__last_name"])
                outcome_student = [(None, None)]*len(problems)
                for student in students:
                    if current_student == student["user_id"]:
                        outcome_student[
                            problems.index(student["problem_id"])
                        ] = (student["final_outcome"],
                             timezone.localtime(student[
                                 "timestamp"]).strftime("%Y-%m-%d %H:%M:%S"))
                    # Previous student is finished, lets start a new one
                    else:
                        only_outcomes = list(zip(*outcome_student))[0]
                        student_row = {
                            "name": (student_name, current_student),
                            "outcomes": outcome_student,
                            "total": {
                                "P": only_outcomes.count("P"),
                                "F": only_outcomes.count("F"),
                                "S": only_outcomes.count("S")
                            }
                        }
                        outcomes.append(student_row)
                        # Get new student
                        outcome_student = [(None,None)]*len(problems)
                        current_student = student["user_id"]
                        student_name = "%s %s" % (student["user__first_name"],
                                                  student["user__last_name"])
                        outcome_student[
                            problems.index(student["problem_id"])
                        ] = (student["final_outcome"],
                             timezone.localtime(student[
                                 "timestamp"]).strftime("%Y-%m-%d %H:%M:%S"))
                # Add last student
                outcome_student[
                    problems.index(student["problem_id"])
                ] = (student["final_outcome"],
                     timezone.localtime(student[
                         "timestamp"]).strftime("%Y-%m-%d %H:%M:%S"))
                only_outcomes = list(zip(*outcome_student))[0]
                student_row = {"name": (student_name, current_student),
                                "outcomes": outcome_student,
                                "total": {"P": only_outcomes.count("P"),
                                            "F": only_outcomes.count("F"),
                                            "S": only_outcomes.count("S")}}
                outcomes.append(student_row)
            end = time.time()
            LOGGER.info("Elapsed time: %d" % (end-start))
    else:
        form = OutcomeForm()
        problems_all = []
    form.fields['onlineclass'].queryset = OnlineClass.objects.filter(
        professor__user=request.user).order_by('name')
    LOGGER.info("Available classes: %s" % form.fields['onlineclass'].queryset)
    LOGGER.info("Showing students and outcomes: %s" % json.dumps(outcomes))
    return render(request, 'questions/outcomes.html',
                  {'title': _('Outcomes'),'form': form, 'problems': problems_all, 'outcomes':outcomes, 'class':onlineclass})

@login_required
@must_be_yours(model=UserLog)
def get_user_solution(request, id):
    userlog = UserLog.objects.get(pk=id)
    context = get_problem(userlog.problem_id)
    comments = Comment.objects.filter(userlog=userlog)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.userlog = userlog 
            student = User.objects.get(pk=userlog.user_id)
            send_comment_email(student, comment, request.path)
            comment.save()
            return redirect('past_solutions', id=userlog.id)
    else:
        form = CommentForm()
    context.update({'log': userlog, 'title': _('Solution'), 'comments': comments, 'form':form})
    return render(request, 'questions/past_solutions.html', context)

@permission_required('questions.view_userlogview', raise_exception=True)
def get_problem_solutions(request, problem_id, class_id):
    logs = UserLog.objects.filter(user_class=class_id,
                problem_id=problem_id).order_by('user__first_name',
                                                'user__last_name',
                                                'user_id',
                                                '-timestamp').values('user_id',
                                                                     'user__first_name',
                                                                     'user__last_name',
                                                                     'solution',
                                                                     'outcome',
                                                                     'timestamp',
                                                                     'test_case_hits',
                                                                     'language',
                                                                     'id')
    students = []
    if logs.count():
        current_student = logs[0]["user_id"]
        student_name = "%s %s" % (logs[0]["user__first_name"],
                                  logs[0]["user__last_name"])
        student = {'name':student_name,'logs':[]}
        for log in logs:
            log["language"] = Language.objects.get(id=log["language"]).name
            if log["user_id"] != current_student:
                students.append(student)
                current_student = log["user_id"]
                student_name = "%s %s" % (log["user__first_name"],
                                          log["user__last_name"])
                student = {'name':student_name,'logs':[]}
            student['logs'].append(log)
        students.append(student)
    problem = Problem.objects.get(id=problem_id)
    onlineclass = OnlineClass.objects.get(id=class_id)
    return render(request, 'questions/solutions.html', {'title': _('Problem solutions'),
                                                        'problem': problem,
                                                        'onlineclass': onlineclass,
                                                        'students': students})

@permission_required('questions.view_userlogview', raise_exception=True)
def get_student_solutions(request, id, chapter):
    student = User.objects.get(id=id)
    LOGGER.debug("Getting logs for student %s", student)
    chapter = Chapter.objects.get(id=chapter)
    logs = UserLog.objects.filter(user=student,
                                  problem__chapter=chapter, 
                                  user_class=student.userprofile.user_class).order_by(
                                                'problem__id',
                                                '-timestamp').values('problem',
                                                                     'solution',
                                                                     'outcome',
                                                                     'timestamp',
                                                                     'test_case_hits',
                                                                     'id',
                                                                     'language')
    problems = []
    if logs.count():
        current_problem = logs[0]["problem"]
        problem = {'problem':Problem.objects.get(id=current_problem),'logs':[]}
        for log in logs:
            log["language"] = Language.objects.get(id=log["language"]).name
            if log["problem"] != current_problem:
                problems.append(problem)
                current_problem = log["problem"]
                problem = {'problem':Problem.objects.get(id=current_problem),'logs':[]}
            problem['logs'].append(log)
        problems.append(problem)
    return render(request, 'questions/student_solutions.html', {'title':_('Student solutions'),
                                                        'problems': problems,
                                                        'student': student,
                                                        'chapter': chapter})

@login_required
def update_strategy(request):
    try:
        sequential = request.GET['sequential']
        user = UserProfile.objects.get(user=request.user)
        user.sequential = bool(int(sequential))
        user.save()
        return JsonResponse({'status': 'success'})
    except Exception:
        return JsonResponse({'status': 'failed'})

@permission_required('questions.view_userlogview', raise_exception=True)
def export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Student', 'Problem', 'Outcome', 'Timestamp'])
    outcomes = []
    if request.method == 'POST':
        form = OutcomeForm(request.POST, user=request.user)
        if form.is_valid():
            onlineclass = form.cleaned_data['onlineclass']
            chapter = form.cleaned_data['chapter']
            # Get class problems
            problems = list(Problem.objects.filter(chapter=chapter).order_by(
                    'id').values_list('id', flat=True))
            # Get latest student outcome for every student in class
            students = UserLogView.objects.filter(
                user__userprofile__user_class=onlineclass,
                problem_id__in=problems, timestamp__gte=onlineclass.start_date
            ).order_by(Lower('user__first_name').asc(),
                       Lower('user__last_name').asc(),
                       'problem_id').values('user__first_name',
                                            'user__last_name',
                                            'problem_id',
                                            'problem__title',
                                            'final_outcome',
                                            'timestamp')
            for student in students:
                outcomes = {'P':'Passed','F':'Failed','S':'Skipped'}
                userlog = [str(student['user__first_name'])+' '+student['user__last_name'],
                    str(student['problem_id'])+' - '+student['problem__title'],
                    outcomes[student['final_outcome']],
                    timezone.localtime(student['timestamp']).strftime("%Y-%m-%d %H:%M:%S")]
                writer.writerow(userlog)
    else:
        form = OutcomeForm()
        problems = []
    form.fields['onlineclass'].queryset = OnlineClass.objects.filter(
        professor__user=request.user).order_by('name')
    LOGGER.info("Available classes: %s" % form.fields['onlineclass'].queryset)
    LOGGER.info("Showing students and outcomes: %s" % json.dumps(outcomes))
    response['Content-Disposition'] = 'attachment; filename="userlog.csv"'
    return response

@permission_required('questions.view_userlogview', raise_exception=True)
def new_problem(request, chapter=None):
    if request.method == 'POST':
        problem_form = ProblemForm(request.POST)
        solution_form = SolutionForm(request.POST)
        if problem_form.is_valid() and solution_form.is_valid():
            problem = problem_form.save(commit=False)
            problem.question_type = solution_form.cleaned_data.get('question_type')
            problem.save()
            solution = solution_form.save(commit=False)
            solution.content = solution_form.cleaned_data.get('solution')
            solution.problem_id = problem.id
            solution.save()
            chapter = list(problem_form.cleaned_data.get('chapter'))[0]
            order = problem_form.cleaned_data.get('order')
            if not order:
                problems = ExerciseSet.objects.filter(chapter=chapter).values_list('order')
                order = len(list(problems))+1
            exerciseset = ExerciseSet(chapter=chapter, problem=problem, order=order)
            exerciseset.save()
            success(request, 'The problem was added')
            return redirect('show_chapter', chapter=chapter.id)
        else:
            error(request, 'The problem was not added')
    else:
        problem_form = ProblemForm()
        solution_form = SolutionForm()
    return render(request, 'questions/new_problem.html',{
        'title': _('New problem'),
        'chapter': chapter,
        'problem_form': problem_form,
        'solution_form': solution_form
        })

@login_required
def save_access(request):
    form = PageAccessForm(request.POST)
    if form.is_valid():
        access = form.save(commit=False)
        access.user = request.user
        access.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})

@login_required
def save_university(request):
    university = request.GET['university']
    registration = request.GET['registration']
    user = UserProfile.objects.get(user=request.user)
    user.university = university
    user.registration = registration
    user.save()
    return JsonResponse({'status': 'success'})


@login_required
def save_interactive(request):
    form = InteractiveForm(request.POST)
    if form.is_valid():
        interactive = form.save(commit=False)
        interactive.user = request.user
        interactive.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST)
        if form.is_valid():
            userprofile = request.user.userprofile
            user_class = OnlineClass.objects.get(
                class_code=form.cleaned_data.get('class_code'))
            userprofile.user_class = user_class
            userprofile.save()
            return redirect('start')
    else:
        form = EditProfileForm()
    return render(request, 'questions/edit_profile.html', {'title':_('Edit profile'),'form':form})

@permission_required('questions.view_userlogview', raise_exception=True)
def classes(request):
    if request.method == 'POST':
        form = NewClassForm(request.POST)
        if form.is_valid():
            onlineclass = form.save(commit=False)
            onlineclass.start_date = datetime.now()
            onlineclass.save()
            onlineclass.professor.set([Professor.objects.get(user=request.user)])
            return redirect('classes')
    else:
        form = NewClassForm()
    onlineclasses = OnlineClass.objects.filter(professor__user=request.user)
    professors = Professor.objects.all().values_list('user')
    classes = []
    for onlineclass in onlineclasses:
        students = User.objects.filter(userprofile__user_class=onlineclass).exclude(pk__in=professors)
        chapters = Deadline.objects.filter(onlineclass=onlineclass)
        classes.append({'id': onlineclass.id,
                        'name': onlineclass.name,
                        'active': onlineclass.active,
                        'class_code': onlineclass.class_code,
                        'start_date': onlineclass.start_date,
                        'students': students.count(),
                        'chapters': chapters.count()})
    return render(request, 'questions/classes.html', {'title': _('Classes'),
                                                      'form': form,
                                                      'classes': classes})

@permission_required('questions.view_userlogview', raise_exception=True)
def manage_class(request, onlineclass):
    if request.method == "POST":
        pass 
    else:
        form = DeadlineForm()
    
    onlineclass = OnlineClass.objects.get(id=onlineclass)
    if onlineclass in Professor.objects.get(user=request.user).prof_class.all():
        professors = Professor.objects.all().values_list('user')
        students = User.objects.filter(userprofile__user_class=onlineclass).exclude(
            pk__in=professors).order_by(Lower('first_name').asc(), Lower('last_name').asc())
        students_list = []
        for student in students:
            try:
                dropout = predict_drop_out(student.id, onlineclass, datetime.now())
                students_list.append({'student':student, 'predict': dropout})
            except AttributeError:
                students_list.append({'student':student})

        deadlines = Deadline.objects.filter(onlineclass=onlineclass)
        chapters = []
        for deadline in deadlines:
            chapter = Chapter.objects.get(deadline=deadline)
            chapters.append({'chapter':chapter, 'deadline':deadline})

        evaluations_list = []
        now = timezone.now()
        all_evaluations = Evaluation.objects.filter(online_class=onlineclass, cancelled=False).order_by('-start_date')

        for evaluation in all_evaluations:
            status_text = ''
            status_color = '' 

            if now > evaluation.end_date:
                status_text = 'Finalizada'
                status_color = 'secondary'
            elif evaluation.start_date <= now <= evaluation.end_date:
                status_text = 'Em andamento'
                status_color = 'success'
            else:
                status_text = 'Agendada'
                status_color = 'primary'
            
            evaluations_list.append({
                'id': evaluation.id,
                'title': evaluation.title,
                'status': status_text,
                'status_color': status_color,
            })

        return render(request, 'questions/show_class.html', {'title': onlineclass.name,
                                                            'students_list': students_list,
                                                            'chapters': chapters,
                                                            'onlineclass': onlineclass,
                                                            'form': form,
                                                            'evaluations': evaluations_list}) 
    else:
        raise PermissionDenied()

@login_required
@permission_required('questions.view_userlogview', raise_exception=True)
def get_class_dashboard(request, onlineclass):
    onlineclass = OnlineClass.objects.get(id=onlineclass)
    if onlineclass in Professor.objects.get(user=request.user).prof_class.all():
        return render(request, 'questions/class_dashboard.html', class_dashboard(onlineclass))
    else:
        raise PermissionDenied()
    
@login_required
@permission_required('questions.view_userlogview', raise_exception=True)
def get_class_dashboard1(request, onlineclass):
    onlineclass = OnlineClass.objects.get(id=onlineclass)
    if onlineclass in Professor.objects.get(user=request.user).prof_class.all():
        return render(request, 'questions/class_dashboard1.html', get_class_dashboards(onlineclass))
    else:
        raise PermissionDenied()

def get_manager_dashboard(request):
    return render(request, 'questions/manager_dashboard.html', manager_dashboard())


@login_required
def delete_deadline(request, onlineclass, deadline):
    Deadline.objects.filter(id=deadline).delete()
    return redirect('manage_class', onlineclass=onlineclass)

def class_active(request):
    if request.method == 'POST':
        onlineclass = OnlineClass.objects.get(id=int(request.POST['class_id']))
        if onlineclass.active:
            onlineclass.active = False
        else:
            onlineclass.active = True
        onlineclass.save()
        return HttpResponse('')

@login_required
def get_dashboard(request):
    context = student_dashboard(request.user)
    return render(request, 'questions/student_dashboard.html', context)

@login_required
def get_dashboard1(request):
    context = get_dashboards(request.user.id)
    return render(request, 'questions/student_dashboard1.html', context)

@permission_required('questions.view_userlogview', raise_exception=True)
def get_student_dashboard1(request, id):
    context = get_dashboards(id, professor=True)
    return render(request, 'questions/student_dashboard1.html', context)

@permission_required('questions.view_userlogview', raise_exception=True)
def get_student_dashboard(request, id):
    student = User.objects.get(id=id)
    context = student_dashboard(student, professor=True)
    context.update({'student': student})
    return render(request, 'questions/student_dashboard.html', context)

@login_required
def start(request):
    onlineclass = request.user.userprofile.user_class
    chapters = Deadline.objects.filter(onlineclass=onlineclass).values_list('chapter', flat=True)
    problems = Problem.objects.filter(chapter__in=chapters)
    passed = UserLogView.objects.filter(user=request.user,
                                        problem__in=problems,
                                        final_outcome='P').count()
    failed = UserLogView.objects.filter(user=request.user,
                                        problem__in=problems,
                                        final_outcome='F').count()
    skipped = UserLogView.objects.filter(user=request.user,
                                        problem__in=problems,
                                        final_outcome='S').count()
    progress = get_progress_per_problem([request.user], problems, onlineclass)
    # Last item is progress sum
    progress[3] = sum(progress[:3])
    # Round values
    progress = list(map(round, progress))

    if request.user.userprofile.sequential:
        strategy = 'sequential'
    else:
        strategy = 'random'
    problem_id = STRATEGIES_FUNC[strategy](request.user)
    next_problem = None
    if problem_id:
        next_problem = Problem.objects.get(id=problem_id)

    times = time_to_finish_exercise(request.user, problems, onlineclass)
    time = None
    if len(times):
        time = round(mean(times)/60)

    chapter_times = []
    for chapter in chapters:
        chapter_problems = problems.filter(chapter=chapter)
        solved_problems = UserLogView.objects.filter(user=request.user, 
                                                        problem__in=chapter_problems,
                                                        final_outcome='P').count()
        if chapter_problems.count() > 0 and solved_problems == chapter_problems.count():      
            time_to_finish_single_chapter = get_time_to_finish_chapter_in_days(request.user, chapter_problems, onlineclass)
            if time_to_finish_single_chapter is not None:           
                chapter_times.append(time_to_finish_single_chapter)
        
    time_to_finish_chapter = None
    if len(chapter_times):
        time_to_finish_chapter = round(mean(chapter_times))

    u_errors = []
    for problem in problems:
        passed = UserLog.objects.filter(user=request.user,
                                            problem=problem,
                                            outcome='P',
                                            timestamp__gte=onlineclass.start_date)
        if passed.count():
            timestamp = passed.first().timestamp

            errors = UserLog.objects.filter(user=request.user,
                                            problem=problem,
                                            outcome='F',
                                            timestamp__gte=onlineclass.start_date,
                                            timestamp__lte=timestamp).count()
            u_errors.append(errors)

    errors = None
    if len(u_errors):
        errors = round(mean(u_errors))

    main_errors = get_error_type_per_chapter([request.user],chapters,onlineclass)

    current_chapter = Deadline.objects.filter(deadline__gte=datetime.now(),
                                              onlineclass=onlineclass).order_by('deadline'
                                              ).first()
    problems = None
    chapter_time = None
    if current_chapter:
        problems = ExerciseSet.objects.filter(chapter=current_chapter.chapter.id).order_by('order')
        chapter_time = get_time_to_finish_chapter(request.user, current_chapter.chapter, onlineclass)

    userlog = UserLog.objects.filter(
        user=request.user,
        timestamp__gte=onlineclass.start_date)
    passed = userlog.filter(outcome='P').values_list('problem_id', flat=True
                                              ).distinct()
    skipped = userlog.filter(outcome='S').values_list('problem_id', flat=True
                                              ).distinct()
    failed = userlog.filter(outcome='F').values_list('problem_id', flat=True
                                              ).distinct()
    
    now = timezone.now()

    current_evaluations = Evaluation.objects.filter(
        online_class=onlineclass,
        cancelled=False,
        start_date__lte=now,
        end_date__gte=now,
        ).order_by('end_date')

    active_evaluations_id = []

    for ev in current_evaluations:
        ue = UserEvaluation.objects.filter(user=request.user,evaluation=ev).first()
        if not ue or not ue.submitted:
            active_evaluations_id.append(ev.id)

    active_evaluations = current_evaluations.filter(id__in=active_evaluations_id)

    return render(request, 'questions/home.html', {'title': _('home'),
                                                   'progress': progress,
                                                   'next_problem': next_problem,
                                                   'time': time,
                                                   'time_to_finish_chapter': time_to_finish_chapter,
                                                   'errors': errors,
                                                   'main_errors': main_errors,
                                                   'current_chapter': current_chapter,
                                                   'chapter_time': chapter_time,
                                                   'problems': problems,
                                                   'passed': passed,
                                                   'failed': failed,
                                                   'skipped': skipped,
                                                   'active_evaluations': active_evaluations  
                                                })

# View to redirect to the satisfation form
def satisfaction_form(request):
    return render(request, 'questions/satisfaction_form.html')

class AttemptsList(APIView):
    def get(self, request, format=None):
        date = request.query_params.get('date')
        logs = UserLog.objects.all()
        if date:
            date = timezone.make_aware(datetime.strptime(date,'%m-%d-%Y'))
            logs = UserLog.objects.filter(timestamp__gte=date)
        problems = Problem.objects.all().values_list('id')
        users = User.objects.all().values_list('id')
        content = []
        for problem in problems:
            problem = problem[0]
            for user in users:
                user = user[0]
                attempts = logs.filter(user_id=user, problem_id=problem).count()
                content.append({'problem_id':problem, 'user_id':user, 'attempts':attempts})
        return Response(content)

class Recommendations(APIView):
    def get(self, request, format=None):
        recommendations = Recommendations.objects.all()
        serializer = RecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)
    def post(self, request, format=None):
        serializer = RecommendationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#worker-node
class ProblemDetailView(APIView):    #Endpoint para recuperar detalhes de um problema específico pelo id
    def get(self, request, problem_id):
        try:
            problem = Problem.objects.get(pk=problem_id)
            serializer = ProblemSerializer(problem)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Problem.DoesNotExist:
            return Response({'error': 'Problem not found'}, status=status.HTTP_404_NOT_FOUND)


def send_comment_email(student, comment, link):
    solution_link = 'http://machineteaching.tech{}'.format(link)
    student_email = student.email
    message_subject = 'Comentário adicionado ao exercício "{}"'.format(comment.userlog.problem.title)
    message_content = '{} {}, foi adicionado um comentário no seu exercício "{}". \n\n Professor: {} \n Comentário: {} \n\n Veja aqui: {}'.format(student.first_name, student.last_name, comment.userlog.problem.title, comment.user, comment.content, solution_link)
    message_html = """
        <div style='display: grid; grid-auto-flow: row; padding: 20px; width: 400px; height: 300px; background-color: #ffffff; border-radius: 10px;'>
            <h4 style='color: #292929; grid-column: 1;'> {} {}, foi adicionado um comentário no seu exercício "{}".</h4> 
            <p style='color: #292929; margin-left: 20px; font-weight: 300; grid-column: 2;'> <strong>Professor:</strong> {} </p> 
            <p style='color: #292929; margin-left: 20px; font-weight: 300; grid-column: 3;'> <strong>Comentário:</strong> {}</p>
            <div style="grid-column: 4; width: 100%; height: 100%;">
                <a href='{}' style='font-weight: 300; margin-left: 40%; width: 20%; height: 50%; padding: 0.5rem 1rem; justify-content: center; align-items: center; border-radius: 4px; text-decoration: none; color: white; background-color: #2196F3'>Veja aqui</a>            
            </div>
        </div>""".format(student.first_name, student.last_name, comment.userlog.problem.title, comment.user, comment.content, solution_link)
    send_mail(message_subject, message_content, None, [student_email], fail_silently=False, html_message=message_html)

@xframe_options_exempt
def about(request):
    Team = Collaborator.objects.all().order_by('name')
    inactiveCount = Team.filter(active = False).count()
    context = {
        'Team': Team,
        'inactiveCount' : inactiveCount,
    }
    return render(request, 'questions/about.html', context)  

@login_required   
def python_tutor(request):
    link_fixo = "https://pythontutor.com/render.html#code="
    codigo_aluno = "none"

    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        linguagem = request.POST.get('linguagem')
        codigo_aluno = urllib.parse.quote_plus(str(codigo))

    if linguagem == "C":
        nome_funcao = request.POST.get('nome_funcao')
        link_fixo = "https://pythontutor.com/c.html#mode=edit&code="
        codigo_aluno = codigo_aluno + f"""%0A%0Aint main(){{%0A++//Descomente a função abaixo e alterne seus parâmetros para testá-la%0A++//{nome_funcao}();%0A++return 0;%0A}}"""
        
    context = {'link_fixo': link_fixo, 'codigo_aluno': codigo_aluno}
    return JsonResponse(context)

@login_required
def profile(request):
    return render(request, 'questions/profile.html')

@login_required
@permission_required('questions.add_evaluation', raise_exception=True)
def create_evaluation(request, onlineclass_id):
    online_class = get_object_or_404(OnlineClass, id=onlineclass_id)

    if not Professor.objects.filter(user=request.user, prof_class=online_class).exists():
        raise PermissionDenied("Você não tem permissão para criar avaliações para esta turma.")

    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.online_class = online_class
            evaluation.save()
            form.save_m2m() 
            success(request, f'A avaliação "{evaluation.title}" foi criada com sucesso. Agora, adicione as questões.')
            return redirect('manage_evaluation', evaluation_id=evaluation.id)
        else:
            error(request, 'Houve um erro no formulário. Por favor, verifique os dados.')
    else:
        form = EvaluationForm()

    context = {
        'form': form,
        'online_class': online_class,
        'title': f'New Assessment for {online_class.name}'
    }
    return render(request, 'questions/create_evaluation.html', context)

@login_required
@permission_required('questions.change_evaluation', raise_exception=True)
def manage_evaluation(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    online_class = evaluation.online_class

    if not Professor.objects.filter(user=request.user, prof_class=online_class).exists():
        raise PermissionDenied("You do not have permission to manage this exam.")

    problem_form = ProblemForm()
    
    if request.method == 'POST':
        
        if 'add_question' in request.POST:
            problem_id = request.POST.get('problem_id')
            problem = get_object_or_404(Problem, id=problem_id)
            
            with transaction.atomic():
                eval_problem, created = EvaluationProblem.objects.get_or_create(
                    evaluation=evaluation, problem=problem,
                    defaults={'weight': 1.0, 'order': evaluation.evaluationproblem_set.count() + 1}
                )

                if created:
                    all_test_cases = problem.testcase_set.all()
                    for tc in all_test_cases:
                        EvaluationProblemTestCase.objects.create(
                            evaluation_problem=eval_problem,
                            test_case=tc,
                            hidden=False  
                        )
                    success(request, f'The question "{problem.title}" was added with all test cases selected by default.')
                else:
                    error(request, f'The question "{problem.title}" is already in the exam.')
            
            search_query = request.POST.get('search_query', '')
            return redirect(f"{request.path}?q={search_query}")

        elif 'remove_question' in request.POST:
            evaluation_problem_id = request.POST.get('remove_question') 
            eval_problem = get_object_or_404(EvaluationProblem, id=evaluation_problem_id)
            problem_title = eval_problem.problem.title
            eval_problem.delete()
            success(request, f'The question "{problem_title}" was removed from the exam.')
            return redirect('manage_evaluation', evaluation_id=evaluation.id)

        elif 'update_weights' in request.POST:
            try:
                with transaction.atomic():
                    for key, value in request.POST.items():
                        if key.startswith('weight-'):
                            ep_id = int(key.split('-')[1])
                            weight_value = float(value.replace(',', '.')) 
                            if weight_value >= 0:
                                EvaluationProblem.objects.filter(id=ep_id, evaluation=evaluation).update(weight=weight_value)
                success(request, 'Exam updated successfuly.')
            except (ValueError, TypeError):
                error(request, 'Error updating exam.')
            return redirect('manage_class', onlineclass=evaluation.online_class.id)

        elif 'cancel_evaluation' in request.POST:
            if evaluation.start_date > timezone.now():
                evaluation.cancelled = True
                evaluation.save()
                success(request, 'The exam was cancelled.')
            else:
                error(request, 'Is not possible to edit an already started exam.')
            return redirect('manage_class', onlineclass=evaluation.online_class.id)

    search_query = request.GET.get('q', '')
    added_problem_ids = list(evaluation.evaluationproblem_set.values_list('problem__id', flat=True))
    
    available_problems = Problem.objects.exclude(id__in=added_problem_ids).filter(locked_problem=False).order_by('title')
    if search_query:
        available_problems = available_problems.filter(title__icontains=search_query, locked_problem=False).order_by('title')

    context = {
        'title': f'Manage exam: {evaluation.title}',
        'evaluation': evaluation,
        'added_problems': evaluation.evaluationproblem_set.order_by('order'),
        'available_problems': available_problems[:20], 
        'search_query': search_query,
        'problem_form': problem_form, 
        'started': timezone.now() > evaluation.start_date,
        'finished': timezone.now() > evaluation.end_date
    }
    return render(request, 'questions/manage_evaluation.html', context)


@require_POST
@login_required
def save_testcases_api(request, ep_id):
    eval_problem = get_object_or_404(EvaluationProblem, id=ep_id)
    
    if not Professor.objects.filter(user=request.user, prof_class=eval_problem.evaluation.online_class).exists():
        return JsonResponse({'status': 'error', 'message': 'Permission Denied'}, status=403)

    try:
        data = json.loads(request.body)
        test_cases_config = data.get('test_cases', [])

        with transaction.atomic():
            EvaluationProblemTestCase.objects.filter(evaluation_problem=eval_problem).delete()
            
            for config in test_cases_config:
                test_case = get_object_or_404(TestCase, id=config.get('id'))
                if test_case.problem == eval_problem.problem:
                    EvaluationProblemTestCase.objects.create(
                        evaluation_problem=eval_problem,
                        test_case=test_case,
                        hidden=config.get('hidden', False)
                    )
        
        return JsonResponse({'status': 'success', 'message': 'Configuração salva com sucesso.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@permission_required('questions.change_evaluation', raise_exception=True)
def edit_evaluation(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)

    if evaluation.start_date <= timezone.now():
        error(request, "Is not possible to edit an already started exam.")
        return redirect('manage_evaluation', evaluation_id=evaluation.id)

    if request.method == 'POST':
        form = EvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            form.save()
            success(request, 'Exam updated successfuly')
            return redirect('manage_evaluation', evaluation_id=evaluation.id)
    else:
        form = EvaluationForm(instance=evaluation)
    
    context = {
        'form': form,
        'evaluation': evaluation,
        'title': f'Edit Exam: {evaluation.title}'
    }
    return render(request, 'questions/edit_evaluation.html', context)

@login_required
def get_problem_details(request, problem_id):
    if not request.user.has_perm('questions.view_problem'):
        return JsonResponse({'error': 'Permission Denied'}, status=403)

    try:
        problem = Problem.objects.get(id=problem_id)
        test_cases = TestCase.objects.filter(problem=problem)

        data = {
            'id': problem.id,
            'title': problem.title,
            'content': problem.content,
            'question_type': problem.get_question_type_display(), 
            'test_cases': list(test_cases.values('id', 'content')) 
        }
        return JsonResponse(data)
    except Problem.DoesNotExist:
        return JsonResponse({'error': 'Problem not found'}, status=404)
    
def get_evaluation_problem_testcases_api(request, ep_id):
    eval_problem = get_object_or_404(EvaluationProblem, id=ep_id)
    
    if not Professor.objects.filter(user=request.user, prof_class=eval_problem.evaluation.online_class).exists():
        return JsonResponse({'error': 'Permission Denied'}, status=403)

    all_test_cases = eval_problem.problem.testcase_set.all()

    saved_configs = EvaluationProblemTestCase.objects.filter(evaluation_problem=eval_problem)
    
    saved_choices = {config.test_case_id: config.hidden for config in saved_configs}

    response_data = []
    for tc in all_test_cases:
        response_data.append({
            'id': tc.id,
            'content': tc.content,
            'selected': tc.id in saved_choices, 
            'hidden': saved_choices.get(tc.id, False) 
        })
        
    return JsonResponse({
        'problem_title': eval_problem.problem.title,
        'test_cases': response_data
    })

@login_required
def preview_problem(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    context = {
        'problem': problem,
        'test_cases': problem.testcase_set.all(),
        'title': f'Viewing: {problem.title}'
    }
    return render(request, 'questions/preview_problem.html', context)


@login_required
def configure_testcases(request, ep_id):
    eval_problem = get_object_or_404(EvaluationProblem, id=ep_id)
    all_test_cases = eval_problem.problem.testcase_set.all()

    if request.method == 'POST':
        selected_tc_ids = request.POST.getlist('selected_tc')
        hidden_tc_ids = request.POST.getlist('hidden_tc')

        with transaction.atomic():
            eval_problem.selected_test_cases.clear()
            for tc_id in selected_tc_ids:
                test_case = get_object_or_404(TestCase, id=tc_id)
                is_hidden = tc_id in hidden_tc_ids
                EvaluationProblemTestCase.objects.create(
                    evaluation_problem=eval_problem,
                    test_case=test_case,
                    hidden=is_hidden
                )
        success(request, 'Test Case Configuration saved successfuly.')
        return redirect('manage_evaluation', evaluation_id=eval_problem.evaluation.id)

    saved_configs = eval_problem.evaluationproblemtestcase_set.all()
    saved_choices = {config.test_case_id: config.hidden for config in saved_configs}
    
    context = {
        'eval_problem': eval_problem,
        'all_test_cases': all_test_cases,
        'saved_choices': saved_choices,
        'title': f'Configure Test Cases for "{eval_problem.problem.title}"'
    }
    return render(request, 'questions/configure_testcases.html', context)

@login_required
@permission_required('questions.add_problem', raise_exception=True)
def create_evaluation_problem(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    
    if not Professor.objects.filter(user=request.user, prof_class=evaluation.online_class).exists():
        raise PermissionDenied("You do not have permission to add questions to this Exam.")

    if request.method == 'POST':
        form = EvaluationProblemForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                cleaned_data = form.cleaned_data

                problem = Problem.objects.create(
                    title=cleaned_data.get('title'),
                    content=cleaned_data.get('content'),
                    question_type=cleaned_data.get('question_type'), 
                    test_case_generator=cleaned_data.get('test_case_generator'),
                    locked_problem=cleaned_data.get('locked_problem', False),
                    evaluation_problem=True 
                )

                Solution.objects.create(
                    problem=problem,
                    header=f"# Solução para a questão '{problem.title}'",
                    content="# N/A"
                )
                
                EvaluationProblem.objects.create(
                    evaluation=evaluation,
                    problem=problem,
                    weight=1.0, 
                    order=evaluation.evaluationproblem_set.count() + 1
                )

            success(request, f'The questions "{problem.title}" was added successfuly.')
            return redirect('manage_evaluation', evaluation_id=evaluation.id)
        else:
            error(request, 'It was not possible to add question.')
    else:
        form = EvaluationProblemForm()

    context = {
        'title': f'New Questions for "{evaluation.title}"',
        'evaluation': evaluation,
        'form': form 
    }
    return render(request, 'questions/create_evaluation_problem.html', context)

@require_POST
@login_required
@permission_required('questions.change_evaluation', raise_exception=True)
def update_question_order(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    if not Professor.objects.filter(user=request.user, prof_class=evaluation.online_class).exists():
        return JsonResponse({'status': 'error', 'message': 'Permission Denied'}, status=403)

    try:
        data = json.loads(request.body)
        ordered_ids = data.get('ordered_ids')

        if not ordered_ids:
            return JsonResponse({'status': 'error', 'message': 'Nenhum ID fornecido.'}, status=400)

        with transaction.atomic():
            for index, ep_id in enumerate(ordered_ids):
                EvaluationProblem.objects.filter(id=ep_id, evaluation_id=evaluation_id).update(order=index)

        return JsonResponse({'status': 'success', 'message': 'Updated order .'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@login_required
def evaluation_instructions(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)

    if request.user.userprofile.user_class != evaluation.online_class:
        raise PermissionDenied("You do not have permission to view this exam.")

    context = {
        'title': f'Instructions: {evaluation.title}',
        'evaluation': evaluation
    }
    return render(request, 'questions/evaluation_instructions.html', context)

@login_required
@require_POST 
def start_exam(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    user = request.user

    if user.userprofile.user_class != evaluation.online_class:
        raise PermissionDenied("You are not in the correct class for this exam.")

    now = timezone.now()
    if not (evaluation.start_date <= now <= evaluation.end_date):
        error(request, "This exam is not currently active.")
        return redirect('start') 

    existing_session = UserEvaluation.objects.filter(user=user, evaluation=evaluation).first()
    if existing_session:
        return redirect('take_exam', user_evaluation_id=existing_session.id)

    try:
        with transaction.atomic():
            user_evaluation_session = UserEvaluation.objects.create(
                user=user,
                evaluation=evaluation,
                start_time=now,
                user_class=user.userprofile.user_class
            )

            questions_in_exam = evaluation.evaluationproblem_set.all()
            for question in questions_in_exam:
                UserEvaluationProblem.objects.create(
                    user_evaluation=user_evaluation_session,
                    evaluation_problem=question
                )
        
        return redirect('take_exam', user_evaluation_id=user_evaluation_session.id)

    except Exception as e:
        LOGGER.error(f"Failed to start exam for user {user.id} on evaluation {evaluation.id}: {e}")
        error(request, "An unexpected error occurred while starting the exam. Please try again.")
        return redirect('evaluation_instructions', evaluation_id=evaluation.id)

@login_required
def take_exam(request, user_evaluation_id):
    user_evaluation = get_object_or_404(UserEvaluation, id=user_evaluation_id)

    if user_evaluation.user != request.user:
        raise PermissionDenied("You do not have permission to access this exam session.")

    if user_evaluation.submitted:
        error(request, "You have already submitted this exam.")
        return redirect('start')
    
    problems_qs = user_evaluation.userevaluationproblem_set.all().order_by('evaluation_problem__order')
    
    problems_list = list(problems_qs)
    
    if user_evaluation.evaluation.random_sort:
        random.seed(user_evaluation.id)
        random.shuffle(problems_list)

    evaluation_duration = user_evaluation.evaluation.end_date - user_evaluation.evaluation.start_date
    time_elapsed = timezone.now() - user_evaluation.start_time
    remaining_time = evaluation_duration - time_elapsed
    remaining_seconds = max(0, int(remaining_time.total_seconds()))

    print("remaining", remaining_seconds)
    context = {
        'title': f"In Progress: {user_evaluation.evaluation.title}",
        'user_evaluation': user_evaluation,
        'problems': problems_list,
        'remaining_seconds': remaining_seconds,
    }
    
    return render(request, 'questions/take_exam.html', context)

@login_required
def solve_evaluation_problem(request, uep_id):
    user_eval_problem = get_object_or_404(UserEvaluationProblem, id=uep_id)
    user_evaluation = user_eval_problem.user_evaluation

    if user_evaluation.user != request.user:
        raise PermissionDenied("You do not have permission to access this problem.")

    evaluation_duration = user_evaluation.evaluation.end_date - user_evaluation.evaluation.start_date
    time_elapsed = timezone.now() - user_evaluation.start_time
    remaining_time = evaluation_duration - time_elapsed
    remaining_seconds = max(0, int(remaining_time.total_seconds()))
    
    problems_qs = user_evaluation.userevaluationproblem_set.all().order_by('evaluation_problem__order')
    
    problems_list = list(problems_qs)

    if user_evaluation.evaluation.random_sort:
        random.seed(user_evaluation.id)
        random.shuffle(problems_list)

    problem_ids = []

    for problem in problems_list:
        problem_ids.append(problem.id)

    current_index = problem_ids.index(uep_id)
    
    prev_uep_id = problem_ids[current_index - 1] if current_index > 0 else None
    next_uep_id = problem_ids[current_index + 1] if current_index < len(problem_ids) - 1 else None

    context = {
        'title': f"Solving: {user_eval_problem.evaluation_problem.problem.title}",
        'problem': user_eval_problem,
        'remaining_seconds': remaining_seconds,
        'user_evaluation_id': user_evaluation.id,
        'prev_uep_id': prev_uep_id,
        'next_uep_id': next_uep_id
    }
    return render(request, 'questions/solve_evaluation_problem.html', context)

@login_required
@require_POST
def save_evaluation_progress(request, uep_id):
    try:
        user_eval_problem = get_object_or_404(UserEvaluationProblem, id=uep_id)

        if user_eval_problem.user_evaluation.user != request.user:
            return JsonResponse({'status': 'error', 'message': 'Permission Denied'}, status=403)
        
        data = json.loads(request.body)
        solution_text = data.get('solution', '')
        
        user_eval_problem.solution = solution_text
        user_eval_problem.save()
        
        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@login_required
def get_public_test_cases(request, uep_id):
    user_eval_problem = get_object_or_404(UserEvaluationProblem, id=uep_id)

    if user_eval_problem.user_evaluation.user != request.user:
        return JsonResponse({'error': 'Permission Denied'}, status=403)
    
    eval_problem = user_eval_problem.evaluation_problem

    public_test_cases = eval_problem.evaluationproblemtestcase_set.filter(hidden=False)
    
    test_cases_data = [json.loads(ptc.test_case.content) for ptc in public_test_cases]

    return JsonResponse({'test_cases': test_cases_data})

def submit_exam(request, user_evaluation_id):
    user_evaluation = get_object_or_404(UserEvaluation, id=user_evaluation_id)

    if user_evaluation.user != request.user:
        raise PermissionDenied
    
    if user_evaluation.submitted:
        error(request, "This exam has already been submitted.")
        return redirect('start')
        
    if timezone.now() > user_evaluation.evaluation.end_date:
        error(request, "The deadline for this exam has passed.")
        return redirect('start')

    user_evaluation.submitted = True
    user_evaluation.end_time = timezone.now()
    user_evaluation.save()

    success(request, f'Your submission for "{user_evaluation.evaluation.title}" was successful.')
    return redirect('submission_confirmation')


@login_required
def submission_confirmation(request):
    return render(request, 'questions/exam_submission_confirmation.html', {'title': 'Submission Successful'})

@login_required
@permission_required('questions.change_evaluation', raise_exception=True)
def grading_dashboard(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    
    submissions = UserEvaluation.objects.filter(
        evaluation=evaluation,
        submitted=True
    ).order_by('user__first_name', 'user__last_name')

    total_weight = evaluation.evaluationproblem_set.aggregate(
        total=Sum('weight')
    )['total'] or 0.0

    total_questions = evaluation.evaluationproblem_set.count()

    for sub in submissions:
            answered_count = sub.userevaluationproblem_set.exclude(solution='').count()
            sub.progress_string = f"{answered_count} of {total_questions}"

    context = {
        'title': f'Grading: {evaluation.title}',
        'evaluation': evaluation,
        'submissions': submissions,
        'total_weight': total_weight,
    }
    return render(request, 'questions/grading_dashboard.html', context)

@require_POST
@login_required
@permission_required('questions.change_evaluation', raise_exception=True)
@transaction.atomic
def run_autograder(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    submissions = UserEvaluation.objects.filter(evaluation=evaluation, submitted=True)
    
    audience = settings.WORKER_NODE_HOST + settings.WORKER_NODE_PORT
    endpoint = audience + "/multi_process"
    
    headers = {}
    if os.getenv('ENVIRONMENT') == 'prod':
        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
        headers['Authorization'] = f'Bearer {id_token}'

    for submission in submissions:
        student_problems = submission.userevaluationproblem_set.all()

        for uep in student_problems:
            problem = uep.evaluation_problem.problem
            if problem.question_type == 'C' and uep.solution:
                
                all_exam_test_cases = uep.evaluation_problem.evaluationproblemtestcase_set.all()
                test_cases_to_run = [json.loads(eptc.test_case.content) for eptc in all_exam_test_cases]

                solution_obj = Solution.objects.filter(problem=problem, language__name='Python', ignore=False).first()
                if not solution_obj:
                    LOGGER.error(f"No valid solution found for problem {problem.id} to grade UEP {uep.id}")
                    continue

                form_data = {
                    'prog_lang': 'Python',
                    'professor_code': solution_obj.content,
                    'func': solution_obj.header,
                    'return_type': solution_obj.return_type,
                    'test_cases': json.dumps(test_cases_to_run),
                    'problem_id': problem.id, 
                }
                
                mem_zip = BytesIO()
                with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr("run_me", uep.solution)
                mem_zip.seek(0)

                files = {'file': ('extract-me.zip', mem_zip.read(), 'application/zip')}

                try:
                    response = requests.post(endpoint, data=form_data, files=files, headers=headers)
                    response.raise_for_status()
                    results = response.json()
                    
                    passed_count = sum(1 for item in results if item.get('result', {}).get('isCorrect'))
                    total_count = len(test_cases_to_run)
                    
                    uep.test_case_hits = passed_count
                    if total_count > 0:
                        weight = uep.evaluation_problem.weight
                        uep.grade = (passed_count / total_count) * weight
                    else:
                        uep.grade = 0
                    
                    uep.save()
                    
                except Exception as e:
                    LOGGER.error(f"Auto-grader failed for UEP {uep.id}: {e}")
                    continue
        
        submission.score = sum(uep.grade for uep in student_problems if uep.grade is not None)
        submission.save()

    evaluation.graded = True
    evaluation.save()
    success(request, 'The auto-grader has finished processing all submissions.')
    return redirect('grading_dashboard', evaluation_id=evaluation.id)

@require_POST
@login_required
@permission_required('questions.change_evaluation', raise_exception=True)
def release_grades(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    evaluation.show_grades = True
    evaluation.save()
    success(request, f'Grades for "{evaluation.title}" have been released to students.')
    return redirect('grading_dashboard', evaluation_id=evaluation.id)

@login_required
@permission_required('questions.change_evaluation', raise_exception=True)
def grade_student_submission(request, ue_id):
    submission = get_object_or_404(UserEvaluation, id=ue_id)
    problems = submission.userevaluationproblem_set.order_by('evaluation_problem__order')

    total_weight = submission.evaluation.evaluationproblem_set.aggregate(
        total=Sum('weight')
    )['total'] or 0.0

    context = {
        'title': f'Grading for {submission.user.get_full_name()}',
        'submission': submission,
        'problems': problems,
        'total_weight': total_weight, 
    }
    return render(request, 'questions/grade_student_submission.html', context)

@login_required
@permission_required('questions.change_evaluation', raise_exception=True)
def grade_evaluation_problem(request, uep_id):
    uep = get_object_or_404(UserEvaluationProblem, id=uep_id)
    submission = uep.user_evaluation
    
    if request.method == 'POST':
        form = GradeSubmissionForm(request.POST, instance=uep)
        if form.is_valid():
            form.save()
            all_problems = submission.userevaluationproblem_set.all()
            submission.score = sum(p.grade for p in all_problems if p.grade is not None)
            submission.save()
            
            success(request, 'Grade and feedback saved successfully.')
            return redirect('grade_student_submission', ue_id=submission.id)
    else:
        form = GradeSubmissionForm(instance=uep)
        
    context = {
        'title': f'Grading: {uep.evaluation_problem.problem.title}',
        'uep': uep,
        'form': form, 
        'style_right_card': 'height: calc(45vh - 30px);' if uep.evaluation_problem.problem.question_type == 'C' else 'height: 100%; margin: 0;'
    }
    return render(request, 'questions/grade_evaluation_problem.html', context)