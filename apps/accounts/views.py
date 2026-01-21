from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count, Prefetch
from django.http import Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, FormView
from django.urls import reverse_lazy, reverse
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Profile, Team, Project, Task, Comment, Attachment
from .serializers import ProjectSerializer, TaskSerializer
from .forms import (
    RegistrationForm, ProfileForm, TeamForm, ProjectForm, 
    TaskForm, CommentForm, AttachmentForm
)

class TeamMemberRequiredMixin(LoginRequiredMixin):
    team_url_kwarg = 'team_id'

    def dispatch(self, request, *args, **kwargs):
        self.team = get_object_or_404(Team, pk=kwargs[self.team_url_kwarg])
        if request.user not in self.team.members.all():
            raise Http404("Nie masz dostępu do tego zespołu")
        return super().dispatch(request, *args, **kwargs)


class ProjectMemberRequiredMixin(LoginRequiredMixin):
    project_url_kwarg = 'project_id'

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=kwargs[self.project_url_kwarg])
        if request.user not in self.project.team.members.all():
            raise Http404("Nie masz dostępu do tego projektu")
        return super().dispatch(request, *args, **kwargs)


class TeamObjectAccessMixin(LoginRequiredMixin):
    def get_object(self, queryset=None):
        team = super().get_object(queryset)
        if self.request.user not in team.members.all():
            raise Http404("Nie masz dostępu do tego zespołu")
        return team


class ProjectObjectAccessMixin(LoginRequiredMixin):
    def get_object(self, queryset=None):
        project = super().get_object(queryset)
        if self.request.user not in project.team.members.all():
            raise Http404("Nie masz dostępu do tego projektu")
        return project


class TaskObjectAccessMixin(LoginRequiredMixin):
    def get_object(self, queryset=None):
        task = super().get_object(queryset)
        if self.request.user not in task.project.team.members.all():
            raise Http404("Nie masz dostępu do tego zadania")
        return task

class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        user = form.save()
        Profile.objects.create(user=user)
        login(self.request, user)
        messages.success(self.request, 'Witaj! Twoje konto zostało utworzone. Zacznij od stworzenia zespołu.')
        return redirect('dashboard')

class ProfileView(LoginRequiredMixin, FormView):
    template_name = 'accounts/profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('profile')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        kwargs['user'] = self.request.user
        kwargs['instance'] = profile
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'], _ = Profile.objects.get_or_create(user=self.request.user)
        return context
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Profil został zaktualizowany!')
        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = Team.objects.filter(members=self.request.user).select_related('owner').prefetch_related('members')
        context['urgent_tasks'] = Task.objects.filter(
            assigned_to=self.request.user,
            status__in=['todo', 'in_progress']
        ).select_related('project__team', 'created_by').order_by('due_date')[:10]
        return context

class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'accounts/team_list.html'
    context_object_name = 'teams'
    
    def get_queryset(self):
        return Team.objects.filter(members=self.request.user).select_related('owner').annotate(
            member_count=Count('members', distinct=True),
            project_count=Count('projects', distinct=True)
        )

class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = 'accounts/team_form.html'
    
    def form_valid(self, form):
        team = form.save(commit=False)
        team.owner = self.request.user
        team.save()
        
        member_to_add = form.cleaned_data.get('add_member')
        if member_to_add:
            team.members.add(member_to_add)
        
        messages.success(self.request, 'Zespół został utworzony!')
        return redirect('team_detail', pk=team.pk)

class TeamDetailView(TeamObjectAccessMixin, DetailView):
    model = Team
    template_name = 'accounts/team_detail.html'
    context_object_name = 'team'
    
    def get_queryset(self):
        return Team.objects.prefetch_related('members', 'projects')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.get_object()
        context['projects'] = team.projects.all()
        if self.request.user == team.owner and 'form' not in context:
            context['form'] = TeamForm(instance=team)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        team = self.object
        if request.user == team.owner:
            form = TeamForm(request.POST, instance=team)
            if form.is_valid():
                form.save()
                member_to_add = form.cleaned_data.get('add_member')
                if member_to_add:
                    team.members.add(member_to_add)
                    messages.success(request, 'Członek został dodany!')
                return redirect('team_detail', pk=team.pk)
            context = self.get_context_data(form=form)
            return self.render_to_response(context)
        return self.get(request, *args, **kwargs)

class ProjectCreateView(TeamMemberRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'accounts/project_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.team
        return context
    
    def form_valid(self, form):
        project = form.save(commit=False)
        project.team = self.team
        project.save()
        messages.success(self.request, 'Projekt został utworzony!')
        return redirect('project_detail', pk=project.pk)

class ProjectDetailView(ProjectObjectAccessMixin, DetailView):
    model = Project
    template_name = 'accounts/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        return Project.objects.select_related('team__owner').prefetch_related(
            Prefetch('tasks', queryset=Task.objects.select_related('assigned_to', 'created_by'))
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks_by_status'] = {
            'todo': self.object.tasks.filter(status='todo'),
            'in_progress': self.object.tasks.filter(status='in_progress'),
            'done': self.object.tasks.filter(status='done'),
        }
        return context

class TaskCreateView(ProjectMemberRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'accounts/task_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.project
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context
    
    def form_valid(self, form):
        task = form.save(commit=False)
        task.project = self.project
        task.created_by = self.request.user
        task.save()
        messages.success(self.request, 'Zadanie zostało utworzone!')
        return redirect('task_detail', pk=task.pk)

class TaskDetailView(TaskObjectAccessMixin, DetailView):
    model = Task
    template_name = 'accounts/task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.select_related(
            'project__team', 'assigned_to', 'created_by'
        ).prefetch_related(
            Prefetch('comments', queryset=Comment.objects.select_related('author__profile')),
            Prefetch('attachments', queryset=Attachment.objects.select_related('uploaded_by'))
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['attachment_form'] = AttachmentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        task = self.get_object()
        
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.task = task
                comment.author = request.user
                comment.save()
                messages.success(request, 'Komentarz dodany!')
                return redirect('task_detail', pk=task.pk)
        
        elif 'attachment_submit' in request.POST:
            attachment_form = AttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.task = task
                attachment.uploaded_by = request.user
                attachment.save()
                messages.success(request, 'Załącznik dodany!')
                return redirect('task_detail', pk=task.pk)
        
        return self.get(request, *args, **kwargs)

class TaskUpdateView(TaskObjectAccessMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'accounts/task_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.object.project
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = self.object
        context['project'] = self.object.project
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Zadanie zostało zaktualizowane!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('task_detail', kwargs={'pk': self.object.pk})

class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(
            team__members=self.request.user
        ).select_related('team')
    
    @extend_schema(
        responses={200: {
            'type': 'object',
            'properties': {
                'total_tasks': {'type': 'integer'},
                'completed_tasks': {'type': 'integer'},
                'completion_rate': {'type': 'number', 'format': 'float'}
            }
        }},
        description='Get project statistics including total tasks, completed tasks and completion rate'
    )
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        project = self.get_object()
        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter(status='done').count()
        
        return Response({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        })

@extend_schema(
    parameters=[
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter tasks by status (todo, in_progress, done)',
            required=False,
            enum=['todo', 'in_progress', 'done']
        )
    ],
    responses={200: TaskSerializer(many=True)},
    description='Get all tasks assigned to the authenticated user with optional status filter'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_tasks(request):
    status_filter = request.query_params.get('status')
    
    tasks = Task.objects.filter(assigned_to=request.user).select_related('project', 'created_by')
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)
