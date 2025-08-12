#!/usr/bin/env python3
"""
Medical Store Management System - Backup & Restore Utility
Provides automated backup and restore functionality for the project
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class BackupRestoreManager:
    """Manages backup and restore operations for the project"""
    
    def __init__(self, project_root: str = None):
        """Initialize the backup manager"""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.backup_config_file = self.project_root / "scripts" / "backup_config.json"
        self.ensure_git_repo()
    
    def ensure_git_repo(self):
        """Ensure we're in a git repository"""
        try:
            subprocess.run(["git", "status"], 
                         cwd=self.project_root, 
                         capture_output=True, 
                         check=True)
        except subprocess.CalledProcessError:
            raise RuntimeError(f"Not a git repository: {self.project_root}")
    
    def get_commit_history(self) -> List[Dict]:
        """Get commit history with details"""
        try:
            result = subprocess.run([
                "git", "log", "--pretty=format:%H|%s|%an|%ad", "--date=short", "-20"
            ], cwd=self.project_root, capture_output=True, text=True, check=True)
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line and line.strip():
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commits.append({
                            'hash': parts[0].strip(),
                            'message': parts[1].strip(),
                            'author': parts[2].strip(),
                            'date': parts[3].strip()
                        })
            return commits
        except subprocess.CalledProcessError as e:
            print(f"Error getting commit history: {e}")
            return []
    
    def create_backup_branch(self, description: str = None) -> str:
        """Create a backup branch from current state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        branch_name = f"backup_{timestamp}"
        
        if description:
            # Sanitize description for branch name
            safe_desc = "".join(c for c in description if c.isalnum() or c in '-_').lower()
            branch_name = f"backup_{timestamp}_{safe_desc}"
        
        try:
            # Create and push backup branch
            subprocess.run(["git", "checkout", "-b", branch_name], 
                         cwd=self.project_root, check=True)
            subprocess.run(["git", "push", "origin", branch_name], 
                         cwd=self.project_root, check=True)
            subprocess.run(["git", "checkout", "main"], 
                         cwd=self.project_root, check=True)
            
            print(f"✅ Backup branch created: {branch_name}")
            return branch_name
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating backup branch: {e}")
            return ""
    
    def restore_from_commit(self, commit_hash: str, create_branch: bool = True) -> bool:
        """Restore project to a specific commit"""
        try:
            if create_branch:
                # Create a new branch for the restore
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                restore_branch = f"restore_{timestamp}_{commit_hash[:8]}"
                subprocess.run(["git", "checkout", "-b", restore_branch, commit_hash], 
                             cwd=self.project_root, check=True)
                print(f"✅ Restored to commit {commit_hash[:8]} in new branch: {restore_branch}")
            else:
                # Direct checkout (dangerous - will lose uncommitted changes)
                subprocess.run(["git", "checkout", commit_hash], 
                             cwd=self.project_root, check=True)
                print(f"✅ Restored to commit {commit_hash[:8]}")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error restoring from commit: {e}")
            return False
    
    def restore_specific_files(self, commit_hash: str, file_paths: List[str]) -> bool:
        """Restore specific files from a commit"""
        try:
            for file_path in file_paths:
                subprocess.run(["git", "checkout", commit_hash, "--", file_path], 
                             cwd=self.project_root, check=True)
            
            print(f"✅ Restored {len(file_paths)} files from commit {commit_hash[:8]}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error restoring files: {e}")
            return False
    
    def list_backup_points(self) -> List[Dict]:
        """List all available backup points (commits and branches)"""
        commits = self.get_commit_history()
        
        # Add branch information
        try:
            result = subprocess.run(["git", "branch", "-a"], 
                                  cwd=self.project_root, capture_output=True, text=True, check=True)
            branches = [line.strip().replace('* ', '').replace('remotes/origin/', '') 
                       for line in result.stdout.strip().split('\n') 
                       if 'backup_' in line]
        except subprocess.CalledProcessError:
            branches = []
        
        return {
            'commits': commits[:20],  # Last 20 commits
            'backup_branches': branches
        }
    
    def create_development_snapshot(self, phase_name: str, description: str) -> Dict:
        """Create a comprehensive development snapshot"""
        timestamp = datetime.now().isoformat()
        
        # Get current status
        status = self.get_project_status()
        
        # Create backup branch
        backup_branch = self.create_backup_branch(phase_name)
        
        snapshot = {
            'timestamp': timestamp,
            'phase_name': phase_name,
            'description': description,
            'backup_branch': backup_branch,
            'commit_hash': status['current_commit'],
            'files_changed': status['files_changed'],
            'test_status': self.run_tests(),
            'project_stats': self.get_project_stats()
        }
        
        # Save snapshot info
        self.save_snapshot_info(snapshot)
        
        return snapshot
    
    def get_project_status(self) -> Dict:
        """Get current project status"""
        try:
            # Current commit
            commit_result = subprocess.run(["git", "rev-parse", "HEAD"], 
                                         cwd=self.project_root, capture_output=True, text=True, check=True)
            current_commit = commit_result.stdout.strip()
            
            # Changed files
            status_result = subprocess.run(["git", "status", "--porcelain"], 
                                         cwd=self.project_root, capture_output=True, text=True, check=True)
            files_changed = len(status_result.stdout.strip().split('\n')) if status_result.stdout.strip() else 0
            
            return {
                'current_commit': current_commit,
                'files_changed': files_changed,
                'branch': self.get_current_branch()
            }
        except subprocess.CalledProcessError as e:
            return {'error': str(e)}
    
    def get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(["git", "branch", "--show-current"], 
                                  cwd=self.project_root, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"
    
    def run_tests(self) -> Dict:
        """Run project tests and return results"""
        try:
            result = subprocess.run(["python", "-m", "pytest", "--tb=short", "-q"], 
                                  cwd=self.project_root, capture_output=True, text=True)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr,
                'return_code': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_project_stats(self) -> Dict:
        """Get project statistics"""
        stats = {
            'total_files': 0,
            'python_files': 0,
            'test_files': 0,
            'lines_of_code': 0
        }
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    stats['total_files'] += 1
                    stats['python_files'] += 1
                    
                    if 'test_' in file:
                        stats['test_files'] += 1
                    
                    # Count lines
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            stats['lines_of_code'] += len(f.readlines())
                    except:
                        pass
        
        return stats
    
    def save_snapshot_info(self, snapshot: Dict):
        """Save snapshot information to file"""
        snapshots_file = self.project_root / "scripts" / "snapshots.json"
        
        # Load existing snapshots
        snapshots = []
        if snapshots_file.exists():
            try:
                with open(snapshots_file, 'r') as f:
                    snapshots = json.load(f)
            except:
                snapshots = []
        
        # Add new snapshot
        snapshots.append(snapshot)
        
        # Keep only last 50 snapshots
        snapshots = snapshots[-50:]
        
        # Save updated snapshots
        snapshots_file.parent.mkdir(exist_ok=True)
        with open(snapshots_file, 'w') as f:
            json.dump(snapshots, f, indent=2)


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python backup_restore.py <command> [args]")
        print("\nCommands:")
        print("  list                    - List all backup points")
        print("  backup <description>    - Create backup branch")
        print("  restore <commit_hash>   - Restore from commit")
        print("  snapshot <phase> <desc> - Create development snapshot")
        print("  status                  - Show project status")
        return
    
    manager = BackupRestoreManager()
    command = sys.argv[1]
    
    if command == "list":
        backup_points = manager.list_backup_points()
        print("\n📋 Recent Commits:")
        for commit in backup_points['commits'][:10]:
            print(f"  {commit['hash'][:8]} - {commit['message']} ({commit['date']})")
        
        print(f"\n🔄 Backup Branches:")
        for branch in backup_points['backup_branches']:
            print(f"  {branch}")
    
    elif command == "backup" and len(sys.argv) > 2:
        description = " ".join(sys.argv[2:])
        branch = manager.create_backup_branch(description)
        if branch:
            print(f"Backup created: {branch}")
    
    elif command == "restore" and len(sys.argv) > 2:
        commit_hash = sys.argv[2]
        success = manager.restore_from_commit(commit_hash)
        if success:
            print(f"Restored to commit: {commit_hash}")
    
    elif command == "snapshot" and len(sys.argv) > 3:
        phase = sys.argv[2]
        description = " ".join(sys.argv[3:])
        snapshot = manager.create_development_snapshot(phase, description)
        print(f"Development snapshot created: {snapshot['backup_branch']}")
    
    elif command == "status":
        status = manager.get_project_status()
        stats = manager.get_project_stats()
        print(f"\n📊 Project Status:")
        print(f"  Current commit: {status['current_commit'][:8]}")
        print(f"  Current branch: {status['branch']}")
        print(f"  Files changed: {status['files_changed']}")
        print(f"  Python files: {stats['python_files']}")
        print(f"  Test files: {stats['test_files']}")
        print(f"  Lines of code: {stats['lines_of_code']}")
    
    else:
        print("Invalid command or missing arguments")


if __name__ == "__main__":
    main()