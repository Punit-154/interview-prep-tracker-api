from django.core.management.base import BaseCommand
from tracker.models import Problem


SAMPLE_PROBLEMS = [
    # Arrays
    {
        "title": "Two Sum",
        "topic": Problem.Topic.ARRAYS,
        "difficulty": Problem.Difficulty.EASY,
        "link": "https://leetcode.com/problems/two-sum/",
    },
    {
        "title": "Best Time to Buy and Sell Stock",
        "topic": Problem.Topic.ARRAYS,
        "difficulty": Problem.Difficulty.EASY,
        "link": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/",
    },
    {
        "title": "3Sum",
        "topic": Problem.Topic.ARRAYS,
        "difficulty": Problem.Difficulty.MEDIUM,
        "link": "https://leetcode.com/problems/3sum/",
    },
    {
        "title": "Trapping Rain Water",
        "topic": Problem.Topic.ARRAYS,
        "difficulty": Problem.Difficulty.HARD,
        "link": "https://leetcode.com/problems/trapping-rain-water/",
    },
    # Strings
    {
        "title": "Valid Anagram",
        "topic": Problem.Topic.STRINGS,
        "difficulty": Problem.Difficulty.EASY,
        "link": "https://leetcode.com/problems/valid-anagram/",
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "topic": Problem.Topic.STRINGS,
        "difficulty": Problem.Difficulty.MEDIUM,
        "link": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
    },
    {
        "title": "Minimum Window Substring",
        "topic": Problem.Topic.STRINGS,
        "difficulty": Problem.Difficulty.HARD,
        "link": "https://leetcode.com/problems/minimum-window-substring/",
    },
    # Linked List
    {
        "title": "Reverse Linked List",
        "topic": Problem.Topic.LINKED_LIST,
        "difficulty": Problem.Difficulty.EASY,
        "link": "https://leetcode.com/problems/reverse-linked-list/",
    },
    {
        "title": "Merge Two Sorted Lists",
        "topic": Problem.Topic.LINKED_LIST,
        "difficulty": Problem.Difficulty.EASY,
        "link": "https://leetcode.com/problems/merge-two-sorted-lists/",
    },
    {
        "title": "LRU Cache",
        "topic": Problem.Topic.LINKED_LIST,
        "difficulty": Problem.Difficulty.MEDIUM,
        "link": "https://leetcode.com/problems/lru-cache/",
    },
    # Trees
    {
        "title": "Maximum Depth of Binary Tree",
        "topic": Problem.Topic.TREES,
        "difficulty": Problem.Difficulty.EASY,
        "link": "https://leetcode.com/problems/maximum-depth-of-binary-tree/",
    },
    {
        "title": "Invert Binary Tree",
        "topic": Problem.Topic.TREES,
        "difficulty": Problem.Difficulty.EASY,
        "link": "https://leetcode.com/problems/invert-binary-tree/",
    },
    {
        "title": "Validate Binary Search Tree",
        "topic": Problem.Topic.TREES,
        "difficulty": Problem.Difficulty.MEDIUM,
        "link": "https://leetcode.com/problems/validate-binary-search-tree/",
    },
    {
        "title": "Binary Tree Maximum Path Sum",
        "topic": Problem.Topic.TREES,
        "difficulty": Problem.Difficulty.HARD,
        "link": "https://leetcode.com/problems/binary-tree-maximum-path-sum/",
    },
    # Graphs
    {
        "title": "Number of Islands",
        "topic": Problem.Topic.GRAPHS,
        "difficulty": Problem.Difficulty.MEDIUM,
        "link": "https://leetcode.com/problems/number-of-islands/",
    },
    {
        "title": "Clone Graph",
        "topic": Problem.Topic.GRAPHS,
        "difficulty": Problem.Difficulty.MEDIUM,
        "link": "https://leetcode.com/problems/clone-graph/",
    },
    {
        "title": "Course Schedule",
        "topic": Problem.Topic.GRAPHS,
        "difficulty": Problem.Difficulty.MEDIUM,
        "link": "https://leetcode.com/problems/course-schedule/",
    },
    {
        "title": "Word Ladder",
        "topic": Problem.Topic.GRAPHS,
        "difficulty": Problem.Difficulty.HARD,
        "link": "https://leetcode.com/problems/word-ladder/",
    },
    # Dynamic Programming
    {
        "title": "Climbing Stairs",
        "topic": Problem.Topic.DYNAMIC_PROGRAMMING,
        "difficulty": Problem.Difficulty.EASY,
        "link": "https://leetcode.com/problems/climbing-stairs/",
    },
    {
        "title": "Coin Change",
        "topic": Problem.Topic.DYNAMIC_PROGRAMMING,
        "difficulty": Problem.Difficulty.MEDIUM,
        "link": "https://leetcode.com/problems/coin-change/",
    },
    {
        "title": "Longest Increasing Subsequence",
        "topic": Problem.Topic.DYNAMIC_PROGRAMMING,
        "difficulty": Problem.Difficulty.MEDIUM,
        "link": "https://leetcode.com/problems/longest-increasing-subsequence/",
    },
    {
        "title": "Edit Distance",
        "topic": Problem.Topic.DYNAMIC_PROGRAMMING,
        "difficulty": Problem.Difficulty.HARD,
        "link": "https://leetcode.com/problems/edit-distance/",
    },
    # Sorting & Searching
    {
        "title": "Binary Search",
        "topic": Problem.Topic.SORTING_SEARCHING,
        "difficulty": Problem.Difficulty.EASY,
        "link": "https://leetcode.com/problems/binary-search/",
    },
    {
        "title": "Search in Rotated Sorted Array",
        "topic": Problem.Topic.SORTING_SEARCHING,
        "difficulty": Problem.Difficulty.MEDIUM,
        "link": "https://leetcode.com/problems/search-in-rotated-sorted-array/",
    },
    # Stack & Queue
    {
        "title": "Valid Parentheses",
        "topic": Problem.Topic.STACK_QUEUE,
        "difficulty": Problem.Difficulty.EASY,
        "link": "https://leetcode.com/problems/valid-parentheses/",
    },
]


class Command(BaseCommand):
    help = "Seeds 25 common coding interview problems for testing and demo."

    def handle(self, *args, **options):
        created_count = 0
        existing_count = 0

        for item in SAMPLE_PROBLEMS:
            obj, created = Problem.objects.get_or_create(
                title=item["title"],
                defaults={
                    "topic": item["topic"],
                    "difficulty": item["difficulty"],
                    "link": item["link"],
                }
            )
            if created:
                created_count += 1
            else:
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Seeded {created_count} new problems ({existing_count} already existed). Total: {Problem.objects.count()} problems."
            )
        )
