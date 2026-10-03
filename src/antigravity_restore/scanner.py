"""Extracts conversation metadata from SQLite databases and Protobuf files."""

import glob
import os
import re
import sqlite3
import urllib.parse
from pathlib import Path


def clean_title(raw_title: str) -> str:
    """Strip leading command tags or markdown prefixes to create a clean chat title."""
    if not raw_title:
        return "Untitled Conversation"
    title = raw_title.strip()
    title = re.sub(r"^<USER_REQUEST>\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^\s*#+\s*", "", title)
    # Take first line if multiple lines
    first_line = title.split("\n")[0].strip()
    return first_line[:120] if first_line else "Untitled Conversation"


def extract_metadata_from_sqlite(db_path: str) -> dict:
    """Read trajectory_metadata_blob and steps from conversation SQLite database."""
    result = {
        "title": "Untitled Conversation",
        "workspace_uri": "",
        "created_at": int(os.path.getmtime(db_path)),
        "updated_at": int(os.path.getmtime(db_path)),
    }

    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cur = con.cursor()

        # Check trajectory_metadata_blob
        try:
            row = cur.execute("SELECT data FROM trajectory_metadata_blob LIMIT 1;").fetchone()
            if row and row[0]:
                blob = row[0]
                # Look for file:/// workspace URI inside blob
                match = re.search(rb"file:///[^\x00-\x1f\x7f-\xff]+", blob)
                if match:
                    result["workspace_uri"] = match.group(0).decode("utf-8", errors="ignore")
        except Exception:
            pass

        # Try to find user prompt or title from steps
        try:
            steps = cur.execute("SELECT step_payload FROM steps WHERE step_payload IS NOT NULL LIMIT 5;").fetchall()
            for (payload,) in steps:
                if payload:
                    text_matches = re.findall(rb"[A-Za-z0-9\s,\.\?\!\-]{8,150}", payload)
                    for tm in text_matches:
                        s = tm.decode("utf-8", errors="ignore").strip()
                        if len(s) > 10 and not s.startswith("file://"):
                            result["title"] = clean_title(s)
                            break
                    if result["title"] != "Untitled Conversation":
                        break
        except Exception:
            pass

        con.close()
    except Exception:
        pass

    return result


def scan_conversations(conv_dirs: list[str]) -> dict[str, dict]:
    """Scan all conversation directories and return map of conversation_id -> metadata."""
    conversations = {}

    for cdir in conv_dirs:
        if not os.path.isdir(cdir):
            continue

        for fpath in glob.glob(os.path.join(cdir, "*")):
            base = os.path.basename(fpath)
            if base.endswith(".db-wal") or base.endswith(".db-shm"):
                continue

            cid = None
            if base.endswith(".db"):
                cid = base[:-3]
            elif base.endswith(".pb"):
                cid = base[:-3]

            if not cid:
                continue

            # Check if valid UUID pattern
            if not re.match(r"^[0-9a-fA-F\-]{32,36}$", cid):
                continue

            if cid in conversations:
                continue

            if base.endswith(".db"):
                meta = extract_metadata_from_sqlite(fpath)
            else:
                mtime = int(os.path.getmtime(fpath))
                meta = {
                    "title": "Restored Conversation",
                    "workspace_uri": "",
                    "created_at": mtime,
                    "updated_at": mtime,
                }

            meta["conversation_id"] = cid
            meta["file_path"] = fpath
            conversations[cid] = meta

    return conversations
