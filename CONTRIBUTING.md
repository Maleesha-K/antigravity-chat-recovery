# Contributing to Antigravity Chat Recovery

Thank you for your interest in improving Antigravity Chat Recovery!

## How You Can Contribute

1. **Reporting Issues:**
   - If a conversation fails to be indexed or displays an incorrect title, please open an issue including the operating system and IDE version.
   - Do **not** post sensitive private API keys or personal chat logs.

2. **Submitting Pull Requests:**
   - Keep the codebase **zero-dependency** (pure standard library only).
   - Ensure all tests pass by running:
     ```bash
     python -m unittest discover -s tests
     ```
   - Follow clean code practices and include unit tests for new decoding/encoding routines.

## Code Structure

- `src/antigravity_restore/detector.py`: Platform-specific path detection.
- `src/antigravity_restore/protobuf_codec.py`: Pure-python Protobuf wire-format encoder/decoder.
- `src/antigravity_restore/scanner.py`: Extracts titles and workspace URIs from SQLite files.
- `src/antigravity_restore/indexer.py`: Serializes the top-level index.
- `src/antigravity_restore/state_manager.py`: Safe backups, rollbacks, and atomic writes.
