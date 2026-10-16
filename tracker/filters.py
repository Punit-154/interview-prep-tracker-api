import django_filters
from .models import Problem, Attempt


class ProblemFilter(django_filters.FilterSet):
    """
    Filter set for Problem queries supporting case-insensitive topic and difficulty matching.
    Usage: ?topic=arrays&difficulty=easy
    """
    topic = django_filters.CharFilter(field_name='topic', lookup_expr='iexact')
    difficulty = django_filters.CharFilter(field_name='difficulty', lookup_expr='iexact')

    class Meta:
        model = Problem
        fields = ['topic', 'difficulty']


class AttemptFilter(django_filters.FilterSet):
    """
    Filter set for candidate attempts supporting status, problem topic, difficulty, and date ranges.
    """
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    topic = django_filters.CharFilter(field_name='problem__topic', lookup_expr='iexact')
    difficulty = django_filters.CharFilter(field_name='problem__difficulty', lookup_expr='iexact')
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Attempt
        fields = ['status', 'topic', 'difficulty', 'date_from', 'date_to']
