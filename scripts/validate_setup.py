#!/usr/bin/env python3
"""
Validation script to verify project setup
"""
import os
import sys
from pathlib import Path


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    return Path(filepath).exists()


def check_directory_exists(dirpath: str) -> bool:
    """Check if a directory exists"""
    return Path(dirpath).is_dir()


def validate_project_structure():
    """Validate the project structure"""
    print("Validating Swara AI Identity Layer project structure...\n")
    
    required_files = [
        "README.md",
        "SETUP.md",
        "requirements.txt",
        ".gitignore",
        ".env.example",
        "pytest.ini",
        "infrastructure/app.py",
        "infrastructure/cdk.json",
        "infrastructure/requirements.txt",
        "infrastructure/stacks/swara_stack.py",
        "lambda/handlers/upload_handler.py",
        "lambda/handlers/voice_processor.py",
        "lambda/handlers/content_generator.py",
        "lambda/shared/models.py",
        "lambda/layers/dependencies/requirements.txt",
        "tests/conftest.py",
        "tests/test_models.py",
        "scripts/setup.sh",
        "scripts/setup.ps1",
        "scripts/deploy.sh",
    ]
    
    required_dirs = [
        "infrastructure",
        "infrastructure/stacks",
        "lambda",
        "lambda/handlers",
        "lambda/shared",
        "lambda/layers",
        "lambda/layers/dependencies",
        "frontend",
        "tests",
        "scripts",
    ]
    
    all_valid = True
    
    # Check directories
    print("Checking directories:")
    for directory in required_dirs:
        exists = check_directory_exists(directory)
        status = "✓" if exists else "✗"
        print(f"  {status} {directory}")
        if not exists:
            all_valid = False
    
    print("\nChecking files:")
    # Check files
    for filepath in required_files:
        exists = check_file_exists(filepath)
        status = "✓" if exists else "✗"
        print(f"  {status} {filepath}")
        if not exists:
            all_valid = False
    
    print("\n" + "="*60)
    if all_valid:
        print("✓ Project structure validation PASSED")
        print("\nNext steps:")
        print("1. Run setup script: ./scripts/setup.sh (Linux/Mac) or .\\scripts\\setup.ps1 (Windows)")
        print("2. Configure AWS credentials: aws configure")
        print("3. Deploy infrastructure: cd infrastructure && cdk deploy")
        return 0
    else:
        print("✗ Project structure validation FAILED")
        print("\nSome required files or directories are missing.")
        return 1


if __name__ == "__main__":
    sys.exit(validate_project_structure())
