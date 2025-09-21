from rich.console import Console
from rich.table import Table
from time import sleep
from fabric import Connection
import os

console = Console()
COLORS = ['purple', 'red', 'green']

INFO = COLORS[0]
ERROR = COLORS[1]
SUCCESS = COLORS[2]


def sel_interface(conn: Connection):
    while True:
        result = conn.run('ip -o -4 addr show', hide=True)
        lines = result.stdout.strip().split('\n')

        iface_data = {}
        for line in lines:
            parts = line.split()
            iface = parts[1]
            ip_addr = parts[3].split('/')[0]
            broadcast = parts[5] if len(parts) > 5 else "-"

            if iface not in iface_data:
                mac_res = conn.run(f'cat /sys/class/net/{iface}/address', hide=True)
                mac = mac_res.stdout.strip()
                iface_data[iface] = {'ip': [ip_addr], 'mac': mac, 'broadcast': [broadcast]}
            else:
                iface_data[iface]['ip'].append(ip_addr)
                iface_data[iface]['broadcast'].append(broadcast)

        table = Table(show_header=True, header_style=INFO, title="Available Interfaces", title_style=INFO, title_justify='center')
        table.add_column("Interface", justify="left")
        table.add_column("IP Address(es)", justify="left")
        table.add_column("MAC Address", justify="left")
        table.add_column("Broadcast(es)", justify="left")

        for iface, data in iface_data.items():
            table.add_row(
                iface,
                ", ".join(data['ip']),
                data['mac'],
                ", ".join(data['broadcast'])
            )
        console.print(table)

        inet = console.input(f"\nType Network Interface: [{INFO}]").strip()
        if inet not in iface_data:
            console.print(f"Interface selected '{inet}' does not exist!", style=ERROR)
            choice = console.input(f"\nBack to menu? (y/n) [{INFO}]").strip().lower()
            if choice == 'y':
                return None
            else:
                continue

        operstate_res = conn.run(f'cat /sys/class/net/{inet}/operstate', hide=True, warn=True)
        operstate = operstate_res.stdout.strip() if operstate_res.ok else "unknown"
        if operstate not in ["up", "unknown"]:
            console.print(f"Interface '{inet}' exists, but it's DOWN. Status: {operstate.upper()}", style=ERROR)
            continue

        return inet


def set_interval():
    while True:
        interval_str = console.input("\nSampling Interval (sec): ").strip()
        if interval_str.isdigit() and int(interval_str) > 0:
            return int(interval_str)
        console.print("Invalid interval. Use only integer numbers > 0.", style=ERROR)
        input("Press ENTER to try again...")


def read_traffic(conn: Connection, inet: str):
    result = conn.run(f'ip -s link show {inet}', hide=True)
    rx_bytes = tx_bytes = 0
    lines = result.stdout.splitlines()
    for i, line in enumerate(lines):
        if 'RX:' in line:
            rx_line = lines[i + 1].strip().split()
            rx_bytes = int(rx_line[0])
        elif 'TX:' in line:
            tx_line = lines[i + 1].strip().split()
            tx_bytes = int(tx_line[0])
    return rx_bytes, tx_bytes


def get_data_traffic(conn: Connection, inet: str, interval: int):
    first_rx, first_tx = read_traffic(conn, inet)
    sleep(interval)
    second_rx, second_tx = read_traffic(conn, inet)

    table = Table(show_header=True, header_style=INFO, title=f"Traffic Data for [{inet}]", title_style=INFO, title_justify='center')
    table.add_column("Sample", justify="left")
    table.add_column("RX (bytes)", justify="right")
    table.add_column("TX (bytes)", justify="right")
    table.add_row("First Collect", str(first_rx), str(first_tx))
    table.add_row("Second Collect", str(second_rx), str(second_tx))

    console.print(table)
    return first_rx, first_tx, second_rx, second_tx


def get_delta_diff_traffic(first_rx, first_tx, second_rx, second_tx, interval):
    rx_bytes = second_rx - first_rx
    tx_bytes = second_tx - first_tx
    rx_mbps = (rx_bytes * 8) / (interval * 1_000_000)
    tx_mbps = (tx_bytes * 8) / (interval * 1_000_000)

    table = Table(show_header=True, header_style=INFO, title=f"Delta Traffic [Interval: {interval}s]", title_style=INFO, title_justify='center')
    table.add_column("Direction", justify="left")
    table.add_column("Bytes Delta", justify="right")
    table.add_column("Mbps", justify="right")
    table.add_row("RX", str(rx_bytes), f"{rx_mbps:.2f}")
    table.add_row("TX", str(tx_bytes), f"{tx_mbps:.2f}")

    console.print(table)


def network_check(conn: Connection):
    conn.run('TERM=xterm clear', warn=True)
    inet = sel_interface(conn)
    if not inet:
        return

    interval = set_interval()
    console.print('Collecting data traffic...', style=SUCCESS)
    first_rx, first_tx, second_rx, second_tx = get_data_traffic(conn, inet, interval)
    get_delta_diff_traffic(first_rx, first_tx, second_rx, second_tx, interval)

    console.print("\nPress ENTER to return to menu...", style=INFO)
    input()
