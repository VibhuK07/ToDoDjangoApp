from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.db.models import Q
from datetime import timedelta

class Project(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} by {self.creator.username}"

    class Meta:
        ordering = ['-start_date']
        unique_together = []

class Task(models.Model):
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed')
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    parent_task = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subtasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration_days = models.PositiveIntegerField()
    is_private = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tasks'
    )
    is_completed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='NOT_STARTED'
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.parent_task:
            if self.parent_task.project != self.project:
                raise ValidationError("Subtasks must belong to the same project as parent")
            self.is_private = self.parent_task.is_private
        super().save(*args, **kwargs)

    def can_start(self):
        for group in self.dependency_groups.all():
            completed_status = [d.depends_on.is_completed for d in group.dependencies.all()]
            if group.logic_type == 'AND' and not all(completed_status):
                return False
            if group.logic_type == 'OR' and not any(completed_status):
                return False
        return True

    def update_dependent_tasks(self):
        for dependency in self.dependent_tasks.all():
            task = dependency.group.task
            if task.can_start() and task.status == 'NOT_STARTED':
                task.status = 'IN_PROGRESS'
                task.save()

    class Meta:
        ordering = ['-project__start_date', 'title']

class DependencyGroup(models.Model):
    LOGIC_TYPES = [('AND', 'All'), ('OR', 'Any')]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependency_groups')
    logic_type = models.CharField(max_length=3, choices=LOGIC_TYPES)

    class Meta:
        unique_together = ['task', 'logic_type']

class Dependency(models.Model):
    group = models.ForeignKey(DependencyGroup, on_delete=models.CASCADE, related_name='dependencies')
    depends_on = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependent_tasks')

    def clean(self):
        if self.group.task.project != self.depends_on.project:
            raise ValidationError("Dependencies must be within the same project!")
        if self.group.task == self.depends_on:
            raise ValidationError("Task cannot depend on itself!")

    class Meta:
        unique_together = ['group', 'depends_on']

class ProjectCollaborator(models.Model):
    ROLES = [('EDIT', 'Editor'), ('VIEW', 'Viewer'), ('ADMIN', 'Project Admin')]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collaborations')
    role = models.CharField(max_length=5, choices=ROLES, default='VIEW')

    class Meta:
        unique_together = ['project', 'user']