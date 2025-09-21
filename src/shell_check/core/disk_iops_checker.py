from rich.console import Console
from rich.table import Table
import os
import re
from time import sleep
from fabric import Connection

console = Console()
COLORS = ['green', 'red', 'purple']

INFO = COLORS[0]
ERROR = COLORS[1]
TITLE = COLORS[2]


def get_block_size(conn: Connection, disk_sel: str):
    try:
        result = conn.run(f'blockdev --getbsz {disk_sel}', hide=True, warn=True)
        if result.ok:
            return int(result.stdout.strip())
    except Exception:
        pass

    try:
        disk_name = os.path.basename(disk_sel)
        path = f"/sys/block/{disk_name}/queue/logical_block_size"
        result = conn.run(f'cat {path}', hide=True, warn=True)
        if result.ok:
            return int(result.stdout.strip())
    except Exception:
        pass

    return 512


def select_disk(conn: Connection):
    while True:
        conn.run('TERM=xterm clear', warn=True)
        result = conn.run('lsblk -o NAME,SIZE,TYPE,MOUNTPOINT', hide=True)
        lines = result.stdout.strip().split('\n')
        disks = []

        table = Table(
            show_header=True,
            header_style=TITLE,
            title="Available Disks",
            title_style=TITLE,
            title_justify='center'
        )
        table.add_column("NAME", justify="left")
        table.add_column("SIZE", justify="right")
        table.add_column("TYPE", justify="left")
        table.add_column("MOUNTPOINT", justify="left")

        for line in lines[1:]:
            parts = line.split()
            name, size, typ = parts[:3]
            mount = parts[3] if len(parts) > 3 else "-"
            table.add_row(name, size, typ, mount)
            if typ == "disk":
                disks.append(name)

        console.print(table)
        console.print()
        disk_sel = console.input(f"[{TITLE}]Select disk (just name, e.g., sda):[/{TITLE}] ").strip()
        console.print()
        if disk_sel not in disks:
            console.print(f"Invalid or non-existent disk: {disk_sel}", style=ERROR)
            sleep(2)
            choice = console.input(f"[{TITLE}]Return to menu? (y/n):[/{TITLE}] ").strip().lower()
            if choice == "y":
                return None
            else:
                continue
        return f"/dev/{disk_sel}"


def get_io_details(conn: Connection, disk_sel: str):
    disk_name = os.path.basename(disk_sel)
    result = conn.run('vmstat 1 5', hide=True)
    lines = result.stdout.strip().split('\n')

    table = Table(
        show_header=True,
        header_style=TITLE,
        title=f"I/O Blocks {disk_name}",
        title_style=TITLE,
        title_justify='center'
    )
    table.add_column("In Blocks", justify="right")
    table.add_column("Out Blocks", justify="right")

    for line in lines[2:]:
        parts = line.split()
        if len(parts) >= 10:
            table.add_row(parts[8], parts[9])

    console.print(table)


def set_io_limit():
    console.print()
    input_val = console.input(f"[{TITLE}]I/O Limit (e.g., 1G, 1M, 1K or bytes):[/{TITLE}] ").strip().lower()
    match = re.match(r"^(\d+)([kmg]?)$", input_val)
    if not match:
        console.print(f"[{ERROR}]Invalid value. Use numeric format with optional K, M, or G.[/{ERROR}]")
        sleep(2)
        return None

    num, unit = match.groups()
    num = int(num)
    unit_multiplier = {'k': 1024, 'm': 1024*1024, 'g': 1024*1024*1024, '': 1}
    return num * unit_multiplier[unit]


def check_io_results(conn: Connection, disk_sel: str, limit_bytes: int):
    block_size = get_block_size(conn, disk_sel)
    limit_blocks = limit_bytes // block_size

    result = conn.run('vmstat 1 5', hide=True)
    lines = result.stdout.strip().split('\n')
    alert = False

    for line in lines[2:]:
        parts = line.split()
        if len(parts) >= 10:
            if int(parts[8]) > limit_blocks or int(parts[9]) > limit_blocks:
                alert = True
                break

    if alert:
        console.print(f"\nALERT: High I/O detected on disk {disk_sel}!", style=ERROR)
    else:
        console.print(f"\nI/O within normal range for {disk_sel}.", style=INFO)


def disk_iops_check(conn: Connection):
    disk_sel = select_disk(conn)
    if not disk_sel:
        return

    get_io_details(conn, disk_sel)
    limit_bytes = set_io_limit()
    if limit_bytes is None:
        return

    check_io_results(conn, disk_sel, limit_bytes)

    console.print("\nPress ENTER to return to the menu...", style=TITLE)
    input()
