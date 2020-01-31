import psutil
from datetime import datetime
import pandas as pd

# the list the contain all process dictionaries
processes = []
for process in psutil.process_iter():
    with process.oneshot():
        pid = process.pid
        name = process.name()
        create_time = datetime.fromtimestamp(process.create_time())
        status = process.status()
        try:
            username = process.username()
        except psutil.AccessDenied:
            username = "N/A"
    processes.append({
        'pid': pid, 'name': name, 'create_time': create_time, 'username': username, 'status':status
    })

# convert to pandas dataframe
df = pd.DataFrame(processes)
# set the process id as index of a process
df.set_index('pid', inplace=True)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Process Viewer & Monitor")
    parser.add_argument("-c", "--columns", help="""Columns to show,
                                                available are name,create_time,cores,cpu_usage,status,nice,memory_usage,read_bytes,write_bytes,n_threads,username.
                                                Default is name,cpu_usage,memory_usage,read_bytes,write_bytes,status,create_time,nice,n_threads,cores.""",
                        default="name,status,create_time,username")
    parser.add_argument("-s", "--sort-by", dest="sort_by", help="Column to sort by, default is create_time .", default="pid")
    parser.add_argument("--descending", action="store_true", help="Whether to sort in descending order.")
    parser.add_argument("-n", help="Number of processes to show, will show all if 0 is specified, default is 25 .", default=25)

    # parse arguments
    args = parser.parse_args()
    columns = args.columns
    sort_by = args.sort_by
    descending = args.descending
    n = int(args.n)

    # sort rows by the column passed as argument
    df.sort_values(sort_by, inplace=True, ascending=not descending)
    # convert to proper date format
    df['create_time'] = df['create_time'].apply(datetime.strftime, args=("%Y-%m-%d %H:%M:%S",))
    # reorder and define used columns
    df = df[columns.split(",")]
    # print
    if n == 0:
        print(df.to_string())
    elif n > 0:
        print(df.head(n).to_string())