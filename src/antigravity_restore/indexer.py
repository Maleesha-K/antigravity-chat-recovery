"""Builds and serializes the complete trajectorySummaries Protobuf index payload."""

from .protobuf_codec import (
    encode_length_delimited,
    encode_string_field,
    encode_timestamp_field,
)


def build_single_summary_blob(
    conversation_id: str,
    title: str,
    workspace_uri: str,
    created_at: int,
    updated_at: int,
) -> bytes:
    """Build a single TrajectorySummary Protobuf message (wire format).

    Field mappings for TrajectorySummary:
      1: trajectory_id (string)
      2: title (string)
      3: created_at (Timestamp)
      4: updated_at (Timestamp)
      7: workspace_uri (string)
    """
    body = bytearray()
    body.extend(encode_string_field(1, conversation_id))
    body.extend(encode_string_field(2, title or "Untitled Conversation"))
    body.extend(encode_timestamp_field(3, created_at))
    body.extend(encode_timestamp_field(4, updated_at))
    if workspace_uri:
        body.extend(encode_string_field(7, workspace_uri))

    return bytes(body)


def build_trajectory_summaries_payload(conversations: list[dict]) -> bytes:
    """Build the top-level TrajectorySummaries message containing all items.

    TrajectorySummaries message:
      Repeated field 1: TrajectorySummary items
    """
    # Sort conversations newest first by updated_at or created_at
    sorted_convs = sorted(
        conversations,
        key=lambda c: max(c.get("updated_at", 0), c.get("created_at", 0)),
        reverse=True,
    )

    top_level = bytearray()
    for item in sorted_convs:
        summary_blob = build_single_summary_blob(
            conversation_id=item["conversation_id"],
            title=item.get("title", "Untitled Conversation"),
            workspace_uri=item.get("workspace_uri", ""),
            created_at=item.get("created_at", 0),
            updated_at=item.get("updated_at", 0),
        )
        # Field 1 repeated length-delimited
        top_level.extend(encode_length_delimited(1, summary_blob))

    return bytes(top_level)
