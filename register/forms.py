from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

from .models import Supervisor, Student, Project, ProjectTopic


class ProjectTopicForm(forms.ModelForm):
    class Meta:
        model = ProjectTopic
        fields = ['title', 'description']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) > 100:
            raise ValidationError("Title must be 100 characters or fewer.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) > 1000:
            raise ValidationError("Description must be 1000 characters or fewer.")
        return description

class ProjectProposalForm(forms.ModelForm):
    project_topics = forms.ModelMultipleChoiceField(
        queryset=ProjectTopic.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Project Topics"
    )

    class Meta:
        model = Project
        fields = ['title', 'description', 'required_skills', 'supervisor']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) > 200:
            raise ValidationError("Title must be 200 characters or fewer.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) > 1000:
            raise ValidationError("Description must be 1000 characters or fewer.")
        return description

class ProjectRequestForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['title', 'description', 'required_skills', 'supervisor', 'status', 'proposed_by']

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput)

class SupervisorForm(UserCreationForm):
    department = forms.CharField(max_length=100)
    telephone_number = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class StudentForm(UserCreationForm):
    course = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
