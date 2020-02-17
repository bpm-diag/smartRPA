import glob
import os

# Remove log files with less than N lines
def removeEmptyLogs(N=3):
    count = 0
    for file in glob.glob('../logs/*.csv'):
        try:
            lines = open(file).readlines()
            if len(lines) < N:
                print(f"Removing {file}")
                os.remove(file)
                count += 1
            # open(file, 'w').writelines(lines[3:])
        except Exception as e:
            continue
    print(f"Removed {count} files")

removeEmptyLogs()