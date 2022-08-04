from questions.models import (Professor, Problem, Deadline, User, UserLogView, OnlineClass)
import csv
from datetime import datetime

from questions.get_dashboards import predict_drop_out

def count_on_time_exercises(user, chapters, onlineclass):
    on_time_list = []
    for c in chapters:
        try:
            problems = Problem.objects.filter(chapter=c)
            deadline = Deadline.objects.filter(chapter=c,
                                            onlineclass=onlineclass).first().deadline
            on_time_exercises = UserLogView.objects.filter(user=user,
                                                        problem__in=problems,
                                                        final_outcome='P',
                                                        timestamp__gte=onlineclass.start_date,
                                                        timestamp__lte=deadline)
            on_time_list.append(on_time_exercises.count())
        except:
            pass
    return sum(on_time_list)

def count_exercises(user, chapters, onlineclass):
    on_time_list = []
    for c in chapters:
        try:
            problems = Problem.objects.filter(chapter=c)
            deadline = Deadline.objects.filter(chapter=c,
                                            onlineclass=onlineclass).first().deadline
            on_time_exercises = UserLogView.objects.filter(user=user,
                                                        problem__in=problems,
                                                        final_outcome='P',
                                                        timestamp__gte=onlineclass.start_date)
            on_time_list.append(on_time_exercises.count())
        except:
            pass
    return sum(on_time_list)


classes = [102,103,97,99,100,101,104,109,110,98,112,113,115,117]
date = datetime(2022,2,1)
semester = '2021_2'

f = open("questions/class_analysis/"+semester+"/summary_"+semester+".csv","w+")
writer = csv.writer(f)
writer.writerow(['turma','aluno','previsao','exercicios_resolvidos_8_9','resultado'])


for id in classes:
    onlineclass = OnlineClass.objects.get(pk=id)
    professors = Professor.objects.all().values_list('user')
    profiles = UserLogView.objects.filter(user_class=onlineclass).values("user").distinct()
    students = User.objects.filter(pk__in=profiles).exclude(pk__in=professors).order_by("first_name","last_name")

    i=1
    for student in students:
        try:
            predict = predict_drop_out(student.id, onlineclass, date)
            on_time_exercises = count_on_time_exercises(student, [17,19], onlineclass)

            if predict < 7:
                if on_time_exercises < 7:
                    result = "VP"
                else:
                    result = "FP"
            else:
                if on_time_exercises < 7:
                    result = "FN"
                else:
                    result = "VN"

            writer.writerow([onlineclass.name,
                             student.first_name+" "+student.last_name,
                             predict,
                             on_time_exercises,
                             result])
            i+=1
        except:
            pass
            
f.close()