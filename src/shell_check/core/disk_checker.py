from rich.console import Console
from rich.table import Table
from pathlib import Path
import subprocess
import os
from time import sleep

COLOR = ['purple', 'green', 'red', 'yellow']
console = Console()

INFO = COLOR[0]
SUCCESS = COLOR[1]
ERROR = COLOR[2]
WARNING = COLOR[3]


def select_directory():
    while True:
        console.print()
        console.print('Select directory or path: ', style=INFO, end='')
        input_directory_selection = input()
        console.print()

        if Path(input_directory_selection).exists() == False:
            console.print('This path not exists or not valid!', style=ERROR)
        
            while True:
                console.print()
                console.print("Back to menu? (y/n) ", style=INFO, end='')
                choice = input()
                
                choice = choice.lower()

                if choice == 'y':
                    return None
                elif choice == 'n':
                    break
                else:
                    console.print('\nInvalid option. Trying again...\n', style=ERROR)
                    sleep(1)
        else:
            return Path(input_directory_selection)
    
def get_dir_analysis(directory):
    if not directory:
        return
    
    result = subprocess.run(['df', '-h', '--output=source,iavail,ipcent,itotal', str(directory)], capture_output=True, text=True)

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

def get_dir_details(directory):
    if not directory:
        return

    find = [
        'find', str(directory), '-xdev', '-type', 'd',
        '-mindepth', '0', '-maxdepth', '5', '-print0'
    ]

    exclude_find = [
        'grep', '-vzE', '/proc|/sys|/dev|/run|/var/lib/docker|/snap|/tmp'
    ]

    xargs = ['xargs', '-0', '-P', str(os.cpu_count()), '-n', '10', 'du', '-sh']
    sort = ['sort', '-hr']
    head = ['head', '-n', '15']

    find_proc = subprocess.Popen(find, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    exclude_proc = subprocess.Popen(exclude_find, stdin=find_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
    xargs_proc = subprocess.Popen(xargs, stdin=exclude_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    exclude_proc.stdout.close()

    sort_proc = subprocess.Popen(sort, stdin=xargs_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    xargs_proc.stdout.close()

    head_proc = subprocess.Popen(head, stdin=sort_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    sort_proc.stdout.close()

    output, _ = head_proc.communicate()
    lines = output.decode().strip().split('\n')

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

def disk_check():
    directory = select_directory()

    if not directory:
        return
    
    get_dir_analysis(directory)
    get_dir_details(directory)
    console.print('\n\nPress ENTER to return to the menu', style=INFO)
    input()
