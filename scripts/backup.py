#!/usr/bin/env python3
"""
Medical Store Management System - Backup Script
Automated backup creation for code, database, and configuration
"""

import os
import sys
import shutil
import sqlite3
import subprocess
import json
from datetime import datetime
from pathlib import Path
import argparse
import logging