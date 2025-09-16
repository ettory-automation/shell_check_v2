from rich.console import Console
from rich.table import Table
from rich.text import Text
import subprocess
from time import sleep
import os

console = Console()
COLORS = ['green', 'red', 'yellow', 'purple']

def get_cpu_consumption(threshold_high=70, threshold_warn=50):
    result = subprocess.run(['ps', '-eo', 'pid,%cpu,comm', '--sort=-%cpu'], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    _ = lines[0]
    data = lines[1:]

    table = Table(show_header=True, header_style=COLORS[3], title="CPU Usage Processes", title_style=COLORS[3], title_justify='center')
    table.add_column("PID", justify="right")
    table.add_column("%CPU", justify="right")
    table.add_column("Command", justify="left")

    if not data:
        table.add_row("-", "-", "No processes found")
        console.print(table)
        return

    for line in data:
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        pid, cpu_str, comm = parts
        cpu = float(cpu_str)

        if cpu >= threshold_high:
            cpu_text = Text(cpu_str, style=COLORS[1])
        elif cpu >= threshold_warn:
            cpu_text = Text(cpu_str, style=COLORS[2])
        else:
            cpu_text = Text(cpu_str, style=COLORS[0])

        table.add_row(pid, cpu_text, comm)

    console.print()
    console.print()
    console.print(table)

def get_consumption_per_core(interval=3):

    cores = os.cpu_count()

    def read_cpu_stats():
        with open("/proc/stat") as f:
            return [line for line in f if line.startswith("cpu")]

    prev_stats = read_cpu_stats()
    sleep(interval)
    current_stats = read_cpu_stats()

    table = Table(show_header=True, header_style=COLORS[3], title="CPU Usage per Core", title_style=COLORS[3], title_justify='center')
    table.add_column("Core", justify="left")
    table.add_column("%User", justify="right")
    table.add_column("%System", justify="right")
    table.add_column("%Idle", justify="right")
    table.add_column("%Total Active", justify="right")

    for i in range(1, cores + 1):
        prev = list(map(int, prev_stats[i].split()[1:8]))
        curr = list(map(int, current_stats[i].split()[1:8]))

        deltas = [c - p for c, p in zip(curr, prev)]
        total = sum(deltas)
        if total == 0:
            total = 1

        user_perc = deltas[0] / total * 100
        system_perc = deltas[2] / total * 100
        idle_perc = deltas[3] / total * 100
        total_active = 100 - idle_perc

        if total_active >= 70:
            color = COLORS[1]
        elif total_active >= 50:
            color = COLORS[2]
        else:
            color = COLORS[0]

        table.add_row(f"cpu{i-1}", f"{user_perc:.2f}", f"{system_perc:.2f}", f"{idle_perc:.2f}", Text(f"{total_active:.2f}", style=color))

    console.print()
    console.print()
    console.print(table)


def get_load_average():
    cores = os.cpu_count()
    with open("/proc/loadavg") as f:
        load1, load5, load15, *_ = map(float, f.read().split()[:3])

    table = Table(show_header=True, header_style=COLORS[3], title="Load Average", title_style=COLORS[3], title_justify='center')
    table.add_column("1min", justify="right")
    table.add_column("5min", justify="right")
    table.add_column("15min", justify="right")
    table.add_column("Alert", justify="left")

    if load1 > cores:
        alert = Text("CRITICAL", style=COLORS[1])
    elif load1 > cores * 0.7:
        alert = Text("WARNING", style=COLORS[2])
    else:
        alert = Text("OK", style=COLORS[0])

    table.add_row(f"{load1:.2f}", f"{load5:.2f}", f"{load15:.2f}", alert)

    console.print()
    console.print()
    console.print(table)


def cpu_check():
    get_cpu_consumption()
    get_consumption_per_core()
    get_load_average()

    console.print("\nPress ENTER to return to menu...", style=COLORS[0])
    input()