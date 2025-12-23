#!/usr/bin/env python3
"""
Simple test runner that bypasses database issues
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\nRunning: {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"SUCCESS: {description}")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FAILED: {description}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Run simple tests that don't require database"""
    print("Running Simple Tests (No Database)")
    print("=" * 50)
    
    # Set environment variables
    os.environ['SECRET_KEY'] = "test-secret-key-for-testing-only"
    os.environ['DATABASE_URL'] = "sqlite+aiosqlite:///:memory:"
    os.environ['REDIS_URL'] = "redis://localhost:6379"
    
    # Test commands that should work
    test_commands = [
        ("python -m pytest tests/test_models_contact.py -v", "Contact Model Tests"),
        ("python -m pytest tests/test_models_meeting.py -v", "Meeting Model Tests"),
        ("python -m pytest tests/test_models_session.py -v", "Session Model Tests"),
        ("python -m pytest tests/test_models_session_event.py -v", "Session Event Model Tests"),
    ]
    
    results = {}
    for cmd, desc in test_commands:
        results[desc] = run_command(cmd, desc)
    
    # Print summary
    print("\nTest Results Summary")
    print("=" * 50)
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    overall_success = all(results.values())
    print(f"\nOverall Result: {'ALL TESTS PASSED' if overall_success else 'SOME TESTS FAILED'}")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
