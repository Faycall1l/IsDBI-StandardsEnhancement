"""
Cleanup Script for Islamic Finance Standards AI

This script helps identify and clean up deprecated files in the codebase,
optimize the architecture for the knowledge graph, and ensure efficient
message passing between teams and agents in the multi-agent system.
"""

import os
import shutil
import json
import re
import asyncio
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
import logging
from datetime import datetime, timedelta
import importlib.util
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodebaseCleaner:
    """Helper class for cleaning up the codebase."""
    
    def __init__(self, root_dir: str):
        """Initialize with the root directory to clean."""
        self.root_dir = Path(root_dir)
        self.backup_dir = self.root_dir.parent / f"{self.root_dir.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.removed_files = []
        self.removed_dirs = []
        
        # Files to be removed (relative to root_dir)
        self.deprecated_files = [
            # Deprecated test files
            "test_web_search.py",
            "test_api_trigger.py",
            "test_kafka_connection.py",
            "test_fas28_enhancement.py",
            "test_imports.py",
            "direct_agent_test.py",
            "realistic_test.py",
            "trigger_real_agents.py",
            "real_agent_results.json",
            "mock_trigger.py",
            
            # Deprecated utility scripts
            "cleanup_old_files.py",
            "fix_imports.py",
            "fix_line_continuation.py",
            "fix_all_imports.py",
            "migrate_agents.py",
            "set_api_key.py",
            
            # Deprecated autonomous system files
            "autonomous_standards_system.py",
            
            # Deprecated single-agent implementations
            "IslamicFinanceStandardsAI/core/agents/single_agent_processor.py",
            "IslamicFinanceStandardsAI/core/agents/single_enhancement_agent.py",
            "IslamicFinanceStandardsAI/core/agents/single_validation_agent.py",
            
            # Old message bus implementations
            "IslamicFinanceStandardsAI/core/messaging/simple_bus.py",
            "IslamicFinanceStandardsAI/core/messaging/kafka_bus.py"
        ]
        
        # Directories to be removed (relative to root_dir)
        self.deprecated_dirs = [
            "autonomous_system",
            "IslamicFinanceStandardsAI/agents_backup",
            "IslamicFinanceStandardsAI/agents_backup_20250517_011617",
            "src/enhancement_agent",  # Deprecated single-agent implementation
            "IslamicFinanceStandardsAI/core/single_agent",  # Old single-agent implementations
            "IslamicFinanceStandardsAI/database/backup",  # Database backup directories
            "IslamicFinanceStandardsAI/database/old_implementations",  # Old database implementations
            "backups",  # General backup directory
            "old_code"  # Old code directory
        ]
        
        # Files to be optimized (relative to root_dir)
        self.files_to_optimize = [
            "IslamicFinanceStandardsAI/database/implementations/neo4j_knowledge_graph.py",
            "IslamicFinanceStandardsAI/core/messaging/message_bus.py",
            "multi_agent_team_pipeline.py"
        ]
    
    def create_backup(self) -> bool:
        """Create a backup of the current state."""
        try:
            if not self.backup_dir.exists():
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created backup directory: {self.backup_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def find_duplicate_files(self) -> Dict[str, List[Path]]:
        """Find potential duplicate files based on name."""
        duplicates: Dict[str, List[Path]] = {}
        all_files = list(self.root_dir.glob('**/*'))
        
        for file_path in all_files:
            if file_path.is_file():
                name = file_path.name
                if name not in duplicates:
                    duplicates[name] = []
                duplicates[name].append(file_path)
        
        # Filter out non-duplicates
        return {k: v for k, v in duplicates.items() if len(v) > 1}
    
    def find_large_files(self, size_threshold: int = 1024 * 500) -> List[Tuple[Path, int]]:
        """Find files larger than the specified threshold (default: 500KB)."""
        large_files = []
        all_files = list(self.root_dir.glob('**/*'))
        
        for file_path in all_files:
            if file_path.is_file():
                size = file_path.stat().st_size
                if size > size_threshold:
                    large_files.append((file_path, size))
        
        # Sort by size (largest first)
        return sorted(large_files, key=lambda x: x[1], reverse=True)
    
    def _find_duplicate_agent_files(self) -> Dict[str, List[str]]:
        """Find duplicate agent implementation files."""
        duplicates = {}
        
        # Look for base agent implementations that might be redundant
        base_agent_files = []
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py') and 'base' in file.lower() and 'agent' in file.lower():
                    base_agent_files.append(str(Path(root) / file))
        
        if len(base_agent_files) > 1:
            duplicates['base_agent_implementations'] = base_agent_files
            
        # Look for multiple coordinators with similar names
        coordinator_files = []
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py') and 'coordinator' in file.lower():
                    coordinator_files.append(str(Path(root) / file))
        
        if len(coordinator_files) > 1:
            duplicates['coordinator_implementations'] = coordinator_files
            
        return duplicates
    
    def find_old_files(self, days_old: int = 90) -> List[str]:
        """Find files older than specified days."""
        old_files = []
        cutoff = datetime.now() - timedelta(days=days_old)
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                file_path = Path(root) / file
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff:
                    old_files.append(str(file_path))
        
        return old_files
    
    def find_empty_dirs(self) -> List[str]:
        """Find empty directories."""
        empty_dirs = []
        
        for root, dirs, _ in os.walk(self.root_dir, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        empty_dirs.append(str(dir_path))
                except Exception as e:
                    logger.warning(f"Error checking directory {dir_path}: {e}")
        
        return empty_dirs
    
    def find_deprecated_terms(self) -> Dict[str, List[str]]:
        """Find files containing deprecated terms."""
        deprecated_terms = [
            'deprecated', 'old_', '_old', 'backup', 'temp', 'tmp', 'archive',
            'todo', 'fixme', 'xxx', 'hack', 'legacy'
        ]
        
        result = {term: [] for term in deprecated_terms}
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(('.py', '.md', '.txt')):
                    file_path = Path(root) / file
                    try:
                        # First check filename for deprecated terms
                        file_path_str = str(file_path).lower()
                        for term in deprecated_terms:
                            if term in file_path_str:
                                result[term].append(str(file_path))
                                break  # No need to check content if filename matches
                        else:  # Only check content if filename doesn't match any deprecated terms
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read().lower()
                                for term in deprecated_terms:
                                    if term in content:
                                        result[term].append(str(file_path))
                                        break
                    except Exception as e:
                        logger.warning(f"Error reading {file_path}: {e}")
        
        return {k: v for k, v in result.items() if v}
    
    def analyze_codebase(self) -> Dict[str, any]:
        """Analyze the codebase for potential cleanup targets."""
        return {
            'duplicate_files': self.find_duplicate_files(),
            'old_files': self.find_old_files(),
            'empty_dirs': self.find_empty_dirs(),
            'deprecated_terms': self.find_deprecated_terms()
        }
    
    def remove_file(self, file_path: str) -> bool:
        """Safely remove a file with backup."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
                
            # Create backup
            rel_path = file_path.relative_to(self.root_dir)
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy to backup
            shutil.copy2(file_path, backup_path)
            
            # Remove original
            file_path.unlink()
            self.removed_files.append(str(file_path))
            logger.info(f"Removed file (backup at {backup_path}): {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove {file_path}: {e}")
            return False
    
    def remove_dir(self, dir_path: str) -> bool:
        """Safely remove an empty directory."""
        try:
            dir_path = Path(dir_path)
            if not dir_path.exists() or not dir_path.is_dir():
                return False
                
            # Skip non-empty directories
            if any(dir_path.iterdir()):
                return False
                
            # Create backup
            rel_path = dir_path.relative_to(self.root_dir)
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy empty directory structure
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Remove original
            dir_path.rmdir()
            self.removed_dirs.append(str(dir_path))
            logger.info(f"Removed empty directory (backup at {backup_path}): {dir_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove directory {dir_path}: {e}")
            return False
    
    def remove_deprecated_files(self) -> None:
        """Remove files that are deprecated or no longer needed."""
        # Remove pattern-based deprecated files
        patterns = [
            "*_old.py",
            "*_backup.py",
            "*.bak",
            "*_deprecated.py"
        ]
        
        for pattern in patterns:
            for file_path in self.root_dir.glob(f"**/{pattern}"):
                if file_path.is_file():
                    backup_path = self.backup_dir / file_path.relative_to(self.root_dir)
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_path)
                    os.remove(file_path)
                    self.removed_files.append(str(file_path))
                    logger.info(f"Removed deprecated file: {file_path}")
    
    def remove_deprecated_dirs(self) -> None:
        """Remove deprecated directories."""
        # Define patterns for deprecated directories
        dir_patterns = [
            "*_backup",
            "*_old",
            "*_deprecated",
            "__pycache__"
        ]
        
        # Find all directories matching the patterns
        deprecated_dirs = []
        for pattern in dir_patterns:
            for dir_path in self.root_dir.glob(f"**/{pattern}"):
                if dir_path.is_dir() and not str(dir_path).startswith(str(self.backup_dir)):
                    deprecated_dirs.append(dir_path)
        
        # Sort directories by depth (deepest first) to avoid dependency issues
        deprecated_dirs.sort(key=lambda x: len(str(x).split(os.sep)), reverse=True)
        self.deprecated_dirs = deprecated_dirs
        self.removed_dirs = []
        
        # Remove each directory
        for dir_path in deprecated_dirs:
            try:
                # Create backup directory structure
                backup_path = self.backup_dir / dir_path.relative_to(self.root_dir)
                backup_path.mkdir(parents=True, exist_ok=True)
                
                # Copy contents to backup
                for item in dir_path.glob("*"):
                    if item.is_file():
                        dest = backup_path / item.name
                        shutil.copy2(item, dest)
                
                # Remove directory
                shutil.rmtree(dir_path)
                self.removed_dirs.append(str(dir_path))
                logger.info(f"Removed deprecated directory: {dir_path}")
            except Exception as e:
                logger.error(f"Failed to remove directory {dir_path}: {e}")
        
        # Remove specifically identified deprecated files
        for file_name in self.deprecated_files:
            file_path = self.root_dir / file_name
            if file_path.is_file():
                backup_path = self.backup_dir / file_path.relative_to(self.root_dir)
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                os.remove(file_path)
                self.removed_files.append(str(file_path))
                logger.info(f"Removed deprecated file: {file_path}")
        
        # Remove deprecated directories
        for dir_name in self.deprecated_dirs:
            dir_path = self.root_dir / dir_name
            if dir_path.is_dir():
                backup_path = self.backup_dir / dir_path.relative_to(self.root_dir)
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(dir_path, backup_path, dirs_exist_ok=True)
                shutil.rmtree(dir_path)
                self.removed_dirs.append(str(dir_path))
                logger.info(f"Removed deprecated directory: {dir_path}")
    
    def cleanup(self, dry_run: bool = True) -> Dict[str, any]:
        """
        Clean up the codebase.
        
        Args:
            dry_run: If True, only show what would be done without making changes
            
        Returns:
            Dictionary with cleanup results
        """
        logger.info(f"{'DRY RUN - ' if dry_run else ''}Starting codebase cleanup in {self.root_dir}")
        
        analysis = self.analyze_codebase()
        return {
            'dry_run': True,
            'dry_run': False,
            'analysis': analysis,
            'removed_files': self.removed_files,
            'removed_dirs': self.removed_dirs,
            'backup_location': str(self.backup_dir)
        }

def analyze_agent_structure(root_dir: str):
    """Analyze the agent directory structure and identify potential issues."""
    print("\n=== Agent Structure Analysis ===")
    
    # Find all Python files in the agents directory
    python_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                rel_path = os.path.relpath(os.path.join(root, file), root_dir)
                python_files.append(rel_path)
    
    # Print summary
    print(f"Found {len(python_files)} Python files in the agents directory")
    
    # Look for potential duplicate implementations
    file_names = [os.path.basename(f) for f in python_files]
    duplicate_files = [f for f in set(file_names) if file_names.count(f) > 1]
    
    if duplicate_files:
        print("\nPotential duplicate files found:")
        for dup in sorted(duplicate_files):
            print(f"\n{dup}:")
            for path in [f for f in python_files if f.endswith(dup)]:
                print(f"  - {path}")
    
    # Look for base agent implementations
    base_agents = [f for f in python_files if 'base' in f.lower() and 'agent' in f.lower()]
    if base_agents:
        print("\nBase agent implementations found:")
        for agent in sorted(base_agents):
            print(f"  - {agent}")
    
    # Look for coordinator implementations
    coordinators = [f for f in python_files if 'coordinator' in f.lower()]
    if coordinators:
        print("\nCoordinator implementations found:")
        for coord in sorted(coordinators):
            print(f"  - {coord}")
    
    return {
        'total_files': len(python_files),
        'duplicate_files': duplicate_files,
        'base_agents': base_agents,
        'coordinators': coordinators
    }

async def optimize_knowledge_graph(file_path: Path) -> bool:
    """Optimize the Neo4j knowledge graph implementation."""
    try:
        # Check if file exists
        if not file_path.exists():
            logger.error(f"Knowledge graph file not found: {file_path}")
            return False
            
        logger.info(f"Optimizing knowledge graph implementation: {file_path}")
        
        # Read current content
        content = file_path.read_text()
        
        # Check if connection pooling is already implemented
        if "_connection_pool" in content and "get_connection" in content:
            logger.info("Connection pooling already implemented in knowledge graph.")
        else:
            logger.info("Adding connection pooling to knowledge graph implementation.")
            
            # Create backup of the file
            backup_file = file_path.with_suffix(f".py.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(file_path, backup_file)
            logger.info(f"Created backup of knowledge graph file: {backup_file}")
            
            # Add connection pooling implementation
            # This is a simplified example - in a real implementation, you would parse the file
            # and make more targeted changes
            connection_pool_code = '''
    # Connection pool for Neo4j
    _connection_pool = None
    _max_pool_size = 50
    _pool_acquisition_timeout = 60  # seconds
    
    async def _initialize_connection_pool(self):
        # Initialize the Neo4j connection pool
        if self.__class__._connection_pool is None:
            from neo4j import GraphDatabase
            self.__class__._connection_pool = GraphDatabase.driver(
                self._uri,
                auth=(self._username, self._password),
                max_connection_pool_size=self.__class__._max_pool_size,
                connection_acquisition_timeout=self.__class__._pool_acquisition_timeout
            )
            logger.info(f"Initialized Neo4j connection pool with max size {self.__class__._max_pool_size}")
    
    async def get_connection(self):
        # Get a connection from the pool
        if self.__class__._connection_pool is None:
            await self._initialize_connection_pool()
        return self.__class__._connection_pool.session()
'''
            
            # Find the class definition
            class_match = re.search(r"class Neo4jKnowledgeGraph\([^)]+\):\s*", content)
            if class_match:
                insert_pos = class_match.end()
                # Insert connection pool code after class definition
                new_content = content[:insert_pos] + connection_pool_code + content[insert_pos:]
                
                # Replace direct connection creation with pooled connections
                new_content = re.sub(
                    r"with GraphDatabase\.driver\([^)]+\)\.session\(\) as session:", 
                    "with await self.get_connection() as session:", 
                    new_content
                )
                
                # Write updated content
                file_path.write_text(new_content)
                logger.info("Added connection pooling to knowledge graph implementation.")
            else:
                logger.error("Could not find Neo4jKnowledgeGraph class definition.")
                return False
                
        return True
    except Exception as e:
        logger.error(f"Error optimizing knowledge graph: {e}")
        return False

async def optimize_message_bus(file_path: Path) -> bool:
    """Optimize the message bus implementation."""
    try:
        # Check if file exists
        if not file_path.exists():
            logger.error(f"Message bus file not found: {file_path}")
            return False
            
        logger.info(f"Optimizing message bus implementation: {file_path}")
        
        # Read current content
        content = file_path.read_text()
        
        # Check if priority queue is already implemented
        if "_message_queue" in content and "PriorityQueue" in content:
            logger.info("Priority queue already implemented in message bus.")
        else:
            logger.info("Adding priority queue to message bus implementation.")
            
            # Create backup of the file
            backup_file = file_path.with_suffix(f".py.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(file_path, backup_file)
            logger.info(f"Created backup of message bus file: {backup_file}")
            
            # This would be a more complex change in a real implementation
            # Here we just log that it would be done
            logger.info("Message bus optimization would require more complex changes.")
            logger.info("Please use the specific message_bus.py implementation that includes priority queue.")
                
        return True
    except Exception as e:
        logger.error(f"Error optimizing message bus: {e}")
        return False

async def optimize_team_pipeline(file_path: Path) -> bool:
    """Optimize the multi-agent team pipeline."""
    try:
        # Check if file exists
        if not file_path.exists():
            logger.error(f"Team pipeline file not found: {file_path}")
            return False
            
        logger.info(f"Optimizing multi-agent team pipeline: {file_path}")
        
        # Read current content
        content = file_path.read_text()
        
        # Check if message bus integration is already implemented
        if "message_bus" in content and "MessageBus" in content:
            logger.info("Message bus integration already implemented in team pipeline.")
        else:
            logger.info("Adding message bus integration to team pipeline.")
            
            # Create backup of the file
            backup_file = file_path.with_suffix(f".py.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(file_path, backup_file)
            logger.info(f"Created backup of team pipeline file: {backup_file}")
            
            # This would be a more complex change in a real implementation
            # Here we just log that it would be done
            logger.info("Team pipeline optimization would require more complex changes.")
            logger.info("Please use the specific multi_agent_team_pipeline.py implementation that includes message bus integration.")
                
        return True
    except Exception as e:
        logger.error(f"Error optimizing team pipeline: {e}")
        return False

async def main():
    """Run the codebase cleanup and optimization."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up and optimize the codebase.')
    parser.add_argument('--root-dir', default='.', help='Root directory to clean up')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--analyze', action='store_true', help='Only analyze the codebase without making changes')
    parser.add_argument('--optimize', action='store_true', help='Optimize the codebase architecture')
    args = parser.parse_args()
    
    root_dir = Path(args.root_dir)
    logger.info(f"Starting cleanup and optimization of codebase at {root_dir}")
    
    if args.analyze:
        analyze_agent_structure(args.root_dir)
        return
    
    cleaner = CodebaseCleaner(root_dir)
    
    # Create backup first
    if not cleaner.create_backup():
        logger.error("Failed to create backup. Aborting cleanup.")
        return
    
    # Find and report potential duplicates
    duplicates = cleaner.find_duplicate_files()
    if duplicates:
        logger.info(f"Found {len(duplicates)} potential duplicate files:")
        for name, paths in duplicates.items():
            logger.info(f"  {name}: {len(paths)} instances")
            for path in paths:
                logger.info(f"    - {path}")
    
    # Find and report large files
    large_files = cleaner.find_large_files()
    if large_files:
        logger.info(f"Found {len(large_files)} large files:")
        for path, size in large_files:
            logger.info(f"  {path}: {size/1024:.1f} KB")
    
    # Analyze agent structure
    analyze_agent_structure(root_dir)
    
    if not args.dry_run:
        # Remove deprecated files and directories
        cleaner.remove_deprecated_files()
        cleaner.remove_deprecated_dirs()
        
        if args.optimize:
            # Optimize knowledge graph implementation
            kg_file = root_dir / "IslamicFinanceStandardsAI" / "database" / "implementations" / "neo4j_knowledge_graph.py"
            await optimize_knowledge_graph(kg_file)
            
            # Optimize message bus implementation
            mb_file = root_dir / "IslamicFinanceStandardsAI" / "core" / "messaging" / "message_bus.py"
            await optimize_message_bus(mb_file)
            
            # Optimize multi-agent team pipeline
            pipeline_file = root_dir / "multi_agent_team_pipeline.py"
            await optimize_team_pipeline(pipeline_file)
    else:
        logger.info("Dry run - no files were actually removed or modified")
    
    # Report results
    logger.info(f"Cleanup and optimization complete.")
    if args.dry_run:
        logger.info(f"Would remove {len(cleaner.deprecated_files)} files and {len(cleaner.deprecated_dirs)} directories.")
        logger.info("Run without --dry-run to apply these changes")
    else:
        logger.info(f"Removed {len(cleaner.removed_files)} files and {len(cleaner.removed_dirs)} directories.")
    
    logger.info(f"Backup created at {cleaner.backup_dir}")
    
    # Print summary of files to be removed
    print(f"\nFiles to be removed: {len(cleaner.deprecated_files)}")
    for file in list(cleaner.deprecated_files)[:5]:  # Show first 5 files
        print(f"  - {file}")
    if len(cleaner.deprecated_files) > 5:
        print(f"  ... and {len(cleaner.deprecated_files) - 5} more")
    
    # Print summary of directories to be removed
    print(f"\nDirectories to be removed: {len(cleaner.deprecated_dirs)}")
    for dir_path in list(cleaner.deprecated_dirs)[:5]:  # Show first 5 dirs
        print(f"  - {dir_path}")
    if len(cleaner.deprecated_dirs) > 5:
        print(f"  ... and {len(cleaner.deprecated_dirs) - 5} more")
    
    if args.dry_run:
        print("\nRun without --dry-run to apply these changes")
    else:
        print("\nCleanup and optimization completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
