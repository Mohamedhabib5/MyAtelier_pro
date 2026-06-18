import os
import re

core_security_path = "/home/mohamed/MyAtelier_pro/backend/app/core/security.py"
service_path = "/home/mohamed/MyAtelier_pro/backend/app/modules/core_platform/security_service.py"

with open(core_security_path, "r", encoding="utf-8") as f:
    core_content = f.read()

with open(service_path, "r", encoding="utf-8") as f:
    service_content = f.read()

# Remove the import __future__ annotations and get imports + content
lines = service_content.split('\n')
clean_lines = [line for line in lines if not line.startswith("from __future__")]

to_append = '\n'.join(clean_lines)

# Append to core/security.py
with open(core_security_path, "a", encoding="utf-8") as f:
    f.write("\n" + to_append)

# Delete service_path
os.remove(service_path)

# Update imports in the whole backend
def update_imports(dir_path):
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                new_content = content.replace(
                    "app.modules.core_platform.security_service",
                    "app.core.security"
                )
                
                if new_content != content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)

update_imports("/home/mohamed/MyAtelier_pro/backend/app")
update_imports("/home/mohamed/MyAtelier_pro/backend/tests")

print("Merge and replace completed.")
