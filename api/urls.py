from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    TaskViewSet,
    PublicProjectViewSet,
    DependencyViewSet,
    ProjectCollaboratorViewSet,
    DependencyGroupViewSet,
    RegisterView
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'public-projects', PublicProjectViewSet, basename='publicproject')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'dependencies', DependencyViewSet, basename='dependency')
router.register(r'collaborators', ProjectCollaboratorViewSet, basename='collaborator')
router.register(r'dependency-groups', DependencyGroupViewSet, basename='dependencygroup')

urlpatterns = [
    path('', include(router.urls)),
]