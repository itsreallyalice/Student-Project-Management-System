from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, ProjectProposalForm, ProjectRequestForm, ProjectTopicForm
from .models import Supervisor, Student, Project, Notification

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SupervisorSerializer, StudentSerializer, ProjectSerializer



class ProjectListView(APIView):
    def get(self, request, supervisorid=None):
        if supervisorid == 'all':
            projects = Project.objects.all()
        else:
            projects = Project.objects.filter(supervisor__id=supervisorid)

        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)


class SupervisorListView(APIView):
    def get(self, request, studentid=None):
        if studentid == 'all':
            supervisors = Supervisor.objects.all()
        else:
            supervisors = Supervisor.objects.filter(student__id=studentid)

        serializer = SupervisorSerializer(supervisors, many=True)
        return Response(serializer.data)


class StudentListView(APIView):
    def get(self, request, supervisorid=None):
        if supervisorid == 'all':
            students = Student.objects.all()
        else:
            students = Student.objects.filter(project__supervisor__id=supervisorid)

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid login credentials')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def home(request):
    user = request.user
    if Supervisor.objects.filter(user=user).exists():
        return redirect('supervisor_home')
    elif Student.objects.filter(user=user).exists():
        return redirect('student_home')
    elif user.is_superuser:
        return redirect('admin:index')  # Redirect to the Django admin index page
    return render(request, 'home.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def student_home(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        # Redirect to a different page if the user is not a student
        return redirect('unauthorised')
    return render(request, 'student_home.html')

@login_required
def proposed_projects(request):
    student = get_object_or_404(Student, user=request.user)
    proposed_projects = Project.objects.filter(status='Proposed')

    # Check if the student has already proposed or requested a project
    existing_project = Project.objects.filter(proposed_by=student).first()

    projects_with_topics = []
    for project in proposed_projects:
        topics = project.projecttopic_set.all()  # Get the related topics
        projects_with_topics.append({
            'project': project,
            'topics': topics
        })

    return render(request, 'proposed_projects.html', {
        'projects_with_topics': projects_with_topics,
        'existing_project': existing_project,
    })


@login_required
def propose_project(request):
    student = get_object_or_404(Student, user=request.user)

    existing_project = Project.objects.filter(proposed_by=student).first()

    if existing_project:
        return render(request, 'proposed_project_detail.html', {
            'project': existing_project,
        })

    if request.method == 'POST':
        proposal_form = ProjectProposalForm(request.POST)
        if proposal_form.is_valid():
            new_project = proposal_form.save(commit=False)
            new_project.proposed_by = student
            new_project.status = 'Requested'
            new_project.save()

            # Add selected topics to the project
            project_topics = proposal_form.cleaned_data['project_topics']
            new_project.projecttopic_set.set(project_topics)

            # Send notification to supervisor
            Notification.objects.create(
                user=new_project.supervisor.user,
                message=f"New project proposed by {student.user.username}: {new_project.title}"
            )

            return redirect('student_home')
    else:
        proposal_form = ProjectProposalForm()

    return render(request, 'propose_project.html', {
        'proposal_form': proposal_form,
    })


@login_required
def request_project(request, project_id):
    student = get_object_or_404(Student, user=request.user)
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        project.status = 'Requested'
        project.proposed_by = student
        project.save()

        # Send notification to supervisor
        Notification.objects.create(
            user=project.supervisor.user,
            message=f"Project requested by {request.user.username}: {project.title}"
        )

        return redirect('proposed_projects')

    # return render(request, 'request_project.html', {
    #     'request_form': request_form,
    #     'project': project,
    # })


def unauthorised(request):
    return render(request, 'unauthorised.html')

@login_required
def supervisor_home(request):
    try:
        supervisor = get_object_or_404(Supervisor, user=request.user)
    except Supervisor.DoesNotExist:
        return redirect('unauthorised')
    notifications = Notification.objects.filter(user=request.user, read=False)
    print(notifications)

    return render(request, 'supervisor_home.html', {
        'notifications': notifications,
    })


@login_required
def register_topic(request):
    user = request.user
    supervisor = get_object_or_404(Supervisor, user=user)
    if request.method == 'POST':
        topic_form = ProjectTopicForm(request.POST)
        if topic_form.is_valid():
            new_topic = topic_form.save(commit=False)
            new_topic.supervisor = supervisor
            new_topic.save()
            return redirect('supervisor_home')
    else:
        topic_form = ProjectTopicForm()

    return render(request, 'register_topic.html', {
        'topic_form': topic_form,
    })


@login_required
def register_proposal(request):
    user = request.user
    supervisor = get_object_or_404(Supervisor, user=user)

    if request.method == 'POST':
        proposal_form = ProjectProposalForm(request.POST)
        if proposal_form.is_valid():
            new_proposal = proposal_form.save(commit=False)
            new_proposal.supervisor = supervisor
            new_proposal.status = 'Proposed'
            new_proposal.save()

            # Add selected topics to the project
            project_topics = proposal_form.cleaned_data['project_topics']
            new_proposal.projecttopic_set.set(project_topics)

            return redirect('supervisor_home')
    else:
        proposal_form = ProjectProposalForm()
    proposal_form.fields.pop('supervisor')
    return render(request, 'register_proposal.html', {
        'proposal_form': proposal_form,
    })


@login_required
def manage_proposals(request):
    notifications = Project.objects.filter(status='Requested')
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        if 'accept_project' in request.POST:
            project = Project.objects.get(id=project_id)
            print(project.proposed_by)
            project.status = 'Accepted'
            print(project.proposed_by)
            project.save()
        elif 'reject_project' in request.POST:
            project = Project.objects.get(id=project_id)
            project.delete()
        return redirect('manage_proposals')

    return render(request, 'manage_proposals.html', {
        'notifications': notifications,
    })


@login_required
def accepted_projects(request):
    user = request.user
    supervisor = get_object_or_404(Supervisor, user=user)
    accepted_projects = Project.objects.filter(supervisor=supervisor, status='Accepted')

    return render(request, 'accepted_projects.html', {
        'accepted_projects': accepted_projects,
    })


def custom_report_view(request):
    supervisors = Supervisor.objects.prefetch_related('projects').all()
    students = Student.objects.select_related('selected_project').all()
    return render(request, 'admin/custom_report.html', {
        'supervisors': supervisors,
        'students': students
    })
