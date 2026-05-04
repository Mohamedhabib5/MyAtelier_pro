#!/bin/bash
# MyAtelier Pro - Security Scanning Script

echo "--- Running Bandit (Static Analysis for Security) ---"
bandit -r app/ -ll

echo ""
echo "--- Running Safety (Dependency Vulnerability Check) ---"
safety check -r requirements.txt

echo ""
echo "--- Running Flake8 (Linting & Best Practices) ---"
flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
