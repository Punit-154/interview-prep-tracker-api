from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Problem(models.Model):
    """
    Represents a coding interview problem categorized by topic and difficulty.
    """
    class Topic(models.TextChoices):
        ARRAYS = 'arrays', 'Arrays'
        STRINGS = 'strings', 'Strings'
        LINKED_LIST = 'linked_list', 'Linked List'
        TREES = 'trees', 'Trees & BST'
        GRAPHS = 'graphs', 'Graphs'
        DYNAMIC_PROGRAMMING = 'dynamic_programming', 'Dynamic Programming'
        SORTING_SEARCHING = 'sorting_searching', 'Sorting & Searching'
        STACK_QUEUE = 'stack_queue', 'Stack & Queue'
        RECURSION_BACKTRACKING = 'recursion_backtracking', 'Recursion & Backtracking'
        OTHER = 'other', 'Other'

    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'

    title = models.CharField(max_length=255, db_index=True)
    topic = models.CharField(
        max_length=50,
        choices=Topic.choices,
        default=Topic.ARRAYS,
        db_index=True
    )
    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM,
        db_index=True
    )
    link = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Problem'
        verbose_name_plural = 'Problems'

    def __str__(self):
        return f"{self.title} [{self.get_difficulty_display()} - {self.get_topic_display()}]"


class Attempt(models.Model):
    """
    Tracks a user's practice attempt, performance, notes, and solve status for a problem.
    Enforces that a user has one primary progress record per problem via UniqueConstraint.
    """
    class Status(models.TextChoices):
        SOLVED = 'solved', 'Solved'
        ATTEMPTED = 'attempted', 'Attempted'
        FAILED = 'failed', 'Failed'
        REVIEWING = 'reviewing', 'Needs Review'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attempts',
        db_index=True
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='attempts',
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ATTEMPTED,
        db_index=True
    )
    time_taken = models.PositiveIntegerField(
        help_text="Time taken to solve or attempt the problem in minutes",
        default=0
    )
    notes = models.TextField(
        blank=True,
        default='',
        help_text="Personal notes, approach, time/space complexity, or pitfalls"
    )
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'problem'],
                name='unique_user_problem_attempt'
            )
        ]
        verbose_name = 'Attempt'
        verbose_name_plural = 'Attempts'

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} ({self.status})"
