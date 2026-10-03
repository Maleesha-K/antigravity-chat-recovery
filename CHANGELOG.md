# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-10-03
### Added
- Pure-Python zero-dependency Protobuf wire-format encoder/decoder.
- Multi-path scanner supporting `.db` SQLite and legacy `.pb` conversation files.
- Metadata and workspace URI preservation extracted from `trajectory_metadata_blob`.
- Safe process check to prevent SQLite file locks while Antigravity IDE is running.
- Automated snapshot backup and `--rollback` support for `state.vscdb`.
- 1-click execution scripts (`run.bat` for Windows and `run.sh` for macOS/Linux).
- GitHub Actions CI matrix running on Ubuntu, Windows, and macOS with Python 3.8 - 3.12.
- Automated PyInstaller binary release workflow.
