from rich.console import Console
from rich.table import Table
import subprocess
import os

console = Console()
COLORS = ['green', 'red', 'purple']

def detect_distro():
    if os.path.exists("/etc/debian_version"):
        return "debian"
    elif os.path.exists("/etc/redhat-release"):
        return "rhel"
    else:
        return None

def get_installed_kernels_debian():
    result = subprocess.run(
        "dpkg --list | grep -E 'linux-image-[0-9]+' | awk '{print $2}' | sort -V | tail -n 5",
        shell=True, capture_output=True, text=True
    )
    return result.stdout.strip().splitlines()

def get_running_kernel():
    return subprocess.check_output("uname -r", shell=True, text=True).strip()

def get_kernel_update_logs_debian():
    logs = []
    logs += subprocess.getoutput(
        "awk '/Start-Date:|Commandline:|Requested-By:|linux-image/' /var/log/apt/history.log* 2>/dev/null | tail -n 20"
    ).splitlines()
    logs += subprocess.getoutput(
        "zgrep -h 'install linux-image' /var/log/dpkg.log* 2>/dev/null | tail -n 20"
    ).splitlines()
    logs += subprocess.getoutput(
        "journalctl --since '30 days ago' | grep -Ei 'kernel.*(upgrade|install)' | head -n 10"
    ).splitlines()
    return logs

def get_pending_kernel_updates_debian():
    result = subprocess.getoutput("apt list --upgradable 2>/dev/null | grep -i linux-image")
    if result:
        return result.splitlines()
    else:
        return ["No kernel updates available."]

def get_installed_kernels_rhel():
    result = subprocess.run("rpm -q kernel | sort -V | tail -n 3", shell=True, capture_output=True, text=True)
    return result.stdout.strip().splitlines()

def get_kernel_update_logs_rhel():
    logs = []
    if os.path.exists("/var/log/dnf.rpm.log"):
        logs += subprocess.getoutput("grep -i kernel /var/log/dnf.rpm.log* 2>/dev/null | tail -n 20").splitlines()
    elif os.path.exists("/var/log/yum.log"):
        logs += subprocess.getoutput("grep -i kernel /var/log/yum.log* 2>/dev/null | tail -n 20").splitlines()
    logs += subprocess.getoutput(
        "journalctl --since '30 days ago' | grep -Ei 'kernel.*(upgrade|install)' | head -n 10"
    ).splitlines()
    return logs

def get_pending_kernel_updates_rhel():
    if subprocess.run("dnf check-update kernel >/dev/null 2>&1", shell=True).returncode == 100:
        return subprocess.getoutput("dnf check-update kernel 2>/dev/null | grep -i kernel").splitlines()
    elif subprocess.run("yum check-update kernel >/dev/null 2>&1", shell=True).returncode == 100:
        return subprocess.getoutput("yum check-update kernel 2>/dev/null | grep -i kernel").splitlines()
    else:
        return ["No kernel updates available."]


def display_table(title, data_dict):
    table = Table(title=title, title_style=COLORS[2], show_header=True)
    table.add_column("Type", style=COLORS[2])
    table.add_column("Result", style=COLORS[0])

    for k, v in data_dict.items():
        if isinstance(v, list):
            v = "\n".join(v)
        table.add_row(k, v)
    console.print(table)
    console.print("\n")

def display_kernel_info():
    distro = detect_distro()
    if not distro:
        console.print(f"[{COLORS[1]}]Distribution not detected[/]{COLORS[1]}")
        return

    if distro == "debian":
        installed = get_installed_kernels_debian()
        pending = get_pending_kernel_updates_debian()
        logs = get_kernel_update_logs_debian()
    else:
        installed = get_installed_kernels_rhel()
        pending = get_pending_kernel_updates_rhel()
        logs = get_kernel_update_logs_rhel()

    running = get_running_kernel()

    display_table("Running Kernel", {"Current Kernel": running})
    display_table("Installed Kernels", {"Installed Kernels": installed})
    display_table("Pending Kernel Updates", {"Updates": pending})

    console.print(f"[{COLORS[2]}]Recent Kernel Update Logs[/]{COLORS[2]}")
    for line in logs:
        console.print(line)

    console.print("\nPress ENTER to continue...")
    input()

def kernel_check():
    display_kernel_info()
    console.print("\nPress ENTER to return to the menu...")
    input()
