import subprocess
import os
from pathlib import Path

def test_source_code_text_integrity():
    """
    Runs the frontend/scripts/check-text-integrity.mjs script to verify
    that no Arabic text corruption (???, mojibake) has been introduced
    into the source code.
    """
    # Calculate path to the script relative to this test file
    # tests/test_text_integrity.py -> ../../frontend/scripts/check-text-integrity.mjs
    root_dir = Path(__file__).parent.parent.parent
    script_path = root_dir / "frontend" / "scripts" / "check-text-integrity.mjs"
    
    if not script_path.exists():
        # Fallback to absolute path if relative fails in some envs
        script_path = Path("d:/Programing project/MyAtelier_pro/frontend/scripts/check-text-integrity.mjs")

    assert script_path.exists(), f"Integrity script not found at {script_path}"

    # Run the script using node
    result = subprocess.run(
        ["node", str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(root_dir / "frontend")
    )

    # Assert that the script passed
    assert result.returncode == 0, f"Text integrity check failed:\n{result.stderr}\n{result.stdout}"
