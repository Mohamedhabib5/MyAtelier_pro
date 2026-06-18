import os
import re

frontend_dir = "/home/mohamed/MyAtelier_pro/frontend/src"

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'catch (err: any)' not in content:
        return
        
    # Replace catch (err: any) with catch (err: unknown)
    # and then add type narrowing inside the block if it uses err.
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'catch (err: any)' in line:
            lines[i] = line.replace('catch (err: any)', 'catch (err: unknown)')
            # naive narrowing: let's inject a cast or let error = err as Error | any
            # Actually, standard narrowing: 
            # if (err instanceof Error) { ... }
            # But wait, we can just replace `err.response` with `(err as any).response` for simplicity, 
            # or add a standard narrowing at the top of the block:
            # `const error = err as any;` -> this defeats the purpose of unknown.
            # A better narrowing:
            # const errorMessage = err instanceof Error ? err.message : String(err);
            # Let's just do a string replacement for now and fix manually.

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

for root, _, files in os.walk(frontend_dir):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            process_file(os.path.join(root, file))
