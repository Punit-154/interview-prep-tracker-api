from rest_framework import serializers
from .models import Problem, Attempt


class ProblemSerializer(serializers.ModelSerializer):
    """
    Serializer for interview problems.
    """
    topic_display = serializers.CharField(source='get_topic_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)

    class Meta:
        model = Problem
        fields = (
            'id',
            'title',
            'topic',
            'topic_display',
            'difficulty',
            'difficulty_display',
            'link',
            'created_at',
        )
        read_only_fields = ('id', 'created_at')


class AttemptSerializer(serializers.ModelSerializer):
    """
    Serializer for candidate practice attempts.
    Handles problem association, owner representation, and readable nested details.
    """
    problem_detail = ProblemSerializer(source='problem', read_only=True)
    username = serializers.ReadOnlyField(source='user.username')
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Attempt
        fields = (
            'id',
            'user',
            'username',
            'problem',
            'problem_detail',
            'status',
            'status_display',
            'time_taken',
            'notes',
            'date',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'user', 'username', 'created_at', 'updated_at')

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        problem = attrs.get('problem')

        # Only validate unique constraint on creation (when self.instance is None)
        if self.instance is None and user and user.is_authenticated and problem:
            if Attempt.objects.filter(user=user, problem=problem).exists():
                raise serializers.ValidationError({
                    'problem': 'You have already recorded an attempt for this problem. Please update your existing attempt.'
                })
        return attrs


class TopicStatItemSerializer(serializers.Serializer):
    topic = serializers.CharField()
    solved = serializers.IntegerField()


class DifficultyStatItemSerializer(serializers.Serializer):
    difficulty = serializers.CharField()
    solved = serializers.IntegerField()


class StatsResponseSerializer(serializers.Serializer):
    total_problems = serializers.IntegerField()
    total_attempts = serializers.IntegerField()
    total_solved = serializers.IntegerField()
    total_time_spent_minutes = serializers.IntegerField()
    solved_by_topic = TopicStatItemSerializer(many=True)
    solved_by_difficulty = DifficultyStatItemSerializer(many=True)
