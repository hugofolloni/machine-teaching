from django.urls import path
from django.views.generic import TemplateView

from . import views, context_processors
from django.urls import re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import ProblemDetailView



urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path('', views.index, name='index'),
    path('saveaccess', views.save_access, name='saveaccess'),
    path('saveinteractive', views.save_interactive, name='saveinteractive'),
    path('saveprofile', context_processors.context, name='saveprofile'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('saveuniversity', views.save_university, name='saveuniversity'),
    path('start', views.start, name='start'),
    path('next', views.get_next_problem, name='next'),
    path('savelog', views.save_user_log, name='savelog'),
    path('export', views.export, name='export'),
    path('update_strategy', views.update_strategy, name='update_strategy'),
    path('signup', views.signup, name='signup'),
    path('past_problems', views.get_past_problems, name='past_problems'),
    path('past_solutions/<int:id>', views.get_user_solution,
         name='past_solutions'),
    path('student_solutions/<int:id>', views.get_student_logs,
         name='student_solutions'),
    path('student_solutions/<int:id>/<int:chapter>', views.get_student_solutions,
         name='student_solutions'),
    path('student_solutions/<int:id>/<int:chapter>/<int:problem>',
         views.get_student_logs, name='student_solutions'),
    path('problem_solutions/<int:problem_id>', views.get_past_solutions, name='problem_solutions'),
    path('problem_solutions/<int:problem_id>/<int:class_id>', views.get_problem_solutions, name='problem_solutions'),
    path('chapters', views.get_chapter_problems, name='chapters'),
    path('chapters/<int:chapter>', views.show_chapter, name='show_chapter'),
    path('new_chapter', views.new_chapter, name='new_chapter'),
    path('new', views.new_problem, name='new'),
    path('new/<int:chapter>', views.new_problem, name='new'),
    path('outcomes', views.show_outcome, name='show_outcome'),
    path('dashboard', views.get_dashboard, name='dashboard'),
    path('student_dashboard/<int:id>', views.get_student_dashboard, name='student_dashboard'),
    path('classes', views.classes, name='classes'),
    path('classes/manage/<int:onlineclass>', views.manage_class, name='manage_class'),
    path('classes/dashboard/<int:onlineclass>', views.get_class_dashboard, name='class_dashboard1'),
    path('classes/old_dashboard/<int:onlineclass>', views.get_class_dashboard1, name='class_dashboard'),
    path('class_active', views.class_active, name='class_active'),
    path('manager_dashboard', views.get_manager_dashboard, name='manager_dashboard'),
    path('delete_deadline/<int:onlineclass>/<int:deadline>', views.delete_deadline, name='delete_deadline'),
    path('terms_and_conditions', TemplateView.as_view(
        template_name='questions/conditions.html'),
        name='terms_and_conditions'),
    path('privacy', TemplateView.as_view(
        template_name='questions/privacy.html'),
        name='privacy'),
    path('about', views.about, name='about'),
    path('dashboard1', views.get_dashboard1, name='dashboard1'),  
    path('student_dashboard1/<int:id>', views.get_student_dashboard1, name='student_dashboard1'),
    path('python_tutor', views.python_tutor, name='python_tutor'),
    path('profile', views.profile, name='profile'), 

    # path('attempts/', views.AttemptsList.as_view(), name='attempts'),
    # path('recommendations/', views.Recommendations.as_view(), name='recommendations'),
    path('submit_code/', views.submit_code, name='submit_code'),   #Endpoint responsável pela requisição feita para o worker-node
    #path('problem_details/<int:problem_id>/', ProblemDetailView.as_view(), name='problem-detail'),    #Endpoint para fornecer detalhes de problemas parar o worker-node (se a API não for usada, COMENTAR)

    # DEBUG PURPOSES
    path('<int:problem_id>/', views.show_problem, name='show_problem'),

    # View to redirect to embed form
    path('satisfaction_form', views.satisfaction_form, name='satisfaction_form'),

    path('classes/manage/<int:onlineclass_id>/evaluations/new/', views.create_evaluation, name='create_evaluation'),
    path('evaluations/manage/<int:evaluation_id>/', views.manage_evaluation, name='manage_evaluation'),
    path('evaluations/edit/<int:evaluation_id>/', views.edit_evaluation, name='edit_evaluation'),
    path('evaluations/manage/<int:evaluation_id>/add-question/', views.create_evaluation_problem, name='create_evaluation_problem'),
    path('api/evaluation-problem/<int:ep_id>/testcases/', views.get_evaluation_problem_testcases_api, name='get_evaluation_problem_testcases_api'),
    path('problem/<int:problem_id>/preview/', views.preview_problem, name='preview_problem'),
    path('evaluation-problem/<int:ep_id>/configure-testcases/', views.configure_testcases, name='configure_testcases'),
    path('api/evaluation-problem/<int:ep_id>/testcases/save/', views.save_testcases_api, name='save_testcases_api'),
    path('api/problem/<int:problem_id>/details/', views.get_problem_details, name='get_problem_details'),
    path('evaluation/<int:evaluation_id>/manage/update-order/', views.update_question_order, name='update_question_order'),
    path('evaluation/<int:evaluation_id>/instructions/', views.evaluation_instructions, name='evaluation_instructions'),
    path('evaluation/<int:evaluation_id>/start/', views.start_exam, name='start_exam'),
    path('take_exam/<int:user_evaluation_id>/', views.take_exam, name='take_exam'),
    path('evaluation_problem/<int:uep_id>/solve/', views.solve_evaluation_problem, name='solve_evaluation_problem'),
    path('api/evaluation_problem/<int:uep_id>/save/', views.save_evaluation_progress, name='save_evaluation_progress'),
    path('api/evaluation_problem/<int:uep_id>/public_test_cases/', views.get_public_test_cases, name='get_public_test_cases'),
    path('submit_exam/<int:user_evaluation_id>/', views.submit_exam, name='submit_exam'),
    path('exam/submitted/', views.submission_confirmation, name='submission_confirmation'),
    path('evaluation/<int:evaluation_id>/grading/', views.grading_dashboard, name='grading_dashboard'),
    path('evaluation/<int:evaluation_id>/run_autograder/', views.run_autograder, name='run_autograder'),
    path('evaluation/<int:evaluation_id>/release_grades/', views.release_grades, name='release_grades'),
    path('user_evaluation/<int:ue_id>/grade/', views.grade_student_submission, name='grade_student_submission'),
    path('user_evaluation_problem/<int:uep_id>/grade/', views.grade_evaluation_problem, name='grade_evaluation_problem'),
    path('evaluation/<int:evaluation_id>/export_grades/', views.export_grades_csv, name='export_grades_csv'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += staticfiles_urlpatterns()
