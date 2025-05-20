from rest_framework import serializers
from django.utils import timezone
from .models import Project, Task, Dependency, ProjectCollaborator, DependencyGroup
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    is_public = serializers.BooleanField(
        source='is_private', 
        read_only=True,
        help_text="Public status (inverse of is_private)"
    )
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 
            'parent_task', 'duration_days', 'is_public',
            'assigned_to', 'is_completed', 'status',
            'start_date', 'end_date', 'is_private'
        ]
        extra_kwargs = {
            'duration_days': {'min_value': 1},
            'project': {'required': True},
            'is_private': {'write_only': True}
        }

    # New Validation: Prevent Overloading Users
    def validate_assigned_to(self, value):
        if value:
            pending_tasks = value.assigned_tasks.filter(
                is_completed=False,
                end_date__gte=timezone.now().date()
            )
            if pending_tasks.exists():
                raise serializers.ValidationError("User has pending tasks")
        return value

    def validate(self, data):
        instance = self.instance
        if instance and data.get('is_completed', False):
            if instance.subtasks.filter(is_completed=False).exists():
                raise serializers.ValidationError("All subtasks must be completed first")
            
            if not instance.can_start():
                raise serializers.ValidationError("Dependencies not met")
        return data

class ProjectSerializer(serializers.ModelSerializer):
    is_public = serializers.BooleanField(default=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'creator',
            'start_date', 'is_public', 'tasks', 'collaborators'
        ]
        read_only_fields = ['creator', 'tasks', 'collaborators', 'start_date']

    def create(self, validated_data):
        # Automatically set the creator to the current user
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class DependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependency
        fields = '__all__'

class DependencyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DependencyGroup
        fields = '__all__'

class ProjectCollaboratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCollaborator
        fields = '__all__'