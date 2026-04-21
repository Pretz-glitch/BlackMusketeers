import streamlit as st
import pandas as pd

st.set_page_config(page_title="DSA Concepts", layout="wide")

st.title("Data Structures and Algorithms (DSA)")

st.header("High-Level Overview")
st.write("This page serves as a reference for core DSA concepts and strategies.")

overview_data = {
    "Concept": [
        "Arrays & Strings",
        "Two Pointers",
        "Sliding Window",
        "Binary Search",
        "Linked Lists",
        "Trees & Graphs",
        "Dynamic Programming"
    ],
    "Description": [
        "Contiguous memory allocation. Used for constant time access.",
        "Iterating with two pointers from different ends or at different speeds.",
        "Maintaining a subset of elements to optimize nested loops over arrays/strings.",
        "Searching a sorted array in O(log n) time.",
        "Nodes pointing to one another. Dynamic memory allocation.",
        "Hierarchical or networked node structures (DFS, BFS).",
        "Solving complex problems by breaking them down into simpler subproblems."
    ],
    "Common Patterns": [
        "Prefix sum, Hash Map tallying",
        "Opposites, slow/fast (Tortoise & Hare)",
        "Fixed-size, Variable-size windows",
        "Search space reduction, monotonic functions",
        "Reverse, Cycle detection",
        "Level order, Post-order, Topological sort",
        "Memoization, Tabulation, Knapsack"
    ]
}

st.table(pd.DataFrame(overview_data))

st.divider()

st.header("Detailed Mapping for Selected Problems")

problem_tabs = st.tabs([
    "Two Sum (Array)", 
    "Valid Palindrome (Two Pointers)", 
    "Maximum Subarray (Sliding Window/Kadane)",
    "Climbing Stairs (DP)"
])

with problem_tabs[0]:
    st.subheader("Two Sum")
    st.markdown("**Category:** Arrays / Hash Map")
    st.markdown("**Time Complexity:** $O(N)$ | **Space Complexity:** $O(N)$")
    st.write("Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.")
    st.code('''def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []''', language='python')

with problem_tabs[1]:
    st.subheader("Valid Palindrome")
    st.markdown("**Category:** Two Pointers")
    st.markdown("**Time Complexity:** $O(N)$ | **Space Complexity:** $O(1)$")
    st.write("A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward.")
    st.code('''def isPalindrome(s):
    l, r = 0, len(s) - 1
    while l < r:
        while l < r and not s[l].isalnum(): l += 1
        while l < r and not s[r].isalnum(): r -= 1
        if s[l].lower() != s[r].lower():
            return False
        l += 1; r -= 1
    return True''', language='python')

with problem_tabs[2]:
    st.subheader("Maximum Subarray")
    st.markdown("**Category:** DP / Kadane's Algorithm")
    st.markdown("**Time Complexity:** $O(N)$ | **Space Complexity:** $O(1)$")
    st.write("Given an integer array `nums`, find the subarray with the largest sum, and return its sum.")
    st.code('''def maxSubArray(nums):
    max_sum = cur_sum = nums[0]
    for num in nums[1:]:
        cur_sum = max(num, cur_sum + num)
        max_sum = max(max_sum, cur_sum)
    return max_sum''', language='python')

with problem_tabs[3]:
    st.subheader("Climbing Stairs")
    st.markdown("**Category:** Dynamic Programming")
    st.markdown("**Time Complexity:** $O(N)$ | **Space Complexity:** $O(1)$")
    st.write("You are climbing a staircase. It takes `n` steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?")
    st.code('''def climbStairs(n):
    if n <= 2: return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b''', language='python')
