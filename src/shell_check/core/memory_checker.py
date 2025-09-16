from rich.console import Console
from rich.table import Table
import subprocess
import os

COLOR = 'purple'
console = Console()

def get_memory_primary_data():
    result = subprocess.run(['free', '-h'], capture_output=True, text=True)

    lines = result.stdout.strip().split('\n')
    _, *rows = lines

    table = Table(show_header=True, header_style=COLOR, title="Total Memory and Usage (Partial)", title_justify='center', title_style=COLOR)
    table.add_column('Total')
    table.add_column('Used')
    table.add_column('Free')
    table.add_column('Shared')
    table.add_column('Buff/Cache')
    table.add_column('Available')

    for row in rows:
        parts = row.split()
        if row.startswith("Mem:"):
            table.add_row(parts[1], parts[2], parts[3], parts[4], parts[5], parts[6])

    table2 = Table(show_header=True, header_style=COLOR, title="Total Swap and Usage (Partial)", title_justify='center', title_style=COLOR)
    table2.add_column('Total')
    table2.add_column('Used')
    table2.add_column('Free')

    for row in rows:
        parts = row.split()
        if row.startswith("Swap:"):
            table2.add_row(parts[1], parts[2], parts[3])

    console.print(table)
    console.print()
    console.print()
    console.print(table2)

def top_process_consumption():
    ps = subprocess.Popen(
        ['ps', '-eo', 'pid,ppid,comm,%mem', '--sort=-%mem'],
        stdout=subprocess.PIPE, text=True
    )
    head = subprocess.Popen(['head', '-n', '11'], stdin=ps.stdout, stdout=subprocess.PIPE, text=True)
    ps.stdout.close()
    output, _ = head.communicate()
    
    lines = output.strip().split('\n')
    _, *rows = lines

    table = Table(
        show_header=True,
        header_style=COLOR,
        title="Top 10 Memory Consuming Processes",
        title_style=COLOR,
        title_justify='center'
    )

    table.add_column("PID", justify='right')
    table.add_column("PPID", justify='right')
    table.add_column("Command", justify='left')
    table.add_column("%MEM", justify='right')

    for row in rows:
        parts = row.split(None, 3)
        table.add_row(*parts)

    console.print()
    console.print()
    console.print(table)

def get_memory_details():
    top = subprocess.Popen(['top', '-b', '-n', '1'], stdout=subprocess.PIPE, text=True)
    grep = subprocess.Popen(['grep', '-Ei', 'mem|swap'], stdin=top.stdout, stdout=subprocess.PIPE, text=True)
    top.stdout.close()
    output, _ = grep.communicate()

    lines = output.strip().split('\n')

    table = Table(
        show_header=True,
        header_style=COLOR,
        title="Memory and Swap Details (Real-Time)",
        title_style=COLOR,
        title_justify='center'
    )
    table.add_column("Type", justify="left")
    table.add_column("Total", justify="right")
    table.add_column("Used", justify="right")
    table.add_column("Free", justify="right")
    table.add_column("Shared", justify="right")
    table.add_column("Buffers/Cached", justify="right")

    for line in lines:
        line_lower = line.lower()

        if ':' not in line:
            continue

        if 'mem' in line_lower and 'swap' not in line_lower:
            parts = line.split(':', 1)[1].split(',')
            total = parts[0].strip().split()[0]
            free = parts[1].strip().split()[0]
            used = parts[2].strip().split()[0]
            buff_cache = parts[3].strip().split()[0]
            shared = '-'
            table.add_row("Memory", total, used, free, shared, buff_cache)
        elif 'swap' in line_lower:
            parts = line.split(':', 1)[1].split(',')
            total = parts[0].strip().split()[0]
            free = parts[1].strip().split()[0]
            used = parts[2].strip().split()[0]
            table.add_row("Swap", total, used, free, "-", "-")

    console.print("\n\n")
    console.print(table)
    
def memory_check():
    os.system('clear')
    get_memory_primary_data()
    top_process_consumption()
    get_memory_details()
    console.print('\n\nPress ENTER to return to the menu...', style=COLOR)
    input()
