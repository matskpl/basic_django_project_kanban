from django.contrib import admin
from .models import User, Profile, Team, Project, Task, Comment, Attachment

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Team)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(Attachment)
