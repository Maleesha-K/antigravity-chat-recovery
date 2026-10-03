"""Command-line interface and orchestrator for Antigravity Chat Recovery."""

import argparse
import sys

from .detector import get_installation_paths
from .indexer import build_trajectory_summaries_payload
from .scanner import scan_conversations
from .state_manager import (
    backup_state_db,
    is_antigravity_running,
    rollback_state_db,
    write_trajectory_summaries,
)


def main():
    parser = argparse.ArgumentParser(
        description="Antigravity Chat Recovery: Restore missing past conversations in Google Antigravity IDE."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and display discovered conversations without modifying state.vscdb.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass the active running process check (not recommended).",
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Revert state.vscdb to the most recent backup.",
    )

    args = parser.parse_args()

    print("=" * 64)
    print("      Antigravity Chat Recovery Toolkit (v1.0.0)")
    print("  Restore hidden and desynced conversations in Antigravity")
    print("=" * 64)

    paths = get_installation_paths()
    db_path = paths["db_path"]

    if not db_path:
        print("\n[!] Error: Could not locate Antigravity IDE globalStorage/state.vscdb.")
        print("    Please ensure Antigravity IDE is installed on this machine.")
        sys.exit(1)

    print(f"\n[*] Detected State Database: {db_path}")

    # Rollback mode
    if args.rollback:
        restored = rollback_state_db(db_path)
        if restored:
            print(f"[+] Successfully rolled back state.vscdb from:\n    {restored}")
        else:
            print("[!] No previous backup files found to restore.")
        return

    # Process check
    if not args.force and not args.dry_run:
        if is_antigravity_running():
            print("\n[!] WARNING: Antigravity IDE or Code process is currently running.")
            print("    Please close Antigravity completely (File -> Exit) before running")
            print("    this tool, otherwise changes will be overwritten upon exit.")
            print("\n    To run anyway (for inspection), use --dry-run or --force.")
            sys.exit(1)

    # Scan conversations
    print("\n[*] Scanning conversation directories:")
    for d in paths["conversations_dirs"]:
        print(f"    - {d}")

    convs = scan_conversations(paths["conversations_dirs"])
    print(f"\n[+] Discovered {len(convs)} conversation(s) on disk:")

    for i, (cid, item) in enumerate(convs.items(), start=1):
        ws = item.get("workspace_uri", "") or "(No workspace bound)"
        title = item.get("title", "Untitled Conversation")
        print(f"  {i:2d}. [{cid[:8]}] {title[:50]} -> {ws}")

    if not convs:
        print("\n[!] No conversation files found to recover.")
        return

    if args.dry_run:
        print("\n[*] Dry run completed. No files or databases were modified.")
        return

    # Create backup before writing
    backup_file = backup_state_db(db_path)
    print(f"\n[+] Created snapshot backup:\n    {backup_file}")

    # Build and write payload
    payload = build_trajectory_summaries_payload(list(convs.values()))
    write_trajectory_summaries(db_path, payload)

    print(f"\n[+] SUCCESS! Successfully indexed {len(convs)} conversations into state.vscdb.")
    print("    You can now re-open Antigravity IDE to view your full past chat history.")
    print("=" * 64)


if __name__ == "__main__":
    main()
