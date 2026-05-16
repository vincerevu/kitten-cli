"""
Chat recording service — saves conversation history to JSONL files.
Ref: gemini-cli/packages/core/src/services/chatRecordingService.ts
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class ChatRecordingService:
    """
    Records conversation turns to JSONL files for persistence and replay.
    Each session gets its own file: ~/.kitten/sessions/<session_id>.jsonl
    """

    def __init__(
        self,
        sessions_dir: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        self.sessions_dir = sessions_dir or str(
            Path.home() / ".kitten" / "sessions"
        )
        self.session_id = session_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self._file_path = os.path.join(self.sessions_dir, f"{self.session_id}.jsonl")
        self._turn_count = 0
        self._initialized = False

    @property
    def file_path(self) -> str:
        return self._file_path

    def _ensure_dir(self) -> None:
        if not self._initialized:
            os.makedirs(self.sessions_dir, exist_ok=True)
            self._initialized = True

    def record_turn(self, message: Dict[str, Any]) -> None:
        """
        Append a single message/turn to the JSONL file.
        Each line is a JSON object with metadata.
        """
        self._ensure_dir()
        self._turn_count += 1

        record = {
            "turn": self._turn_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": message.get("role", "unknown"),
            "content": message.get("content"),
        }

        # Include tool_calls if present
        if "tool_calls" in message:
            record["tool_calls"] = message["tool_calls"]
        if "tool_call_id" in message:
            record["tool_call_id"] = message["tool_call_id"]

        with open(self._file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def record_event(self, event_type: str, data: Any = None) -> None:
        """Record a non-message event (e.g., session start, tool confirmation)."""
        self._ensure_dir()

        record = {
            "turn": self._turn_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "data": data,
        }

        with open(self._file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def record_history(self, history: List[Dict[str, Any]]) -> None:
        """Record an entire conversation history at once."""
        for msg in history:
            self.record_turn(msg)

    def load_session(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load a recorded session from JSONL.
        Returns list of recorded entries.
        """
        sid = session_id or self.session_id
        path = os.path.join(self.sessions_dir, f"{sid}.jsonl")

        if not os.path.isfile(path):
            return []

        entries = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return entries

    def restore_messages(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Restore conversation messages from a recorded session.
        Returns messages in the format expected by the LLM (role/content/tool_calls).
        """
        entries = self.load_session(session_id)
        messages = []

        for entry in entries:
            if "event" in entry:
                continue  # Skip events, only restore messages

            msg: Dict[str, Any] = {"role": entry.get("role", "user")}

            if entry.get("content") is not None:
                msg["content"] = entry["content"]

            if "tool_calls" in entry:
                msg["tool_calls"] = entry["tool_calls"]
            if "tool_call_id" in entry:
                msg["tool_call_id"] = entry["tool_call_id"]

            messages.append(msg)

        return messages

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all recorded sessions with metadata."""
        if not os.path.isdir(self.sessions_dir):
            return []

        sessions = []
        for fname in sorted(os.listdir(self.sessions_dir), reverse=True):
            if not fname.endswith(".jsonl"):
                continue

            fpath = os.path.join(self.sessions_dir, fname)
            sid = fname.replace(".jsonl", "")

            try:
                stat = os.stat(fpath)
                # Count lines (turns)
                with open(fpath, "r", encoding="utf-8") as f:
                    line_count = sum(1 for _ in f)

                sessions.append({
                    "session_id": sid,
                    "file": fpath,
                    "size_bytes": stat.st_size,
                    "turns": line_count,
                    "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                })
            except OSError:
                continue

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete a recorded session."""
        path = os.path.join(self.sessions_dir, f"{session_id}.jsonl")
        try:
            os.remove(path)
            return True
        except OSError:
            return False
