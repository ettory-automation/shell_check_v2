from rich.console import Console
from rich.table import Table
import subprocess
import os
from time import sleep
import re

console = Console()
COLORS = ['green', 'red', 'purple']

def get_block_size(disk_sel):
    try:
        return int(subprocess.check_output(
            ['blockdev', '--getbsz', disk_sel],
            stderr=subprocess.DEVNULL
        ).strip())
    except subprocess.CalledProcessError:
        try:
            path = f"/sys/block/{os.path.basename(disk_sel)}/queue/logical_block_size"
            with open(path) as f:
                return int(f.read().strip())
        except Exception:
            return 512


def select_disk():
    while True:
        os.system("clear")

        result = subprocess.run(['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')

        table = Table(
            show_header=True,
            header_style=COLORS[2],
            title="Available Disks",
            title_style=COLORS[2],
            title_justify='center'
        )
        
        table.add_column("NAME", justify="left")
        table.add_column("SIZE", justify="right")
        table.add_column("TYPE", justify="left")
        table.add_column("MOUNTPOINT", justify="left")

        disks = []
        for line in lines[1:]:
            parts = line.split()
            name = parts[0]
            size = parts[1]
            typ = parts[2]
            mount = parts[3] if len(parts) > 3 else "-"
            table.add_row(name, size, typ, mount)
            if typ == "disk":
                disks.append(name)

        console.print()
        console.print()
        console.print(table)

        console.print()
        disk_sel = console.input(f"[{COLORS[2]}]Select disk (just name, e.g., sda):[/{COLORS[2]}] ").strip()
        if disk_sel not in disks:
            console.print()
            console.print(f"Invalid or non-existent disk: {disk_sel}", style=COLORS[1])
            sleep(2)
            console.print()
            choice = console.input(f"[{COLORS[2]}]Return to menu? (y/n):[/{COLORS[2]}] ").strip().lower()
            if choice == "y":
                return None
            continue

        return f"/dev/{disk_sel}"

def get_io_details(disk_sel):
    disk_name = os.path.basename(disk_sel)
    result = subprocess.run(['vmstat', '1', '5'], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')

    table = Table(
        show_header=True,
        header_style=COLORS[2],
        title=f"I/O Blocks {disk_name}",
        title_style=COLORS[2],
        title_justify='center'
    )
    table.add_column("In Blocks", justify="right")
    table.add_column("Out Blocks", justify="right")

    for line in lines[2:]:
        parts = line.split()
        if len(parts) >= 10:
            in_blocks = parts[8]
            out_blocks = parts[9]
            table.add_row(in_blocks, out_blocks)

    console.print()
    console.print()
    console.print(table)


def set_io_limit():
    console.print()
    console.print()

    input_val = console.input(f"[{COLORS[2]}]I/O Limit (e.g., 1G, 1M, 1K or bytes):[/{COLORS[2]}] ").strip().lower()
    
    match = re.match(r"^(\d+)([kmg]?)$", input_val)
    
    if not match:
        console.print(f"[{COLORS[1]}]Invalid value. Use numeric format with optional K, M, or G.[/{COLORS[1]}]")
        sleep(2)
        return None

    num, unit = match.groups()
    num = int(num)
    unit_multiplier = {'k': 1024, 'm': 1024*1024, 'g': 1024*1024*1024, '': 1}
    return num * unit_multiplier[unit]

def check_io_results(disk_sel, limit_bytes):
    block_size = get_block_size(disk_sel)
    limit_blocks = limit_bytes // block_size

    result = subprocess.run(['vmstat', '1', '5'], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    alert = False

    for line in lines[2:]:
        parts = line.split()
        if len(parts) >= 10:
            if int(parts[8]) > limit_blocks or int(parts[9]) > limit_blocks:
                alert = True
                break

    if alert:
        console.print(f"\nALERT: High I/O detected on disk {disk_sel}!", style=COLORS[1])
    else:
        console.print(f"\nI/O within normal range for {disk_sel}.", style=COLORS[0])

def disk_iops_check():
    disk_sel = select_disk()
    if not disk_sel:
        return

    get_io_details(disk_sel)

    limit_bytes = set_io_limit()
    if limit_bytes is None:
        return

    check_io_results(disk_sel, limit_bytes)

    console.print("\nPress ENTER to return to the menu...")
    input()
