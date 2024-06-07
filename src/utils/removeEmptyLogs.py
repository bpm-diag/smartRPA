# ****************************** #
# remove empy logs
# Not used by any module, just a command line utility to remove logs with less than N lines.
# ****************************** #

import glob
import os
import sys


# Remove log files with less than N lines
def removeEmptyLogs(N=10):
    count = 0
    for file in glob.glob('../logs/*.csv'):
        try:
            lines = open(file).readlines()
            if len(lines) < N:
                print(f"Removing {file}")
                os.remove(file)
                count += 1
        except Exception:
            continue
    print(f"Removed {count} files")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        removeEmptyLogs(int(sys.argv[1]))
    else:
        print("USAGE: python3 removeEmptyLogs.py N - files with less than N lines are removed")
