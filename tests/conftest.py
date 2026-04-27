"""
Root test conftest — registers shared fixture modules.

Adding a module here makes its fixtures available to ALL tests in the suite
without needing to import or copy anything into individual conftest files.
"""

pytest_plugins = [
    "tests.fixtures.flows",
]
