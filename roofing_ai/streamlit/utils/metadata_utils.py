from datetime import datetime
from typing import Any, Dict, List


def get_metadata_template() -> Dict[str, List[str]]:
    """
    Returns a template defining the expected metadata structure.

    Returns:
        Dict[str, List[str]]: Dictionary containing metadata field categories and their fields
    """
    return {
        "core_attributes": [
            "title",
            "category",
            "subcategory",
            "tags",
            "keywords",
            "description",
            "audience",
            "content_snippet",
        ],
        "functional_attributes": [
            "purpose",
            "question_intent",
            "document_type",
            "location",
        ],
        "technical_attributes": [
            "date_created",
            "date_last_updated",
            "author",
            "related_documents",
        ],
    }


def validate_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Validates the provided metadata against required fields and data types.

    Args:
        metadata (Dict[str, Any]): The metadata to validate

    Returns:
        bool: True if metadata is valid

    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Check required fields
    required_fields = ["title", "category", "description", "tags", "keywords"]
    for field in required_fields:
        if not metadata.get(field):
            raise ValueError(f"Missing required metadata field: {field}")

    # Validate data types
    list_fields = ["keywords", "audience", "question_intent", "tags", "location"]
    for field in list_fields:
        if field in metadata and not isinstance(metadata[field], list):
            raise ValueError(f"{field} must be a list")

    # Validate dates
    date_fields = ["date_created", "date_last_updated"]
    for field in date_fields:
        if field in metadata:
            try:
                datetime.fromisoformat(metadata[field])
            except ValueError:
                raise ValueError(f"{field} must be a valid ISO format date")

    return True
