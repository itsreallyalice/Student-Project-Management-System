from django.urls import path
from . import views
from .views import register_topic, register_proposal, manage_proposals, accepted_projects, custom_report_view, \
    ProjectListView, SupervisorListView, StudentListView, unauthorised

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('student_home/', views.student_home, name='student_home'),
    path('supervisor_home/', views.supervisor_home, name='supervisor_home'),
    path('register-topic/', register_topic, name='register_topic'),
    path('register-proposal/', register_proposal, name='register_proposal'),
    path('manage-proposals/', manage_proposals, name='manage_proposals'),
    path('accepted-projects/', accepted_projects, name='accepted_projects'),
    path('proposed-projects/', views.proposed_projects, name='proposed_projects'),
    path('propose-project/', views.propose_project, name='propose_project'),
    path('request-project/<int:project_id>/', views.request_project, name='request_project'),
    path('custom-report/', custom_report_view, name='custom_report'),
    path('project/<str:supervisorid>/', ProjectListView.as_view(), name='project-list'),
    path('supervisor/<str:studentid>/', SupervisorListView.as_view(), name='supervisor-list'),
    path('student/<str:supervisorid>/', StudentListView.as_view(), name='student-list'),
    path('unauthorised/', unauthorised, name='unauthorised'),
]