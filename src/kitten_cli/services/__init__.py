from kitten_cli.services.git_service import GitService
from kitten_cli.services.file_discovery import FileDiscoveryService, BINARY_EXTENSIONS
from kitten_cli.services.shell_execution import (
    ShellExecutionService,
    ShellResult,
    BackgroundProcess,
    ProcessStatus,
)
from kitten_cli.services.chat_recording import ChatRecordingService
from kitten_cli.services.loop_detection import LoopDetectionService
from kitten_cli.services.memory_service import MemoryService
from kitten_cli.services.session_summary import SessionSummaryService
from kitten_cli.services.folder_trust import FolderTrustService

__all__ = [
    # Core services (Phase 5.1-5.3)
    "GitService",
    "FileDiscoveryService",
    "BINARY_EXTENSIONS",
    "ShellExecutionService",
    "ShellResult",
    "BackgroundProcess",
    "ProcessStatus",
    # Advanced services (Phase 5.4-5.8)
    "ChatRecordingService",
    "LoopDetectionService",
    "MemoryService",
    "SessionSummaryService",
    "FolderTrustService",
]
