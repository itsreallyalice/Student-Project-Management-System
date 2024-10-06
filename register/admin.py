
from django.urls import path
from django.contrib import admin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.html import format_html


# Register your models here.
from .models import Supervisor, Student, Project, ProjectTopic

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1

@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'surname', 'email', 'sussex_id', 'department', 'telephone_number', 'list_projects')
    search_fields = ('name', 'surname', 'sussex_id', 'department', 'user__username', 'email')
    inlines = [ProjectInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('project_set')

    def list_projects(self, obj):
        projects = obj.project_set.all()
        return format_html(", ".join([p.title for p in projects]))

    list_projects.short_description = 'Projects'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'surname', 'email', 'sussex_id', 'course', 'selected_project')
    search_fields = ('name', 'surname', 'sussex_id', 'course', 'user__username', 'email')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('project_set')

    def selected_project(self, obj):
        projects = obj.project_set.all()
        if projects.exists():
            return ', '.join([p.title for p in projects])
        return 'No Project'
    selected_project.short_description = 'Selected/Proposed Project'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'supervisor', 'proposed_by')
    list_filter = ('status', 'supervisor', 'proposed_by')
    search_fields = ('title', 'supervisor__user__username', 'proposed_by__user__username')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('supervisor', 'proposed_by')

@admin.register(ProjectTopic)
class ProjectTopicAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

    filter_horizontal = ('projects',)

