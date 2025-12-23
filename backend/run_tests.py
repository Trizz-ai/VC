#!/usr/bin/env python3
"""
Comprehensive test runner for Verified Compliance Backend
Achieves 95%+ code coverage across all modules
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}")
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
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False


def check_coverage():
    """Check if coverage meets 95%+ requirement"""
    print("\n📊 Checking Coverage Requirements")
    print("=" * 50)
    
    # Run coverage analysis
    coverage_cmd = "pytest --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=95"
    
    success = run_command(coverage_cmd, "Running tests with 95%+ coverage requirement")
    
    if success:
        print("\n✅ Coverage requirement met: 95%+")
        return True
    else:
        print("\n❌ Coverage requirement not met: <95%")
        return False


def run_unit_tests():
    """Run all unit tests"""
    print("\n🧪 Running Unit Tests")
    print("=" * 50)
    
    test_commands = [
        ("pytest tests/test_core_*.py -v", "Core module tests"),
        ("pytest tests/test_models_*.py -v", "Model tests"),
        ("pytest tests/test_services_*.py -v", "Service tests"),
        ("pytest tests/test_api_*.py -v", "API integration tests"),
    ]
    
    all_success = True
    for cmd, desc in test_commands:
        success = run_command(cmd, desc)
        if not success:
            all_success = False
    
    return all_success


def run_specific_tests(test_pattern):
    """Run specific test pattern"""
    print(f"\n🎯 Running Specific Tests: {test_pattern}")
    print("=" * 50)
    
    cmd = f"pytest {test_pattern} -v"
    return run_command(cmd, f"Running {test_pattern}")


def generate_coverage_report():
    """Generate detailed coverage report"""
    print("\n📈 Generating Coverage Report")
    print("=" * 50)
    
    commands = [
        ("pytest --cov=app --cov-report=html", "Generate HTML coverage report"),
        ("pytest --cov=app --cov-report=xml", "Generate XML coverage report"),
        ("pytest --cov=app --cov-report=json", "Generate JSON coverage report"),
    ]
    
    all_success = True
    for cmd, desc in commands:
        success = run_command(cmd, desc)
        if not success:
            all_success = False
    
    return all_success


def run_performance_tests():
    """Run performance tests"""
    print("\n⚡ Running Performance Tests")
    print("=" * 50)
    
    perf_cmd = "pytest tests/test_performance_*.py -v --durations=10"
    return run_command(perf_cmd, "Performance tests")


def run_security_tests():
    """Run security tests"""
    print("\n🔒 Running Security Tests")
    print("=" * 50)
    
    security_cmd = "pytest tests/test_security_*.py -v"
    return run_command(security_cmd, "Security tests")


def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests")
    print("=" * 50)
    
    integration_cmd = "pytest tests/test_integration_*.py -v"
    return run_command(integration_cmd, "Integration tests")


def run_all_tests():
    """Run all test suites"""
    print("\n🚀 Running All Test Suites")
    print("=" * 50)
    
    test_suites = [
        ("Unit Tests", run_unit_tests),
        ("Integration Tests", run_integration_tests),
        ("Performance Tests", run_performance_tests),
        ("Security Tests", run_security_tests),
        ("Coverage Validation", check_coverage),
    ]
    
    results = {}
    for suite_name, suite_func in test_suites:
        print(f"\n📋 {suite_name}")
        print("-" * 30)
        results[suite_name] = suite_func()
    
    return results


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Verified Compliance Backend Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--coverage", action="store_true", help="Check coverage only")
    parser.add_argument("--report", action="store_true", help="Generate coverage report only")
    parser.add_argument("--pattern", type=str, help="Run specific test pattern")
    parser.add_argument("--all", action="store_true", help="Run all test suites")
    
    args = parser.parse_args()
    
    print("🧪 Verified Compliance Backend Test Suite")
    print("=" * 50)
    print("Target: 95%+ Code Coverage")
    print("Framework: pytest + pytest-asyncio")
    print("Coverage: pytest-cov")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    success = True
    
    if args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.performance:
        success = run_performance_tests()
    elif args.security:
        success = run_security_tests()
    elif args.coverage:
        success = check_coverage()
    elif args.report:
        success = generate_coverage_report()
    elif args.pattern:
        success = run_specific_tests(args.pattern)
    elif args.all:
        results = run_all_tests()
        success = all(results.values())
        
        # Print summary
        print("\n📊 Test Results Summary")
        print("=" * 50)
        for suite_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{suite_name}: {status}")
        
        overall_success = all(results.values())
        print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    else:
        # Default: run unit tests with coverage
        success = run_unit_tests() and check_coverage()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("✅ 95%+ code coverage achieved")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        print("❌ Coverage requirement not met")
        sys.exit(1)


if __name__ == "__main__":
    main()