from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import models
from .models import Project, Task, Dependency, ProjectCollaborator, DependencyGroup
from .serializers import (
    ProjectSerializer, TaskSerializer, 
    DependencySerializer, ProjectCollaboratorSerializer,
    DependencyGroupSerializer, UserSerializer
)
from .scheduling import calculate_project_schedule

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Project.objects.filter(
                models.Q(is_public=True) |
                models.Q(creator=user) |
                models.Q(collaborators__user=user)
            ).distinct()
        return Project.objects.filter(is_public=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        project = self.get_object()
        schedule = calculate_project_schedule(project)
        
        # Get all tasks in one query
        tasks = {t.id: t for t in Task.objects.filter(id__in=schedule.keys())}
        
        return Response({
            str(task_id): {
                'title': tasks[task_id].title,
                'start': dates['start'].isoformat(),
                'end': dates['end'].isoformat(),
                'assigned_to': tasks[task_id].assigned_to.username if tasks[task_id].assigned_to else None
            } for task_id, dates in schedule.items()
        })

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(
                models.Q(is_private=False) |
                models.Q(creator=user) |
                models.Q(assigned_to=user) |
                models.Q(project__collaborators__user=user)
            ).distinct()
        return Task.objects.filter(project__is_public=True, is_private=False)

class DependencyViewSet(viewsets.ModelViewSet):
    serializer_class = DependencySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Dependency.objects.all()

class ProjectCollaboratorViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectCollaboratorSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ProjectCollaborator.objects.all()

class DependencyGroupViewSet(viewsets.ModelViewSet):
    serializer_class = DependencyGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DependencyGroup.objects.all()

class PublicProjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Project.objects.filter(is_public=True)