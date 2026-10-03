"""Manages state.vscdb updates, backups, rollbacks, and running process checks."""

import base64
import os
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path


def is_antigravity_running() -> bool:
    """Check if any Antigravity IDE process is actively running."""
    try:
        proc = subprocess.run(
            ["tasklist"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = proc.stdout.lower()
        targets = ["antigravity.exe", "antigravity ide.exe", "code.exe"]
        for target in targets:
            if target in output:
                return True
    except Exception:
        pass
    return False


def backup_state_db(db_path: str) -> str:
    """Create a timestamped backup copy of state.vscdb."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def get_current_index(db_path: str) -> str | None:
    """Read current Base64 encoded value of trajectorySummaries."""
    if not os.path.exists(db_path):
        return None
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        row = cur.execute(
            "SELECT value FROM ItemTable WHERE key = 'antigravityUnifiedStateSync.trajectorySummaries';"
        ).fetchone()
        con.close()
        return row[0] if row else None
    except Exception:
        return None


def write_trajectory_summaries(db_path: str, raw_payload: bytes) -> bool:
    """Write base64-encoded Protobuf index into state.vscdb ItemTable."""
    b64_val = base64.b64encode(raw_payload).decode("ascii")

    con = sqlite3.connect(db_path, timeout=10)
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO ItemTable (key, value)
        VALUES ('antigravityUnifiedStateSync.trajectorySummaries', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value;
        """,
        (b64_val,),
    )
    con.commit()
    con.close()
    return True


def rollback_state_db(db_path: str) -> str | None:
    """Find the most recent backup and restore it."""
    dir_name = os.path.dirname(db_path)
    base_name = os.path.basename(db_path)
    candidates = []

    for f in os.listdir(dir_name):
        if f.startswith(f"{base_name}.backup_"):
            candidates.append(os.path.join(dir_name, f))

    if not candidates:
        return None

    candidates.sort(key=os.path.getmtime, reverse=True)
    latest_backup = candidates[0]
    shutil.copy2(latest_backup, db_path)
    return latest_backup
