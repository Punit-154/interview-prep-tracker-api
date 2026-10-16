from django.contrib import admin
from .models import Problem, Attempt


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'topic', 'difficulty', 'created_at')
    list_filter = ('topic', 'difficulty')
    search_fields = ('title',)
    ordering = ('id',)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'problem', 'status', 'time_taken', 'date', 'updated_at')
    list_filter = ('status', 'problem__topic', 'problem__difficulty', 'date')
    search_fields = ('user__username', 'problem__title', 'notes')
    ordering = ('-date', '-updated_at')
