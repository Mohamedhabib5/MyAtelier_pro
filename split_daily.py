import ast
import sys

source_file = "backend/app/modules/exports/daily_report_service.py"
with open(source_file, "r", encoding="utf-8") as f:
    source_code = f.read()

tree = ast.parse(source_code)

header_lines = []
funcs = {}
# To preserve the exact source code of each function, we can use ast.get_source_segment
import tokenize
import io

lines = source_code.split('\n')

for node in tree.body:
    if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign)):
        # Collect imports and logger
        start = node.lineno - 1
        end = node.end_lineno
        header_lines.extend(lines[start:end])
    elif isinstance(node, ast.FunctionDef):
        start = node.lineno - 1
        # Extract decorator if any (there are no decorators here but just in case)
        if node.decorator_list:
            start = node.decorator_list[0].lineno - 1
        end = node.end_lineno
        funcs[node.name] = '\n'.join(lines[start:end])

header = '\n'.join(header_lines)

# Distribute
files_map = {
    "daily_report_templates.py": ["generate_daily_report_html"],
    "daily_report_runner.py": ["send_email_report", "run_test_report_for_config"],
    "daily_report_config.py": ["list_daily_report_configs", "create_daily_report_config", "update_daily_report_config", "delete_daily_report_config"],
    "daily_report_scheduler.py": ["check_and_run_due_reports"],
}

import os
base_dir = "backend/app/modules/exports"

# Note: check_and_run_due_reports calls send_daily_operations_digest and verify_chain_integrity, but those are internal imports.
# It also needs send_email_report and generate_daily_report_html if it was generating it, but actually run_test_report_for_config uses them.
# We will inject local imports or just add them to the header.
# run_test_report_for_config needs generate_daily_report_html and send_email_report.
# Let's just modify the header to include cross imports if needed, or better, we can just write them as is, and let flake8/imports work.

for fname, fnames in files_map.items():
    content = header + "\n\n"
    # Additional imports for cross-file usage
    if fname == "daily_report_runner.py":
        content += "from app.modules.exports.daily_report_templates import generate_daily_report_html\n\n"
    if fname == "daily_report_scheduler.py":
        pass # It imports from daily_report_service currently, but we will redirect to daily_report_runner inside the function if needed, wait, the original function check_and_run_due_reports calls `generate_daily_report_html` and `send_email_report`.
        content += "from app.modules.exports.daily_report_templates import generate_daily_report_html\n"
        content += "from app.modules.exports.daily_report_runner import send_email_report\n\n"
        
    for name in fnames:
        if name in funcs:
            content += funcs[name] + "\n\n"
    
    with open(os.path.join(base_dir, fname), "w", encoding="utf-8") as f:
        f.write(content)

# Now overwrite daily_report_service.py to be an aggregator
aggregator = """from .daily_report_runner import send_email_report, run_test_report_for_config
from .daily_report_templates import generate_daily_report_html
from .daily_report_config import list_daily_report_configs, create_daily_report_config, update_daily_report_config, delete_daily_report_config
from .daily_report_scheduler import check_and_run_due_reports
"""
with open(source_file, "w", encoding="utf-8") as f:
    f.write(aggregator)

print("Split successful")
