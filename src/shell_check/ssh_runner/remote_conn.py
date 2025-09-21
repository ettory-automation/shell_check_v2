from shell_check.ssh_runner.hosts_ctrl.hostlist_control import menu_run, show_list
from pathlib import Path
from fabric import Connection, Config
from rich.console import Console
from rich.table import Table
from .banner_remote_conn import banner
import getpass
import socket
import os

console = Console()
COLORS = ['green', 'red', 'yellow', 'purple', 'magenta']
BASE_DIR = Path(__file__).parent
HOSTS_FILE = BASE_DIR / 'hosts_ctrl' / 'hosts.txt'
KEY_DIR = BASE_DIR / 'keyfile_control'
PASSWORD_ATTEMPTS = 3


def get_connection_type():
    while True:
        console.print()
        conn_type = console.input(f'[{COLORS[3]}]Select connection type (key/password): [/]').strip().lower()
        if conn_type in ('key', 'password'):
            return conn_type
        console.print("\nInvalid option! Please enter 'key' or 'password'.", style=COLORS[1])


def wait_for_enter(msg="Press Enter to continue..."):
    console.print()
    console.input(f"[{COLORS[3]}]{msg}[/]")


def define_hostlist():
    menu_run()

def get_username():
    while True:
        user = console.input(f'[{COLORS[3]}]Username: [/]')
        if user.strip():
            return user
        console.print("\nUsername cannot be empty! \n", style=COLORS[1])

def choose_ssh_key():
    keys = list(KEY_DIR.glob('*'))
    if not keys:
        return None

    table = Table(title=f"SSH Key List", title_style=COLORS[3])
    table.add_column("Index", justify="right")
    table.add_column("Key File", justify="left")

    for i, key in enumerate(keys):
        table.add_row(str(i), key.name)

    console.print("\n", table, "\n")
    console.print(f'Located in: {KEY_DIR}\n', style=COLORS[4])

    while True:
        choice = console.input(f"[{COLORS[3]}]Select key index to use: [/]").strip()
        try:
            index = int(choice)
            if 0 <= index < len(keys):
                return keys[index]
            console.print("\nInvalid index, try again.", style=COLORS[1])
        except ValueError:
            console.print("\nPlease enter a valid number.", style=COLORS[1])


def select_host():
    HOSTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(HOSTS_FILE, 'r') as f:
        f_hosts = [line.strip() for line in f if line.strip()]

    if not f_hosts:
        console.print("\nHosts list is empty!", style=COLORS[1])
        wait_for_enter()
        return None

    table = Table(title=f"Hostlist", title_style=COLORS[3], title_justify='center')
    table.add_column("Index", justify="right")
    table.add_column("Host", justify="left")
    for i, host in enumerate(f_hosts):
        table.add_row(str(i), host)

    console.print("\n", table, "\n")
    console.print(f'Located in: {HOSTS_FILE}', style=COLORS[4])

    while True:
        console.print()
        choice = console.input(f"[{COLORS[3]}]Select host index: [/]").strip()
        try:
            index = int(choice)
            if 0 <= index < len(f_hosts):
                return f_hosts[index]
            console.print("\nInvalid index, try again.", style=COLORS[1])
        except ValueError:
            console.print("\nPlease enter a valid number.", style=COLORS[1])


def connect_with_password(host, user):
    for attempt in range(1, PASSWORD_ATTEMPTS + 1):
        console.print(f"\nPassword attempt {attempt}/{PASSWORD_ATTEMPTS}: ", style=COLORS[3], end='')
        passwd = getpass.getpass('')
        config = Config(overrides={'sudo': {'password': passwd}})
        try:
            conn = Connection(
                host=host,
                user=user,
                connect_kwargs={'password': passwd},
                config=config,
                connect_timeout=10
            )
            conn.open()
            console.print(f"\nConnected with password to {host}", style=COLORS[0])
            return conn
        except (Exception, socket.timeout) as e:
            console.print()
            console.print(f"Connection failed: {e}", style=COLORS[1])
    console.print(f"All {PASSWORD_ATTEMPTS} password attempts failed.", style=COLORS[1])
    return None


def create_ssh_session():
    os.system('clear')
    banner()

    host = select_host()
    if not host:
        console.print("No host selected. Exiting...", style=COLORS[1])
        return None

    connection_type = get_connection_type()
    conn = None

    if connection_type == 'key':
        key_file = choose_ssh_key()
        if not key_file:
            console.print()
            console.print(f"No keyfile exists or not selected in {KEY_DIR}", style=COLORS[1])
            console.print()
            console.print(f'Falling back to password authentication...', style=COLORS[3])
            connection_type = 'password'
        else:
            console.print()
            user = get_username()
            console.print(f'\nConnecting to host: {host}', style=COLORS[3])
            try:
                conn = Connection(
                    host=host,
                    user=user,
                    connect_kwargs={'key_filename': str(key_file)},
                    connect_timeout=10
                )
                conn.open()
                console.print(f'\nConnected with SSH key {key_file.name} to {host}', style=COLORS[0])
            except Exception as e:
                console.print(f'\nKey authentication failed: {e}', style=COLORS[1])
                console.print(f'\nFalling back to password authentication...', style=COLORS[3])
                connection_type = 'password'

    if connection_type == 'password':
        console.print()
        user = get_username()
        console.print(f'\nConnecting to host: {host}', style=COLORS[3])
        conn = connect_with_password(host, user)

    if not conn:
        console.print("\nNo connection was established.", style=COLORS[1])
        return None

    return conn


