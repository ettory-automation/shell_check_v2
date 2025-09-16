from rich.console import Console
from rich.table import Table
from pathlib import Path
import subprocess
import os
from time import sleep

console = Console()
COLORS = ['purple', 'red', 'green']

def sel_interface():
    while True:
        result = subprocess.run(['ip', '-o', '-4', 'addr', 'show'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')

        iface_data = {}
        for line in lines:
            parts = line.split()
            iface = parts[1]
            ip_addr = parts[3].split('/')[0]
            broadcast = parts[5] if len(parts) > 5 else "-"

            if iface not in iface_data:
                mac_result = subprocess.run(['cat', f'/sys/class/net/{iface}/address'], capture_output=True, text=True)
                mac = mac_result.stdout.strip()
                iface_data[iface] = {'ip': [ip_addr], 'mac': mac, 'broadcast': [broadcast]}
            else:
                iface_data[iface]['ip'].append(ip_addr)
                iface_data[iface]['broadcast'].append(broadcast)

        table = Table(show_header=True, header_style=COLORS[0], title="Available Interfaces", title_style=COLORS[0], title_justify='center')
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

        console.print(f"\nType Network Interface: ", style=COLORS[0], end='')
        inet = input().strip()

        if inet not in iface_data:
            console.print()
            console.print(f"Interface selected '{inet}' does not exist!", style=COLORS[1])
            
            console.print("\nBack to menu? (y/n) ", style=COLORS[0], end='')
            choice = input().strip().lower()

            if choice == 'y':
                return None
            elif choice == 'n':
                console.clear()
                continue
            else:
                console.print('\nInvalid option. Trying again...\n', style=COLORS[1])
                sleep(1)
                continue

        operstate_file = Path(f"/sys/class/net/{inet}/operstate")
        if operstate_file.exists():
            operstate = operstate_file.read_text().strip()
            if operstate not in ["up", "unknown"]:
                console.print(f"Interface '{inet}' exists, but it's DOWN. Status: {operstate.upper()}", style=COLORS[1])
                continue

        return inet

def set_interval():
    while True:
        console.print("\nSampling Interval (sec): ", style=COLORS[0], end='')
        interval_str = input().strip()
        if interval_str.isdigit() and int(interval_str) > 0:
            return int(interval_str)
        console.print("Invalid interval. Use only integer numbers > 0.", style=COLORS[1])
        console.print("Press ENTER to try again...", style=COLORS[0])
        input()

def read_traffic(inet: str):
    result = subprocess.run(['ip', '-s', 'link', 'show', inet], capture_output=True, text=True)
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

def get_data_traffic(inet: str, interval: int):
    first_rx, first_tx = read_traffic(inet)
    sleep(interval)
    second_rx, second_tx = read_traffic(inet)

    # Tabela de coletas
    table = Table(show_header=True, header_style=COLORS[0], title=f"Traffic Data for [{inet}]", title_style=COLORS[0], title_justify='center')
    table.add_column("Sample", justify="left")
    table.add_column("RX (bytes)", justify="right")
    table.add_column("TX (bytes)", justify="right")
    table.add_row("First Collect", str(first_rx), str(first_tx))
    table.add_row("Second Collect", str(second_rx), str(second_tx))

    console.print("\n")
    console.print(table)
    return first_rx, first_tx, second_rx, second_tx

def get_delta_diff_traffic(first_rx, first_tx, second_rx, second_tx, interval):
    rx_bytes = second_rx - first_rx
    tx_bytes = second_tx - first_tx
    rx_mbps = (rx_bytes * 8) / (interval * 1_000_000)
    tx_mbps = (tx_bytes * 8) / (interval * 1_000_000)

    # Tabela de delta
    table = Table(show_header=True, header_style=COLORS[0], title=f"Delta Traffic [Interval: {interval}s]", title_style=COLORS[0], title_justify='center')
    table.add_column("Direction", justify="left")
    table.add_column("Bytes Delta", justify="right")
    table.add_column("Mbps", justify="right")
    table.add_row("RX", str(rx_bytes), f"{rx_mbps:.2f}")
    table.add_row("TX", str(tx_bytes), f"{tx_mbps:.2f}")

    console.print("\n")
    console.print(table)

def network_check():
    os.system('clear')
    inet = sel_interface()
    if not inet:
        return

    interval = set_interval()
    console.print()
    console.print('Collecting data traffic...', style=COLORS[2])
    first_rx, first_tx, second_rx, second_tx = get_data_traffic(inet, interval)
    get_delta_diff_traffic(first_rx, first_tx, second_rx, second_tx, interval)

    console.print("\nPress ENTER to return to menu...", style=COLORS[0])
    input()
