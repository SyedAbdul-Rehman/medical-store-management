# Version Control & Backup System

This document provides comprehensive version control and backup procedures for the Medical Store Management System.

## 🚀 Quick Commands

### Create Backup
```bash
# Quick backup with description
python scripts/backup.py "sidebar toggle fix completed"

# Create development snapshot
python scripts/backup_restore.py snapshot "phase4" "Bug fixes and improvements"
```

### List Available Versions
```bash
# List recent commits and backup branches
python scripts/backup_restore.py list

# Show project status
python scripts/backup_restore.py status
```

### Restore from Backup
```bash
# Restore to specific commit (creates new branch)
python scripts/backup_restore.py restore <commit-hash>

# Restore specific files only
git checkout <commit-hash> -- medical_store_app/ui/components/sidebar.py
```

## 📋 Version History

### Current Version: 1.0.0-beta
**Latest Commit**: `2d6dc5a`  
**Status**: Stable  
**Features**: Core UI framework with sidebar navigation fix

### Available Restore Points

#### Phase 1: Foundation (Commit: 732fa9a)
- Complete project structure
- Database layer and business logic
- Core models and repositories
- Authentication system
- Basic UI framework

#### Phase 2: Documentation (Commit: db0a9e1)
- Comprehensive README
- MIT License
- GitHub repository setup

#### Phase 3: Bug Fixes (Commit: 2d6dc5a) - **CURRENT**
- Fixed sidebar toggle text restoration
- Added development history tracking
- Enhanced test coverage
- Backup and restore utilities

## 🛠️ Backup Strategies

### 1. Automatic Daily Backups
```bash
# Add to crontab for daily backups
0 2 * * * cd /path/to/project && python scripts/backup.py "daily_backup"
```

### 2. Feature Development Backups
```bash
# Before starting new feature
python scripts/backup_restore.py snapshot "pre_feature" "Before implementing medicine UI"

# After completing feature
python scripts/backup_restore.py snapshot "post_feature" "Medicine UI implementation complete"
```

### 3. Release Backups
```bash
# Create release branch
git checkout -b release-v1.0.0
git push origin release-v1.0.0

# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 🔄 Restore Procedures

### Full Project Restore
```bash
# 1. Clone fresh copy
git clone https://github.com/SyedAbdul-Rehman/medical-store-management.git
cd medical-store-management

# 2. Restore to specific version
python scripts/backup_restore.py restore 2d6dc5a

# 3. Set up environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 4. Verify installation
python -m pytest
python medical_store_app/main.py
```

### Partial Restore (Specific Components)
```bash
# Restore only UI components
git checkout 2d6dc5a -- medical_store_app/ui/

# Restore only database layer
git checkout 732fa9a -- medical_store_app/models/ medical_store_app/repositories/

# Restore only tests
git checkout 2d6dc5a -- tests/
```

### Emergency Restore
```bash
# If main branch is corrupted, restore from backup branch
git checkout backup_20250113_143022_sidebar_fix
git checkout -b main-restored
git push origin main-restored

# Then merge back to main after verification
git checkout main
git reset --hard main-restored
git push --force-with-lease origin main
```

## 📊 Backup Verification

### Test Backup Integrity
```bash
# Run full test suite
python -m pytest -v

# Test application startup
python medical_store_app/main.py --help

# Check database integrity
python -c "from medical_store_app.config.database import DatabaseManager; db = DatabaseManager(); print('DB OK' if db.initialize() else 'DB Error')"
```

### Verify Backup Contents
```bash
# Check file count
find . -name "*.py" | wc -l

# Check test coverage
python -m pytest --cov=medical_store_app

# Verify git history
git log --oneline --graph --all
```

## 🔐 Security & Best Practices

### Sensitive Data Protection
- ✅ Database files excluded from git (.gitignore)
- ✅ No hardcoded passwords or API keys
- ✅ Environment variables for configuration
- ✅ Secure backup storage

### Backup Retention Policy
- **Daily Backups**: Keep for 30 days
- **Weekly Backups**: Keep for 12 weeks
- **Monthly Backups**: Keep for 12 months
- **Release Backups**: Keep permanently

### Access Control
```bash
# Set proper permissions on backup scripts
chmod +x scripts/backup.py
chmod +x scripts/backup_restore.py

# Secure backup directories
chmod 700 backups/
```

## 📱 Mobile/Remote Access

### GitHub Codespaces
```bash
# Open in GitHub Codespaces for remote development
# All backups and restore points available via git
```

### Cloud Backup Integration
```bash
# Sync to cloud storage (example with rclone)
rclone sync . remote:medical-store-backup --exclude ".git/**" --exclude ".venv/**"
```

## 🚨 Disaster Recovery

### Complete System Loss
1. **Clone Repository**
   ```bash
   git clone https://github.com/SyedAbdul-Rehman/medical-store-management.git
   ```

2. **Restore to Last Known Good State**
   ```bash
   python scripts/backup_restore.py restore 2d6dc5a
   ```

3. **Verify System Integrity**
   ```bash
   python -m pytest
   python medical_store_app/main.py
   ```

4. **Resume Development**
   ```bash
   git checkout main
   git pull origin main
   ```

### Database Corruption
```bash
# Restore database from backup
cp backups/medical_store_backup.db medical_store_app/data/medical_store.db

# Or reinitialize from schema
python -c "from medical_store_app.config.database import DatabaseManager; DatabaseManager().initialize()"
```

## 📞 Support Contacts

**Primary Developer**: Syed Abdul Rehman  
**GitHub**: [@SyedAbdul-Rehman](https://github.com/SyedAbdul-Rehman)  
**Repository**: [medical-store-management](https://github.com/SyedAbdul-Rehman/medical-store-management)

## 📝 Backup Log Template

```
Date: YYYY-MM-DD HH:MM:SS
Version: X.X.X
Commit: xxxxxxxx
Description: Brief description of changes
Files Changed: N files
Test Status: PASS/FAIL
Backup Branch: backup_YYYYMMDD_HHMMSS_description
Notes: Any additional notes
```

---

*Last Updated: January 2025*  
*Document Version: 1.0*