from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
import logging

from .models import Course, Enrollment, Question, Choice, Submission

logger = logging.getLogger(__name__)

# ---------------- AUTH (keep yours as-is) ---------------- #

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)

    username = request.POST['username']
    password = request.POST['psw']

    if User.objects.filter(username=username).exists():
        context['message'] = "User already exists."
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)

    user = User.objects.create_user(username=username, password=password)
    login(request, user)
    return redirect('onlinecourse:index')


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('onlinecourse:index')

        context['message'] = "Invalid username or password."
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)

    return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


# ---------------- COURSE ---------------- #

class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.all()


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


# ---------------- ENROLL ---------------- #

def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.user.is_authenticated:
        Enrollment.objects.get_or_create(user=request.user, course=course)

    return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))


# ---------------- EXAM ---------------- #

def extract_answers(request):
    selected = []
    for key in request.POST:
        if key.startswith('choice'):
            selected.append(int(request.POST[key]))
    return selected


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    submission = Submission.objects.create(enrollment=enrollment)

    selected_ids = extract_answers(request)

    submission.choices.add(*selected_ids)
    submission.save()

    return redirect('onlinecourse:show_exam_result', course.id, submission.id)


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, id=submission_id)

    selected_ids = submission.choices.values_list('id', flat=True)

    score = 0
    total = course.question_set.count()

    for question in course.question_set.all():
        correct = question.choice_set.filter(is_correct=True).values_list('id', flat=True)

        if any(cid in selected_ids for cid in correct):
            score += 1

    return render(request, 'onlinecourse/exam_result_bootstrap.html', {
        'course': course,
        'score': score,
        'total': total
    })
    




