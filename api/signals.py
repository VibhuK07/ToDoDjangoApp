# api/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task, Dependency, DependencyGroup, ProjectCollaborator
from .scheduling import calculate_project_schedule

@receiver(post_save, sender=Task)
def handle_task_updates(sender, instance, **kwargs):
    """NEW: Enhanced parent task status management"""
    # Update dependent tasks when marked completed
    if instance.is_completed:
        instance.update_dependent_tasks()
    
    # Parent task status rollback logic
    if instance.parent_task:
        parent = instance.parent_task
        
        # Calculate completion status
        completed_subtasks = parent.subtasks.filter(is_completed=True).count()
        total_subtasks = parent.subtasks.count()
        all_completed = (completed_subtasks == total_subtasks)
        
        # Update parent completion status
        parent.is_completed = all_completed
        
        # NEW: Determine parent status
        if all_completed:
            parent.status = 'COMPLETED'
        else:
            # Check if any subtask is in progress
            if parent.subtasks.filter(status='IN_PROGRESS').exists():
                parent.status = 'IN_PROGRESS'
            else:
                parent.status = 'NOT_STARTED'
        
        parent.save()

@receiver(post_save, sender=Task)
def update_subtask_privacy(sender, instance, **kwargs):
    """Propagate privacy changes to subtasks"""
    if instance.subtasks.exists():
        Task.objects.filter(parent_task=instance).update(is_private=instance.is_private)

@receiver(post_save, sender=Dependency)
@receiver(post_save, sender=DependencyGroup)
@receiver(post_save, sender=ProjectCollaborator)
def update_schedule_on_change(sender, instance, **kwargs):
    """Trigger schedule recalculation"""
    project = None
    if isinstance(instance, Dependency):
        project = instance.group.task.project
    elif isinstance(instance, DependencyGroup):
        project = instance.task.project
    elif isinstance(instance, ProjectCollaborator):
        project = instance.project
    if project:
        calculate_project_schedule(project)