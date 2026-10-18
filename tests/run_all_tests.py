#!/usr/bin/env python3
"""
Master test runner for Campus Resource Hub
Runs all test files and provides colored, user-friendly output
"""
import sys
import subprocess
import os
from pathlib import Path

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(test_name):
    """Print success message in green"""
    print(f"{GREEN}[PASS] {test_name} test successful{RESET}")

def print_failure(test_name, error):
    """Print failure message in red"""
    print(f"{RED}[FAIL] {test_name} test failed{RESET}")
    if error:
        print(f"{RED}  Error: {error}{RESET}")

def print_info(text):
    """Print info message in yellow"""
    print(f"{YELLOW}{text}{RESET}")

def run_test_file(test_file):
    """Run a single test file and return success status and output"""
    # Handle both direct file paths and subdirectory paths
    test_path = Path(__file__).parent / test_file
    if not test_path.exists():
        return False, f"Test file not found: {test_file}"
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_path), "-v"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        success = result.returncode == 0
        output = result.stdout + result.stderr
        return success, output
    except subprocess.TimeoutExpired:
        return False, "Test timed out after 60 seconds"
    except Exception as e:
        return False, str(e)

def main():
    """Main test runner"""
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print_header("Campus Resource Hub - Test Suite")
    
    # Define test files and their display names
    test_files = [
        ("test_utils.py", "Unit Tests (Utilities)"),
        ("test_auth_flow.py", "Integration: Authentication Flow"),
        ("test_dal.py", "Integration: Data Access Layer (CRUD)"),
        ("test_booking_conflict.py", "Integration: Booking Conflict Detection"),
        ("test_waitlist.py", "Integration: Waitlist System"),
        ("test_security_sqli.py", "Integration: Security (SQL Injection)"),
        ("test_accessibility.py", "Integration: Accessibility (WCAG)"),
        ("ai_eval/test_chatbot.py", "AI Evaluation: Chatbot (Gemini)"),
    ]
    
    results = []
    total_tests = len(test_files)
    passed_tests = 0
    
    print_info(f"Running {total_tests} test suites...\n")
    
    for test_file, test_name in test_files:
        print(f"Running {BOLD}{test_name}{RESET}...", end=" ", flush=True)
        success, output = run_test_file(test_file)
        
        if success:
            print_success(test_name)
            passed_tests += 1
        else:
            print_failure(test_name, None)
            # Print detailed error if verbose
            if "--verbose" in sys.argv or "-v" in sys.argv:
                print(f"\n{output}\n")
        
        results.append((test_name, success, output))
    
    # Print summary
    print_header("Test Summary")
    
    print(f"Total test suites: {total_tests}")
    print(f"{GREEN}Passed: {passed_tests}{RESET}")
    print(f"{RED}Failed: {total_tests - passed_tests}{RESET}")
    
    if passed_tests == total_tests:
        print(f"\n{BOLD}{GREEN}All tests passed! [SUCCESS]{RESET}\n")
        return 0
    else:
        print(f"\n{BOLD}{RED}Some tests failed. Please review the output above.{RESET}\n")
        
        # Print failed test details
        print(f"{BOLD}Failed Tests:{RESET}")
        for test_name, success, output in results:
            if not success:
                print(f"  {RED}[FAIL] {test_name}{RESET}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())

