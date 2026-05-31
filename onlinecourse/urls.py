from django.urls import path
from . import views

app_name = 'onlinecourse'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='index'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details'),

    path('enroll/<int:course_id>/', views.enroll, name='enroll'),

    # ✅ EXAM ROUTES
    path('submit/<int:course_id>/', views.submit, name='submit'),
    path('result/<int:course_id>/<int:submission_id>/', views.show_exam_result, name='show_exam_result'),

    # AUTH
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('registration/', views.registration_request, name='registration'),
]