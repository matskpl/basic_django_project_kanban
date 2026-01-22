from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Team, Project, Task
from .forms import TeamForm

class TeamAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        self.team = Team.objects.create(
            name='Team A',
            owner=self.user1
        )
    
    def test_user_cannot_access_other_team(self):
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('team_detail', kwargs={'pk': self.team.pk}))
        self.assertEqual(response.status_code, 404)
    
    def test_user_can_access_own_team(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('team_detail', kwargs={'pk': self.team.pk}))
        self.assertEqual(response.status_code, 200)

class ProjectAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        self.team = Team.objects.create(name='Team A', owner=self.user1)
        
        self.project = Project.objects.create(
            name='Project 1',
            team=self.team
        )
    
    def test_user_cannot_access_other_team_project(self):
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('project_detail', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 404)
    def test_user_can_access_own_team_project(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('project_detail', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 200)

class TaskAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        self.team = Team.objects.create(name='Team A', owner=self.user1)
        
        self.project = Project.objects.create(name='Project 1', team=self.team)
        
        self.task = Task.objects.create(
            title='Task 1',
            project=self.project,
            created_by=self.user1,
            status='todo'
        )
    
    def test_user_cannot_access_other_team_task(self):
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('task_detail', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 404)
    
    def test_user_cannot_edit_other_team_task(self):
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('task_edit', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 404)

class TeamFormValidationTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        self.team = Team.objects.create(name='Team A', owner=self.user1)
        self.team.members.add(self.user2)
    
    def test_cannot_add_existing_member(self):
        form = TeamForm(data={'name': 'Team A', 'add_member': 'user2'}, instance=self.team)
        self.assertFalse(form.is_valid())
        self.assertIn('add_member', form.errors)
        self.assertIn('już jest w zespole', str(form.errors['add_member']))
    
    def test_cannot_add_nonexistent_user(self):
        form = TeamForm(data={'name': 'Team A', 'add_member': 'nonexistent'}, instance=self.team)
        self.assertFalse(form.is_valid())
        self.assertIn('add_member', form.errors)
        self.assertIn('nie istnieje', str(form.errors['add_member']))