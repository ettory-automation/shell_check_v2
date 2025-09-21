from rich.console import Console
from rich.table import Table
from fabric import Connection
import os

console = Console()
COLORS = ['green', 'red', 'purple']

INFO = COLORS[2]
SUCCESS = COLORS[0]
ERROR = COLORS[1]


def detect_distro(conn: Connection):
    res = conn.run('test -f /etc/debian_version && echo debian || true', hide=True, warn=True)
    if res.stdout.strip() == "debian":
        return "debian"
    res = conn.run('test -f /etc/redhat-release && echo rhel || true', hide=True, warn=True)
    if res.stdout.strip() == "rhel":
        return "rhel"
    return None


def get_installed_kernels_debian(conn: Connection):
    result = conn.run(
        "dpkg --list | grep -E 'linux-image-[0-9]+' | awk '{print $2}' | sort -V | tail -n 5",
        hide=True
    )
    return result.stdout.strip().splitlines()


def get_running_kernel(conn: Connection):
    return conn.run("uname -r", hide=True).stdout.strip()


def get_kernel_update_logs_debian(conn: Connection):
    logs = []
    logs += conn.run(
        "awk '/Start-Date:|Commandline:|Requested-By:|linux-image/' /var/log/apt/history.log* 2>/dev/null | tail -n 20",
        hide=True, warn=True
    ).stdout.splitlines()
    logs += conn.run(
        "zgrep -h 'install linux-image' /var/log/dpkg.log* 2>/dev/null | tail -n 20",
        hide=True, warn=True
    ).stdout.splitlines()
    logs += conn.run(
        "journalctl --since '30 days ago' | grep -Ei 'kernel.*(upgrade|install)' | head -n 10",
        hide=True, warn=True
    ).stdout.splitlines()
    return logs


def get_pending_kernel_updates_debian(conn: Connection):
    result = conn.run("apt list --upgradable 2>/dev/null | grep -i linux-image", hide=True, warn=True)
    if result.stdout.strip():
        return result.stdout.strip().splitlines()
    return ["No kernel updates available."]


def get_installed_kernels_rhel(conn: Connection):
    result = conn.run("rpm -q kernel | sort -V | tail -n 3", hide=True, warn=True)
    return result.stdout.strip().splitlines()


def get_kernel_update_logs_rhel(conn: Connection):
    logs = []
    if conn.run('test -f /var/log/dnf.rpm.log', hide=True, warn=True).ok:
        logs += conn.run("grep -i kernel /var/log/dnf.rpm.log* 2>/dev/null | tail -n 20", hide=True, warn=True).stdout.splitlines()
    elif conn.run('test -f /var/log/yum.log', hide=True, warn=True).ok:
        logs += conn.run("grep -i kernel /var/log/yum.log* 2>/dev/null | tail -n 20", hide=True, warn=True).stdout.splitlines()
    logs += conn.run(
        "journalctl --since '30 days ago' | grep -Ei 'kernel.*(upgrade|install)' | head -n 10",
        hide=True, warn=True
    ).stdout.splitlines()
    return logs


def get_pending_kernel_updates_rhel(conn: Connection):
    updates = []
    if conn.run("dnf check-update kernel >/dev/null 2>&1", hide=True, warn=True).return_code == 100:
        updates += conn.run("dnf check-update kernel 2>/dev/null | grep -i kernel", hide=True, warn=True).stdout.splitlines()
    elif conn.run("yum check-update kernel >/dev/null 2>&1", hide=True, warn=True).return_code == 100:
        updates += conn.run("yum check-update kernel 2>/dev/null | grep -i kernel", hide=True, warn=True).stdout.splitlines()
    if not updates:
        updates = ["No kernel updates available."]
    return updates


def display_table(title, data_dict):
    table = Table(title=title, title_style=INFO, show_header=True)
    table.add_column("Type", style=INFO)
    table.add_column("Result", style=SUCCESS)
    for k, v in data_dict.items():
        if isinstance(v, list):
            v = "\n".join(v)
        table.add_row(k, v)
    console.print(table)
    console.print("\n")


def display_kernel_info(conn: Connection):
    distro = detect_distro(conn)
    if not distro:
        console.print("Distribution not detected", style=ERROR)
        return

    if distro == "debian":
        installed = get_installed_kernels_debian(conn)
        pending = get_pending_kernel_updates_debian(conn)
        logs = get_kernel_update_logs_debian(conn)
    else:
        installed = get_installed_kernels_rhel(conn)
        pending = get_pending_kernel_updates_rhel(conn)
        logs = get_kernel_update_logs_rhel(conn)

    running = get_running_kernel(conn)

    display_table("Running Kernel", {"Current Kernel": running})
    display_table("Installed Kernels", {"Installed Kernels": installed})
    display_table("Pending Kernel Updates", {"Updates": pending})

    console.print("Recent Kernel Update Logs", style=INFO)
    console.print()
    for line in logs:
        console.print(line)


def kernel_check(conn: Connection):
    console.print()
    display_kernel_info(conn)
    console.print("\nPress ENTER to return to the menu...", style=INFO)
    input()
