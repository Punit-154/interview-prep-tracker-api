from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from tracker.models import Problem, Attempt


class StatsTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='stats_user_a', password='password123')
        self.user_b = User.objects.create_user(username='stats_user_b', password='password123')

        # Problems
        self.p_arr_easy = Problem.objects.create(
            title="Two Sum",
            topic=Problem.Topic.ARRAYS,
            difficulty=Problem.Difficulty.EASY
        )
        self.p_arr_med = Problem.objects.create(
            title="3Sum",
            topic=Problem.Topic.ARRAYS,
            difficulty=Problem.Difficulty.MEDIUM
        )
        self.p_tree_med = Problem.objects.create(
            title="Validate BST",
            topic=Problem.Topic.TREES,
            difficulty=Problem.Difficulty.MEDIUM
        )
        self.p_dp_hard = Problem.objects.create(
            title="Edit Distance",
            topic=Problem.Topic.DYNAMIC_PROGRAMMING,
            difficulty=Problem.Difficulty.HARD
        )

        self.stats_url = reverse('tracker:attempt-stats')

    def test_unauthenticated_user_cannot_access_stats(self):
        """Unauthenticated requests to stats endpoint return 401."""
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stats_aggregation_for_authenticated_user(self):
        """
        Stats endpoint correctly aggregates solved counts by topic, difficulty,
        and total preparation time using Django ORM annotate and Count.
        """
        # User A attempts
        Attempt.objects.create(
            user=self.user_a,
            problem=self.p_arr_easy,
            status=Attempt.Status.SOLVED,
            time_taken=20
        )
        Attempt.objects.create(
            user=self.user_a,
            problem=self.p_arr_med,
            status=Attempt.Status.SOLVED,
            time_taken=40
        )
        Attempt.objects.create(
            user=self.user_a,
            problem=self.p_tree_med,
            status=Attempt.Status.ATTEMPTED,  # Not solved
            time_taken=30
        )

        # User B attempts (Should NOT affect User A's stats)
        Attempt.objects.create(
            user=self.user_b,
            problem=self.p_dp_hard,
            status=Attempt.Status.SOLVED,
            time_taken=60
        )

        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.stats_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(data['total_problems'], 4)
        self.assertEqual(data['total_attempts'], 3)
        self.assertEqual(data['total_solved'], 2)
        self.assertEqual(data['total_time_spent_minutes'], 90)  # 20 + 40 + 30

        # Topic aggregation checks
        topics_map = {item['topic']: item['solved'] for item in data['solved_by_topic']}
        self.assertEqual(topics_map.get('arrays'), 2)
        # Tree was only 'attempted', not 'solved', so it should not appear as solved
        self.assertNotIn('trees', topics_map)
        # User B's DP solve must not appear in User A's stats
        self.assertNotIn('dynamic_programming', topics_map)

        # Difficulty aggregation checks
        diff_map = {item['difficulty']: item['solved'] for item in data['solved_by_difficulty']}
        self.assertEqual(diff_map.get('easy'), 1)
        self.assertEqual(diff_map.get('medium'), 1)
        self.assertNotIn('hard', diff_map)
