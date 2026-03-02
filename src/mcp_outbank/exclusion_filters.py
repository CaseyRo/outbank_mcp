"""Exclusion filter utilities for transaction filtering.

This module contains pure-Python functions for filtering transactions based on
category and tag exclusions. Extracted to a separate module to allow testing
without importing FastMCP dependencies.
"""

import os
from typing import Any


def env_exclusion_list(name: str) -> list[str]:
    """Parse a comma-separated exclusion list from environment variable.

    Returns a list of normalized (lowercase, stripped) exclusion values.
    Empty strings and whitespace-only values are filtered out.

    This function returns normalized values for matching purposes.
    Use env_exclusion_list_display() to get original case-preserved values for display.
    """
    value = os.getenv(name)
    if not value:
        return []
    return [item.strip().lower() for item in value.split(",") if item.strip()]


def env_exclusion_list_display(name: str) -> list[str]:
    """Parse a comma-separated exclusion list from environment variable for display.

    Returns a list of original case-preserved (but trimmed) exclusion values.
    Empty strings and whitespace-only values are filtered out.

    This function preserves the original case as entered by the user for display purposes.
    """
    value = os.getenv(name)
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def matches_exclusion(value: str, exclusion_list: list[str]) -> bool:
    """Check if a value matches any exclusion in the list.

    Matching is case-insensitive and supports partial matches.
    Returns True if the value contains any exclusion string.
    """
    if not exclusion_list:
        return False
    normalized_value = value.lower()
    # Normalize exclusion list items to lowercase for case-insensitive matching
    normalized_exclusions = [exclusion.lower() for exclusion in exclusion_list]
    return any(exclusion in normalized_value for exclusion in normalized_exclusions)


def should_exclude_transaction(transaction: dict[str, Any]) -> bool:
    """Check if a transaction should be excluded based on category or tag filters.

    A transaction is excluded if:
    - Its category, subcategory, or category_path matches any value in EXCLUDED_CATEGORIES, OR
    - Any of its tags matches any value in EXCLUDED_TAGS

    Matching is case-insensitive and supports partial matches (e.g., "transfer"
    matches "internal-transfer" or "Finances & Insurances / Transfer").

    Args:
        transaction: Normalized transaction dictionary with 'category', 'subcategory',
                     'category_path', and 'tags' fields

    Returns:
        True if the transaction should be excluded, False otherwise
    """
    excluded_categories = env_exclusion_list("EXCLUDED_CATEGORIES")
    excluded_tags = env_exclusion_list("EXCLUDED_TAGS")

    # Check category exclusion - check category, subcategory, and category_path
    if excluded_categories:
        category = transaction.get("category", "")
        subcategory = transaction.get("subcategory", "")
        category_path = transaction.get("category_path", "")

        if category and matches_exclusion(category, excluded_categories):
            return True
        if subcategory and matches_exclusion(subcategory, excluded_categories):
            return True
        if category_path and matches_exclusion(category_path, excluded_categories):
            return True

    # Check tag exclusion
    tags = transaction.get("tags", [])
    if tags:
        for tag in tags:
            if matches_exclusion(tag, excluded_tags):
                return True

    return False
