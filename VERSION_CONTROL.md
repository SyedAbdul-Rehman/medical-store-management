# Version Control & Backup/Restore Guide

This document provides a comprehensive guide for managing versions, creating backups, and restoring to any development step in the Medical Store Management System project.

## 📋 Table of Contents
- [Git Version History](#git-version-history)
- [Development Milestones](#development-milestones)
- [Backup & Restore Commands](#backup--restore-commands)
- [Branch Management](#branch-management)
- [Release Management](#release-management)
- [Emergency Recovery](#emergency-recovery)

## 🔄 Git Version History

### Current Repository Status
- **Repository**: https://github.com/SyedAbdul-Rehman/medical-store-management.git
- **Main Branch**: `main`
- **Current Version**: v1.0.0-beta
- **Last Updated**: January 2025

### Commit History & Restoration Points

#### 📌 Major Milestones

| Version | Commit Hash | Date | Description | Restore Command |
|---------|-------------|------|-------------|-----------------|
| v1.0.0-beta | `db0a9e1` | 2025-01-13 | Complete UI framework with documentation | `git checkout db0a9e1` |
| v0.9.0 | `732fa9a` | 2025-01-13 | Initial commit with core components | `git checkout 732fa9a` |

#### 🏗️ Development Steps (Detailed)

| Step | Feature | Commit | Files Changed | Restore Command |
|------|---------|--------|---------------|-----------------|
| 1 | Project Setup | `732fa9a` | 91 files | `git checkout 732fa9a` |
| 2 | Documentation | `db0a9e1` | +2 files | `git checkout db0a9e1` |

## 🎯 Development Milestones

### ✅ Completed Milestones

#### Milestone 1: Foundation Setup (v0.9.0)
- **Commit**: `732fa9a`
- **Date**: 2025-01-13
- **Features**:
  - Project structure and configuration
  - Database models and repositories
  - Business logic managers
  - Core UI framework
  - Main window with header, sidebar, content areas
  - Reusable UI components with validation
  - Base dialog system
  - Comprehensive test suite (38 tests)
  - Authentication system
  - Medicine and sales backend

**Restore Command**:
```bash
git checkout 732fa9a
```

#### Milestone 2: Documentation & Release Prep (v1.0.0-beta)
- **Commit**: `db0a9e1`
- **Date**: 2025-01-13
- **Features**:
  - Comprehensive README documentation
  - MIT License
  - Installation and usage guides
  - Project structure documentation

**Restore Command**:
```bash
git checkout db0a9e1
```

### 🔄 Upcoming Milestones

#### Milestone 3: Medicine Management UI (Planned)
- **Target**: v1.1.0
- **Features**:
  - Medicine inventory screens
  - Add/Edit/Delete medicine forms
  - Search and filtering
  - Stock management

#### Milestone 4: Billing System UI (Planned)
- **Target**: v1.2.0
- **Features**:
  - Sales interface
  - Receipt generation
  - Payment processing
  - Customer management

#### Milestone 5: Reports Dashboard (Planned)
- **Target**: v1.3.0
- **Features**:
  - Sales reports
  - Inventory reports
  - Analytics dashboard
  - Export functionality

## 🔧 Backup & Restore Commands

### Quick Restore to Any Point

#### 1. View All Available Restore Points
```bash
# View commit history with one-line format
git log --oneline

# View detailed commit history
git log --graph --pretty=format:'%h -%d %s (%cr) <%an>' --abbrev-commit

# View commits with file changes
git log --stat
```

#### 2. Restore to Specific Commit
```bash
# Restore to specific commit (temporary)
git checkout <commit-hash>

# Create new branch from specific commit
git checkout -b restore-point-<date> <commit-hash>

# Restore to specific commit permanently (CAUTION: This will lose newer changes)
git reset --hard <commit-hash>
```

#### 3. Restore Specific Files
```bash
# Restore specific file from commit
git checkout <commit-hash> -- <file-path>

# Restore multiple files
git checkout <commit-hash> -- file1.py file2.py

# Restore entire directory
git checkout <commit-hash> -- medical_store_app/ui/
```

### Creating Backup Points

#### 1. Create Development Snapshots
```bash
# Create snapshot with descriptive message
git add .
git commit -m "SNAPSHOT: <feature-name> - <description>"

# Tag important milestones
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

#### 2. Create Feature Branches
```bash
# Create feature branch
git checkout -b feature/medicine-ui
git push -u origin feature/medicine-ui

# Create backup branch
git checkout -b backup/before-major-changes
git push -u origin backup/before-major-changes
```

## 🌿 Branch Management Strategy

### Branch Types

#### Main Branches
- **`main`**: Production-ready code
- **`develop`**: Integration branch for features

#### Supporting Branches
- **`feature/*`**: New features (e.g., `feature/medicine-ui`)
- **`hotfix/*`**: Critical fixes (e.g., `hotfix/login-bug`)
- **`release/*`**: Release preparation (e.g., `release/v1.1.0`)
- **`backup/*`**: Backup points (e.g., `backup/before-ui-refactor`)

### Branch Commands

```bash
# Create and switch to feature branch
git checkout -b feature/new-feature

# Switch between branches
git checkout main
git checkout develop
git checkout feature/medicine-ui

# Merge feature to main
git checkout main
git merge feature/medicine-ui

# Delete branch after merge
git branch -d feature/medicine-ui
git push origin --delete feature/medicine-ui
```

## 🏷️ Release Management

### Semantic Versioning
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Process

#### 1. Prepare Release
```bash
# Create release branch
git checkout -b release/v1.1.0

# Update version numbers in files
# Update CHANGELOG.md
# Run tests
python -m pytest

# Commit release changes
git commit -m "Prepare release v1.1.0"
```

#### 2. Create Release
```bash
# Merge to main
git checkout main
git merge release/v1.1.0

# Create tag
git tag -a v1.1.0 -m "Release version 1.1.0"

# Push to GitHub
git push origin main
git push origin v1.1.0
```

#### 3. GitHub Release
```bash
# Create GitHub release (using GitHub CLI)
gh release create v1.1.0 --title "Version 1.1.0" --notes "Release notes here"
```

## 🚨 Emergency Recovery

### Scenario 1: Accidental File Deletion
```bash
# Restore deleted file from last commit
git checkout HEAD -- <deleted-file>

# Restore from specific commit
git checkout <commit-hash> -- <deleted-file>
```

### Scenario 2: Bad Commit
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Undo multiple commits
git reset --hard HEAD~3
```

### Scenario 3: Corrupted Working Directory
```bash
# Clean untracked files
git clean -fd

# Reset to last known good state
git reset --hard HEAD

# Reset to specific commit
git reset --hard <commit-hash>
```

### Scenario 4: Complete Repository Recovery
```bash
# Re-clone repository
git clone https://github.com/SyedAbdul-Rehman/medical-store-management.git

# Restore to specific version
cd medical-store-management
git checkout <commit-hash>
```

## 📊 Version Tracking Template

### For Each Major Development Step

```markdown
## Version X.Y.Z - [Date]

### 🎯 Milestone: [Milestone Name]
- **Commit Hash**: `<hash>`
- **Branch**: `<branch-name>`
- **Developer**: [Name]

### ✅ Features Added
- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3

### 🔧 Technical Changes
- [ ] Database changes
- [ ] UI modifications
- [ ] API updates

### 🧪 Testing
- [ ] Unit tests: X/Y passing
- [ ] Integration tests: X/Y passing
- [ ] Manual testing completed

### 📝 Notes
- Any important notes or considerations
- Breaking changes
- Migration steps required

### 🔄 Restore Command
```bash
git checkout <commit-hash>
```
```

## 🛠️ Automated Backup Script

Create this script for automated backups:

```bash
#!/bin/bash
# backup.sh - Automated backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_BRANCH="backup/auto_$DATE"

echo "Creating automated backup: $BACKUP_BRANCH"

# Create backup branch
git checkout -b $BACKUP_BRANCH
git push -u origin $BACKUP_BRANCH

# Return to main branch
git checkout main

echo "Backup created successfully: $BACKUP_BRANCH"
echo "Restore command: git checkout $BACKUP_BRANCH"
```

## 📋 Checklist for Each Development Phase

### Before Starting New Feature
- [ ] Create backup branch
- [ ] Document current state
- [ ] Run all tests
- [ ] Commit current changes

### After Completing Feature
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create descriptive commit
- [ ] Tag if milestone reached
- [ ] Push to GitHub

### Before Major Changes
- [ ] Create comprehensive backup
- [ ] Document rollback plan
- [ ] Notify team members
- [ ] Test in separate branch first

---

## 🔗 Quick Reference Commands

```bash
# View current status
git status
git log --oneline -10

# Create backup point
git add . && git commit -m "BACKUP: Before major changes"

# Restore to previous commit
git checkout <commit-hash>

# Create restore branch
git checkout -b restore-$(date +%Y%m%d) <commit-hash>

# Emergency reset
git reset --hard HEAD

# View all branches
git branch -a

# View all tags
git tag -l
```

---

**Remember**: Always test your restore commands in a separate directory or branch before applying them to your main development environment!