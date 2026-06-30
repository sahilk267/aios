#!/usr/bin/env python3
"""AIOS File Watcher for Automatic Indexing.

Monitors file system changes and triggers re-indexing of modified files.
Can also be used as a Git hook for post-commit indexing.
"""

import argparse
import asyncio
import structlog
import sys
import time
from pathlib import Path
from typing import Set

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from aios.knowledge.indexer import index_file, should_index_file
from aios.core.config import settings

# Configure logging
structlog.configure(
    processors=[
        structlog.std,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(colors=True),
    ]
)

logger = structlog.get_logger(__name__)


class FileWatcher:
    """Watches for file changes and triggers indexing."""
    
    def __init__(self, watch_dir: Path, interval: float = 5.0):
        self.watch_dir = watch_dir
        self.interval = interval
        self.known_files: dict[str, float] = {}
        self.running = False
    
    async def scan_files(self) -> dict[str, float]:
        """Scan directory for files and their modification times."""
        files = {}
        for file_path in self.watch_dir.rglob("*"):
            if file_path.is_file() and should_index_file(file_path):
                try:
                    mtime = file_path.stat().st_mtime
                    files[str(file_path)] = mtime
                except OSError:
                    continue
        return files
    
    async def process_changes(self, current_files: dict[str, float]) -> int:
        """Process file changes and index new/modified files."""
        indexed = 0
        
        # Find new and modified files
        for file_path, mtime in current_files.items():
            if file_path not in self.known_files or self.known_files[file_path] != mtime:
                path = Path(file_path)
                result = await index_file(path)
                if result:
                    indexed += 1
        
        # Find deleted files (would need cleanup in vector store)
        # For now, we just update our known files
        
        self.known_files = current_files
        return indexed
    
    async def run(self):
        """Run the file watcher loop."""
        self.running = True
        logger.info("File watcher started", directory=str(self.watch_dir))
        
        # Initial scan
        self.known_files = await self.scan_files()
        logger.info("Initial scan complete", files=len(self.known_files))
        
        while self.running:
            try:
                current_files = await self.scan_files()
                indexed = await self.process_changes(current_files)
                
                if indexed > 0:
                    logger.info("Indexed files", count=indexed)
                
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Watcher error", error=str(e))
                await asyncio.sleep(self.interval)
    
    def stop(self):
        """Stop the file watcher."""
        self.running = False


async def index_all(watch_dir: Path) -> int:
    """Index all files in a directory."""
    from aios.knowledge.indexer import index_directory
    return await index_directory(watch_dir)


async def handle_git_hook():
    """Handle Git post-commit hook."""
    import subprocess
    
    # Get list of changed files from last commit
    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    
    if result.returncode != 0:
        logger.error("Git hook failed", error=result.stderr)
        return
    
    changed_files = result.stdout.strip().split("\n")
    indexed = 0
    
    for file_path in changed_files:
        path = Path(file_path)
        if path.exists() and should_index_file(path):
            result = await index_file(path)
            if result:
                indexed += 1
    
    logger.info("Git hook indexing complete", files=indexed)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AIOS File Watcher")
    parser.add_argument(
        "--watch-dir",
        type=Path,
        default=Path("."),
        help="Directory to watch for changes",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Scan interval in seconds",
    )
    parser.add_argument(
        "--index-all",
        action="store_true",
        help="Index all files and exit",
    )
    parser.add_argument(
        "--git-hook",
        action="store_true",
        help="Run as Git post-commit hook",
    )
    
    args = parser.parse_args()
    
    if args.git_hook:
        asyncio.run(handle_git_hook())
    elif args.index_all:
        count = asyncio.run(index_all(args.watch_dir))
        print(f"Indexed {count} files")
    else:
        watcher = FileWatcher(args.watch_dir, args.interval)
        try:
            asyncio.run(watcher.run())
        except KeyboardInterrupt:
            watcher.stop()
            print("\nFile watcher stopped")


if __name__ == "__main__":
    main()
