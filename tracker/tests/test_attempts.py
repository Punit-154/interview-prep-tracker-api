from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from tracker.models import Problem, Attempt


class AttemptTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='user_a', password='password123')
        self.user_b = User.objects.create_user(username='user_b', password='password123')

        self.problem_1 = Problem.objects.create(
            title="Two Sum",
            topic=Problem.Topic.ARRAYS,
            difficulty=Problem.Difficulty.EASY
        )
        self.problem_2 = Problem.objects.create(
            title="LRU Cache",
            topic=Problem.Topic.LINKED_LIST,
            difficulty=Problem.Difficulty.MEDIUM
        )

        self.list_url = reverse('tracker:attempt-list')

    def test_unauthenticated_user_cannot_access_attempts(self):
        """Unauthenticated requests are rejected with 401 Unauthorized."""
        res_get = self.client.get(self.list_url)
        self.assertEqual(res_get.status_code, status.HTTP_401_UNAUTHORIZED)

        res_post = self.client.post(self.list_url, {
            'problem': self.problem_1.id,
            'status': Attempt.Status.SOLVED,
            'time_taken': 20
        })
        self.assertEqual(res_post.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_attempt(self):
        """Authenticated user can track an attempt, and owner is auto-assigned."""
        self.client.force_authenticate(user=self.user_a)
        payload = {
            'problem': self.problem_1.id,
            'status': Attempt.Status.SOLVED,
            'time_taken': 25,
            'notes': 'Used hash map for O(n) time and O(n) space.'
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], Attempt.Status.SOLVED)
        self.assertEqual(response.data['time_taken'], 25)
        self.assertEqual(response.data['username'], 'user_a')
        self.assertIn('problem_detail', response.data)
        self.assertEqual(response.data['problem_detail']['title'], "Two Sum")

        # Verify database record
        attempt = Attempt.objects.get(id=response.data['id'])
        self.assertEqual(attempt.user, self.user_a)

    def test_unique_constraint_per_user_and_problem(self):
        """User cannot create two separate attempts for the same problem."""
        self.client.force_authenticate(user=self.user_a)
        Attempt.objects.create(
            user=self.user_a,
            problem=self.problem_1,
            status=Attempt.Status.ATTEMPTED,
            time_taken=15
        )

        # Attempt to create duplicate for problem_1
        payload = {
            'problem': self.problem_1.id,
            'status': Attempt.Status.SOLVED,
            'time_taken': 30
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('problem', response.data)

    def test_user_a_cannot_read_user_b_attempts(self):
        """
        Critical Owner Isolation:
        User A cannot see User B's attempts in list and receives 404 when querying User B's attempt ID directly.
        """
        # User B creates an attempt
        attempt_b = Attempt.objects.create(
            user=self.user_b,
            problem=self.problem_1,
            status=Attempt.Status.SOLVED,
            time_taken=45,
            notes="User B's secret notes"
        )

        # Authenticate as User A
        self.client.force_authenticate(user=self.user_a)

        # 1. User A lists attempts -> Should be empty
        list_res = self.client.get(self.list_url)
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(list_res.data['count'], 0)
        self.assertEqual(len(list_res.data['results']), 0)

        # 2. User A tries to GET User B's attempt directly by ID -> 404 Not Found
        detail_url = reverse('tracker:attempt-detail', args=[attempt_b.id])
        detail_res = self.client.get(detail_url)
        self.assertEqual(detail_res.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_a_cannot_edit_or_delete_user_b_attempts(self):
        """User A cannot modify or delete User B's attempt (receives 404)."""
        attempt_b = Attempt.objects.create(
            user=self.user_b,
            problem=self.problem_1,
            status=Attempt.Status.ATTEMPTED,
            time_taken=10
        )
        detail_url = reverse('tracker:attempt-detail', args=[attempt_b.id])

        # Authenticate as User A
        self.client.force_authenticate(user=self.user_a)

        # PUT
        put_res = self.client.put(detail_url, {
            'problem': self.problem_1.id,
            'status': Attempt.Status.SOLVED,
            'time_taken': 99
        })
        self.assertEqual(put_res.status_code, status.HTTP_404_NOT_FOUND)

        # PATCH
        patch_res = self.client.patch(detail_url, {'time_taken': 99})
        self.assertEqual(patch_res.status_code, status.HTTP_404_NOT_FOUND)

        # DELETE
        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_404_NOT_FOUND)

        # Verify attempt still belongs unchanged to User B in DB
        attempt_b.refresh_from_db()
        self.assertEqual(attempt_b.time_taken, 10)

    def test_user_can_update_and_delete_own_attempt(self):
        """User can successfully update and delete their own attempt."""
        self.client.force_authenticate(user=self.user_a)
        attempt_a = Attempt.objects.create(
            user=self.user_a,
            problem=self.problem_1,
            status=Attempt.Status.ATTEMPTED,
            time_taken=15,
            notes='Initial attempt'
        )
        detail_url = reverse('tracker:attempt-detail', args=[attempt_a.id])

        # PATCH update
        patch_res = self.client.patch(detail_url, {
            'status': Attempt.Status.SOLVED,
            'time_taken': 20,
            'notes': 'Optimal solution found'
        })
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data['status'], Attempt.Status.SOLVED)
        self.assertEqual(patch_res.data['time_taken'], 20)
        self.assertEqual(patch_res.data['notes'], 'Optimal solution found')

        # DELETE
        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Attempt.objects.filter(id=attempt_a.id).exists())
