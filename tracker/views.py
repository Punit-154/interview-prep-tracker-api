from django.db.models import Count, Sum
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Problem, Attempt
from .serializers import (
    ProblemSerializer,
    AttemptSerializer,
    StatsResponseSerializer
)
from .permissions import IsOwner
from .filters import ProblemFilter, AttemptFilter


class ProblemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint for browsing coding interview problems.
    Supports filtering by topic and difficulty, searching by title, and pagination.
    """
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = (permissions.AllowAny,)
    filterset_class = ProblemFilter
    search_fields = ('title',)
    ordering_fields = ('id', 'title', 'difficulty', 'created_at')
    ordering = ('id',)

    @extend_schema(
        summary="List problems",
        description="Retrieve a paginated list of interview problems with optional filtering and search."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a problem",
        description="Retrieve details for a single interview problem by ID."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class AttemptViewSet(viewsets.ModelViewSet):
    """
    Full CRUD ViewSet for user practice attempts.
    Guarantees row-level isolation: users can strictly view, create, edit, and delete their own attempts.
    """
    serializer_class = AttemptSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    filterset_class = AttemptFilter
    search_fields = ('problem__title', 'notes')
    ordering_fields = ('date', 'time_taken', 'created_at', 'updated_at')
    ordering = ('-date', '-updated_at')

    def get_queryset(self):
        """
        Enforce Row-Level Security: Only return attempts belonging to the authenticated user.
        Uses select_related to prevent N+1 query overhead for related problems and users.
        """
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Attempt.objects.none()
        return Attempt.objects.filter(user=self.request.user).select_related('problem', 'user')

    def perform_create(self, serializer):
        """
        Associate the newly created attempt with the authenticated user.
        """
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="User Preparation Statistics",
        description=(
            "Aggregates total problems solved, breakdown by topic using Django ORM annotate + Count, "
            "breakdown by difficulty, and total practice time spent."
        ),
        responses={200: StatsResponseSerializer}
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def stats(self, request):
        """
        Calculates prep metrics for the authenticated user using ORM aggregation and annotation.
        """
        user_attempts = Attempt.objects.filter(user=request.user)
        solved_attempts = user_attempts.filter(status=Attempt.Status.SOLVED)

        # 1. Solved count per topic using annotate & Count
        topic_counts_qs = (
            solved_attempts
            .values('problem__topic')
            .annotate(solved=Count('id'))
            .order_by('-solved')
        )
        solved_by_topic = [
            {'topic': item['problem__topic'], 'solved': item['solved']}
            for item in topic_counts_qs
        ]

        # 2. Solved count per difficulty using annotate & Count
        difficulty_counts_qs = (
            solved_attempts
            .values('problem__difficulty')
            .annotate(solved=Count('id'))
            .order_by('-solved')
        )
        solved_by_difficulty = [
            {'difficulty': item['problem__difficulty'], 'solved': item['solved']}
            for item in difficulty_counts_qs
        ]

        # 3. Aggregated metrics (total time spent and total attempts)
        total_time_spent = user_attempts.aggregate(total_time=Sum('time_taken'))['total_time'] or 0
        total_problems_in_db = Problem.objects.count()
        total_solved = solved_attempts.count()

        payload = {
            'total_problems': total_problems_in_db,
            'total_attempts': user_attempts.count(),
            'total_solved': total_solved,
            'total_time_spent_minutes': total_time_spent,
            'solved_by_topic': solved_by_topic,
            'solved_by_difficulty': solved_by_difficulty,
        }
        return Response(payload, status=status.HTTP_200_OK)
