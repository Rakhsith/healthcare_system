import os
import shutil
root = os.path.abspath(os.path.dirname(__file__)+'..')
removed = []
for name in ['.venv', '.venv-1']:
    path = os.path.join(root, name)
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            removed.append(name)
        except Exception as e:
            print(f"Failed to remove {path}: {e}")
    else:
        # also try without leading dot
        alt = os.path.join(root, name.lstrip('.'))
        if os.path.exists(alt):
            try:
                shutil.rmtree(alt)
                removed.append(os.path.basename(alt))
            except Exception as e:
                print(f"Failed to remove {alt}: {e}")

if removed:
    print("Removed:", ", ".join(removed))
else:
    print("No extra venvs found")
