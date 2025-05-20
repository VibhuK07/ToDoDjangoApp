# api/admin.py
from django.contrib import admin
from .models import Project, Task, Dependency, ProjectCollaborator, DependencyGroup

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'start_date', 'is_public']
    raw_id_fields = ['creator']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'assigned_to', 'status']
    raw_id_fields = ['project', 'parent_task', 'assigned_to']

@admin.register(Dependency)
class DependencyAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_task', 'depends_on']
    raw_id_fields = ['group', 'depends_on']
    
    def get_task(self, obj):
        return obj.group.task
    get_task.short_description = 'Task'

@admin.register(DependencyGroup)
class DependencyGroupAdmin(admin.ModelAdmin):
    list_display = ['task', 'logic_type']
    raw_id_fields = ['task']

@admin.register(ProjectCollaborator)
class ProjectCollaboratorAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'role']
    raw_id_fields = ['project', 'user']