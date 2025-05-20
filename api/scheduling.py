# api/scheduling.py
from datetime import date, timedelta
from collections import defaultdict, deque
from .models import Task, DependencyGroup

# NEW FUNCTION ADDED FOR PROJECT SWITCHING LOGIC
def handle_multiple_projects(user):
    """Determine if user is already working on another project"""
    current_tasks = user.assigned_tasks.filter(is_completed=False)
    return current_tasks.first().project if current_tasks.exists() else None

def calculate_project_schedule(project):
    # Initialize data structures
    tasks = Task.objects.filter(project=project).prefetch_related(
        'dependency_groups__dependencies__depends_on',
        'assigned_to'
    )
    task_map = {task.id: task for task in tasks}
    schedule = {}
    
    # Track user availability {user_id: next_available_date}
    user_availability = defaultdict(lambda: project.start_date)
    
    # Build dependency graph and in-degree count
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    task_order = []

    # Kahn's algorithm for topological sort
    for task in tasks:
        deps = []
        for group in task.dependency_groups.all():
            deps.extend([d.depends_on_id for d in group.dependencies.all()])
        
        for dep_id in deps:
            graph[dep_id].append(task.id)
            in_degree[task.id] += 1
        
        if not deps:  # Tasks without dependencies
            task_order.append(task.id)
    
    # Initialize queue with tasks having no dependencies
    queue = deque([tid for tid in task_map if in_degree[tid] == 0])
    
    while queue:
        current_id = queue.popleft()
        current_task = task_map[current_id]
        
        # Calculate earliest possible start date based on dependencies
        dependency_start = project.start_date
        for group in current_task.dependency_groups.all():
            group_dates = []
            for dependency in group.dependencies.all():
                dep_task = dependency.depends_on
                if dep_task.id in schedule:
                    group_dates.append(schedule[dep_task.id]['end'])
            
            if group_dates:
                if group.logic_type == 'AND':
                    group_start = max(group_dates)
                else:  # OR logic
                    group_start = min(group_dates)
                
                dependency_start = max(dependency_start, group_start)
        
        # MODIFIED: Added project switching logic
        user = current_task.assigned_to
        if user:
            current_project = handle_multiple_projects(user)
            # Check if user is working on another project
            if current_project and current_project != project:
                # User is busy - can't start this task yet
                user_start = user_availability[user.id]
            else:
                # User is available for this project
                user_start = user_availability[user.id]
        else:
            # Unassigned task uses dependency start
            user_start = dependency_start

        # Calculate actual start date
        start_date = max(dependency_start, user_start)
        end_date = start_date + timedelta(days=current_task.duration_days)
        
        # Update schedule and user availability
        schedule[current_id] = {
            'start': start_date,
            'end': end_date,
            'user': user.id if user else None
        }
        
        # MODIFIED: Only update availability if working on current project
        if user and (not current_project or current_project == project):
            user_availability[user.id] = end_date + timedelta(days=1)
        
        # Update topological sort
        for neighbor in graph[current_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
                task_order.append(neighbor)

    # Handle tasks with circular dependencies (fallback)
    for task in tasks:
        if task.id not in schedule:
            start_date = user_availability.get(task.assigned_to.id, project.start_date)
            end_date = start_date + timedelta(days=task.duration_days)
            schedule[task.id] = {
                'start': start_date,
                'end': end_date,
                'user': task.assigned_to.id if task.assigned_to else None
            }

    # Update tasks with calculated dates
    for task in tasks:
        if task.id in schedule:
            task_data = schedule[task.id]
            task.start_date = task_data['start']
            task.end_date = task_data['end']
            task.save()

    return schedule