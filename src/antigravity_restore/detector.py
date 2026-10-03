"""Cross-platform directory and path detector for Antigravity IDE installations."""

import os
import platform
import subprocess
from pathlib import Path


def is_wsl() -> bool:
    """Return True if running inside Windows Subsystem for Linux."""
    if platform.system() != "Linux":
        return False
    if "microsoft" in platform.release().lower():
        return True
    try:
        with open("/proc/version", "r", encoding="utf-8") as f:
            return "microsoft" in f.read().lower()
    except Exception:
        return False


def get_wsl_windows_appdata() -> str | None:
    """Resolve Windows %APPDATA% path when running from within WSL."""
    try:
        proc = subprocess.run(
            ["cmd.exe", "/c", "echo %APPDATA%"],
            capture_output=True,
            text=True,
            check=True,
        )
        win_path = proc.stdout.strip()
        if win_path and win_path != "%APPDATA%":
            proc_wsl = subprocess.run(
                ["wslpath", win_path],
                capture_output=True,
                text=True,
                check=True,
            )
            wsl_path = proc_wsl.stdout.strip()
            if os.path.exists(wsl_path):
                return wsl_path
    except Exception:
        pass
    return None


def get_installation_paths() -> dict:
    """Detect state.vscdb location, conversation folders, and brain directories."""
    system = platform.system()
    db_candidates = []
    conv_candidates = []
    brain_candidates = []

    if system == "Windows":
        appdata = os.path.expandvars(r"%APPDATA%")
        userprofile = os.path.expandvars(r"%USERPROFILE%")
        gemini = os.path.join(userprofile, ".gemini")

        db_candidates = [
            os.path.join(appdata, "Antigravity IDE", "User", "globalStorage", "state.vscdb"),
            os.path.join(appdata, "antigravity", "User", "globalStorage", "state.vscdb"),
            os.path.join(appdata, "Antigravity", "User", "globalStorage", "state.vscdb"),
        ]
        conv_candidates = [
            os.path.join(gemini, "antigravity-ide", "conversations"),
            os.path.join(gemini, "antigravity", "conversations"),
        ]
        brain_candidates = [
            os.path.join(gemini, "antigravity-ide", "brain"),
            os.path.join(gemini, "antigravity", "brain"),
        ]

    elif is_wsl():
        wsl_appdata = get_wsl_windows_appdata()
        home = os.path.expanduser("~")
        gemini_wsl = os.path.join(home, ".gemini")

        if wsl_appdata:
            db_candidates = [
                os.path.join(wsl_appdata, "Antigravity IDE", "User", "globalStorage", "state.vscdb"),
                os.path.join(wsl_appdata, "antigravity", "User", "globalStorage", "state.vscdb"),
                os.path.join(wsl_appdata, "Antigravity", "User", "globalStorage", "state.vscdb"),
            ]
        conv_candidates = [
            os.path.join(gemini_wsl, "antigravity-ide", "conversations"),
            os.path.join(gemini_wsl, "antigravity", "conversations"),
        ]
        brain_candidates = [
            os.path.join(gemini_wsl, "antigravity-ide", "brain"),
            os.path.join(gemini_wsl, "antigravity", "brain"),
        ]

    elif system == "Darwin":  # macOS
        home = os.path.expanduser("~")
        support = os.path.join(home, "Library", "Application Support")
        gemini = os.path.join(home, ".gemini")

        db_candidates = [
            os.path.join(support, "Antigravity IDE", "User", "globalStorage", "state.vscdb"),
            os.path.join(support, "antigravity", "User", "globalStorage", "state.vscdb"),
        ]
        conv_candidates = [
            os.path.join(gemini, "antigravity-ide", "conversations"),
            os.path.join(gemini, "antigravity", "conversations"),
        ]
        brain_candidates = [
            os.path.join(gemini, "antigravity-ide", "brain"),
            os.path.join(gemini, "antigravity", "brain"),
        ]

    else:  # Linux
        home = os.path.expanduser("~")
        config = os.path.join(home, ".config")
        gemini = os.path.join(home, ".gemini")

        db_candidates = [
            os.path.join(config, "Antigravity IDE", "User", "globalStorage", "state.vscdb"),
            os.path.join(config, "Antigravity", "User", "globalStorage", "state.vscdb"),
        ]
        conv_candidates = [
            os.path.join(gemini, "antigravity-ide", "conversations"),
            os.path.join(gemini, "antigravity", "conversations"),
        ]
        brain_candidates = [
            os.path.join(gemini, "antigravity-ide", "brain"),
            os.path.join(gemini, "antigravity", "brain"),
        ]

    # Select existing paths
    primary_db = next((p for p in db_candidates if os.path.exists(p)), db_candidates[0] if db_candidates else "")
    existing_convs = [p for p in conv_candidates if os.path.isdir(p)]
    existing_brains = [p for p in brain_candidates if os.path.isdir(p)]

    return {
        "db_path": primary_db,
        "all_db_candidates": [p for p in db_candidates if os.path.exists(p)],
        "conversations_dirs": existing_convs or conv_candidates[:1],
        "brain_dirs": existing_brains or brain_candidates[:1],
        "system": system,
    }
