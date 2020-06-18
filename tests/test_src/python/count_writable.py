"""
This test counts the number of writable files in all the subdirectories
"""
import os

## This is used for pruning, 
exit_after = int(input())
total_writable_files = 0
total_writable_dirs = 0
paths = []


for r, d, f in os.walk("/"):
    for dd in d:
        dir_path = os.path.join(r, dd)
        if os.access(dir_path, os.W_OK):
            total_writable_dirs += 1
            paths.append(dir_path)

    for ff in f:
        file_path = os.path.join(r, ff)
        if os.access(file_path, os.W_OK):
            # skip dev
            if file_path in ["/dev/null", "/dev/random"]:
                continue
            total_writable_files += 1
            paths.append(file_path)


print(total_writable_dirs)
print(total_writable_files)
