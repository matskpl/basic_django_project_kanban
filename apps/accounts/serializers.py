from rest_framework import serializers
from .models import Project, Task

class ProjectSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField(source='team.id', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    task_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'team_id', 'team_name', 'task_count']

class TaskSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(source='project.id', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_to_id = serializers.IntegerField(source='assigned_to.id', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status', 'due_date',
            'project_id', 'project_name', 'assigned_to_id', 'assigned_to_username',
            'created_at', 'updated_at'
        ]