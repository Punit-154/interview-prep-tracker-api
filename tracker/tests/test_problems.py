from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tracker.models import Problem


class ProblemTests(APITestCase):
    def setUp(self):
        self.list_url = reverse('tracker:problem-list')
        self.p1 = Problem.objects.create(
            title="Two Sum",
            topic=Problem.Topic.ARRAYS,
            difficulty=Problem.Difficulty.EASY,
            link="https://leetcode.com/problems/two-sum/"
        )
        self.p2 = Problem.objects.create(
            title="3Sum",
            topic=Problem.Topic.ARRAYS,
            difficulty=Problem.Difficulty.MEDIUM,
            link="https://leetcode.com/problems/3sum/"
        )
        self.p3 = Problem.objects.create(
            title="Reverse Linked List",
            topic=Problem.Topic.LINKED_LIST,
            difficulty=Problem.Difficulty.EASY,
            link="https://leetcode.com/problems/reverse-linked-list/"
        )

    def test_list_problems_pagination(self):
        """Problems list endpoint returns paginated results."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 3)

    def test_retrieve_problem_detail(self):
        """Retrieve single problem detail by ID."""
        detail_url = reverse('tracker:problem-detail', args=[self.p1.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Two Sum")
        self.assertEqual(response.data['topic'], "arrays")
        self.assertEqual(response.data['difficulty'], "easy")

    def test_problems_endpoint_is_read_only(self):
        """Problems endpoint disallows POST, PUT, DELETE (405 Method Not Allowed)."""
        # POST
        post_res = self.client.post(self.list_url, {"title": "New Problem"})
        self.assertEqual(post_res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # PUT
        detail_url = reverse('tracker:problem-detail', args=[self.p1.id])
        put_res = self.client.put(detail_url, {"title": "Modified Title"})
        self.assertEqual(put_res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # DELETE
        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_filter_problems_by_topic_and_difficulty(self):
        """Filter problems by topic and difficulty query parameters."""
        # Filter arrays
        res_topic = self.client.get(f"{self.list_url}?topic=arrays")
        self.assertEqual(res_topic.status_code, status.HTTP_200_OK)
        self.assertEqual(res_topic.data['count'], 2)

        # Filter arrays + easy
        res_both = self.client.get(f"{self.list_url}?topic=arrays&difficulty=easy")
        self.assertEqual(res_both.status_code, status.HTTP_200_OK)
        self.assertEqual(res_both.data['count'], 1)
        self.assertEqual(res_both.data['results'][0]['title'], "Two Sum")

    def test_search_problems_by_title(self):
        """Search problems by keyword in title."""
        res_search = self.client.get(f"{self.list_url}?search=Reverse")
        self.assertEqual(res_search.status_code, status.HTTP_200_OK)
        self.assertEqual(res_search.data['count'], 1)
        self.assertEqual(res_search.data['results'][0]['title'], "Reverse Linked List")
