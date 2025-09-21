from rich.console import Console
from rich.table import Table
from pathlib import Path
from time import sleep
from fabric import Connection
import os

COLOR = ['purple', 'green', 'red', 'yellow']
console = Console()

INFO = COLOR[0]
SUCCESS = COLOR[1]
ERROR = COLOR[2]
WARNING = COLOR[3]


def select_directory(conn):
    while True:
        console.print()
        console.print('Select directory or path: ', style=INFO, end='')
        input_directory_selection = input()
        console.print()

        result = conn.run(f'test -d "{input_directory_selection}"', warn=True)
        if result.exited != 0:
            console.print('This path does not exist or is not valid on the remote host!', style=ERROR)
            
            while True:
                console.print()
                console.print("Back to menu? (y/n) ", style=INFO, end='')
                choice = input().strip().lower()
                if choice in ('y', 'n'):
                    break
                console.print('\nInvalid input! Please type "y" or "n".\n', style=ERROR)

            if choice == 'y':
                return None
        else:
            return input_directory_selection



def get_dir_analysis(conn: Connection, directory: Path):
    if not directory:
        return
    
    result = conn.run(f'df -h --output=source,iavail,ipcent,itotal {directory}', hide=True)
    lines = result.stdout.strip().split('\n')
    _, *rows = lines

    table = Table(
        show_header=True,
        header_style=INFO,
        title="Inodes Consumption",
        title_justify='center',
        title_style=INFO
    )
    
    table.add_column('Diskpath', width=40)
    table.add_column("Inode Available", width=20)
    table.add_column("Inode(%)", width=10)
    table.add_column("Inode(Total)", width=14)

    for row in rows:
        parts = row.split()[:4]
        inode_percent = int(parts[2].replace('%',''))

        if inode_percent <= 50:
            color = SUCCESS
        elif inode_percent <= 80:
            color = WARNING
        else:
            color = ERROR

        table.add_row(parts[0], parts[1], f'[{color}]{parts[2]}[/{color}]', parts[3])

    console.print(table)


def get_dir_details(conn: Connection, directory: Path):
    if not directory:
        return

    cmd = (
        f"find {directory} -xdev -type d -mindepth 0 -maxdepth 5 -print0 "
        f"| grep -vzE '/proc|/sys|/dev|/run|/var/lib/docker|/snap|/tmp' "
        f"| xargs -0 -P {os.cpu_count()} -n 10 du -sh "
        f"| sort -hr | head -n 15"
    )
    result = conn.run(cmd, hide=True, warn=True)
    lines = result.stdout.strip().split('\n')

    console.print()

    table = Table(
        show_header=True,
        header_style=INFO,
        title="TOP 15 Directories Most Used",
        title_justify='center',
        title_style=INFO
    )

    table.add_column('Size')
    table.add_column('Directory')

    for line in lines:
        if not line.strip():
            continue

        size, path = line.split(maxsplit=1)
        table.add_row(size, path)

    console.print(table)


def disk_check(conn: Connection):
    directory = select_directory(conn)
    if not directory:
        return
    
    get_dir_analysis(conn, directory)
    get_dir_details(conn, directory)
    console.print('\n\nPress ENTER to return to the menu...', style=INFO)
    input()
