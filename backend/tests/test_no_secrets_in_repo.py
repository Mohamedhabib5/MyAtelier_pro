import subprocess
import pytest

@pytest.mark.guardrail
def test_no_sensitive_files_in_git():
    """Regression test for C1: لا يجب أن توجد ملفات حساسة في الفهرس."""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True, text=True, check=True
    )
    files = result.stdout.strip().split("\n")
    forbidden_patterns = [".sql", ".db", ".sqlite", ".bak", ".env", "all_files.txt"]
    violations = []
    for f in files:
        for pat in forbidden_patterns:
            if f.endswith(pat) or f == pat.lstrip(".") or pat in f:
                # استثناءات صريحة
                if f.endswith(".env.example") or f.endswith(".env.prod.example"):
                    continue
                if "migrations" in f and f.endswith(".sql"):
                    continue
                violations.append(f)
    assert not violations, f"Sensitive files found in git: {violations}"
