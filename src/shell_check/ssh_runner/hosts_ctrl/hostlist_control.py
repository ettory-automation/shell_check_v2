from rich.console import Console
from pathlib import Path
from time import sleep
import os
from rich.live import Live
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.formatted_text import HTML
from .banner_hostlist import banner

console = Console()
COLORS = ['green', 'red', 'yellow', 'purple']

BASE_DIR = Path(__file__).parent
HOSTS_FILE = BASE_DIR / 'hosts.txt'

def wait_for_enter(msg="Press Enter to continue..."):
    console.print()
    console.input(f"[{COLORS[3]}]{msg}[/]")

def populate_hostlist() -> Path:
    HOSTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    while True:
        console.print()
        add_host = console.input(f"[{COLORS[3]}]Type host IP address: [/] ").strip()
        if not add_host:
            console.print("Empty input, try again!", style=COLORS[1])
            continue

        with open(HOSTS_FILE, 'a') as f:
            f.write(f"{add_host}\n")

        console.print()
        console.print(f"Host [{COLORS[0]}]{add_host}[/] added!", style=COLORS[3])
        console.print()

        choice = console.input(f"[{COLORS[3]}]Insert another host? (y/n): [/] ").strip().lower()
        if choice != 'y':
            break

    with open(HOSTS_FILE, 'r') as f:
        f_hosts = [line.strip() for line in f if line.strip()]

    console.print("\nHosts loaded:", style=COLORS[3])
    for i, host in enumerate(f_hosts):
        console.print()
        console.print(f"[{COLORS[2]}]{i}[/] → [{COLORS[0]}]{host}[/]")

    console.print("\nHosts list complete!", style=COLORS[3])
    return HOSTS_FILE

def edit_hostlist() -> None:
    HOSTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(HOSTS_FILE, 'r') as f:
        f_hosts = [line.strip() for line in f if line.strip()]

    if not f_hosts:
        console.print("\nHosts list is empty! Add hosts first.", style=COLORS[1])
        wait_for_enter()
        return

    first_time = True

    while True:
        console.print("\nCurrent hosts list:", style=COLORS[3])
        console.print()
        for i, host in enumerate(f_hosts):
            console.print(f"[{COLORS[2]}]{i}[/] → [{COLORS[0]}]{host}[/]")

        if first_time:
            wait_for_enter("Press Enter to continue to editing...")
            console.print()
            first_time = False
        else:
            while True:
                console.print()
                choice = console.input(f"[{COLORS[3]}]Do you want to edit another host? (y/n): [/] ").strip().lower()
                if choice in ('y', 'n'):
                    break
                console.print("Invalid input! Please type 'y' or 'n'.", style=COLORS[1])
            if choice == 'n':
                break

        # edição do host
        try:
            index = int(console.input(f"[{COLORS[3]}]Enter index to edit: [/] ").strip())
        except ValueError:
            console.print("\nIndex must be a number!", style=COLORS[1])
            continue

        if index < 0 or index >= len(f_hosts):
            console.print(f"Invalid index [{COLORS[0]}]{index}[/]!", style=COLORS[1])
            wait_for_enter()
            continue
        
        console.print()
        new_entry = console.input(f"[{COLORS[3]}]New entry: [/] ").strip()
        if not new_entry:
            console.print("Empty input, try again!", style=COLORS[1])
            wait_for_enter()
            continue

        old_value = f_hosts[index]
        f_hosts[index] = new_entry

        with open(HOSTS_FILE, 'w') as f:
            f.write("\n".join(f_hosts) + "\n")

        console.print(f"\nIndex [{COLORS[0]}]{index}[/] updated!", style=COLORS[3])
        console.print()
        console.print(f"[{COLORS[3]}]Old →[/] [{COLORS[1]}]{old_value}[/]")
        console.print(f"[{COLORS[3]}]New →[/] [{COLORS[0]}]{new_entry}[/]")
        console.print()
        wait_for_enter("Press Enter to continue editing...")

def fullclear_hostlist():
    HOSTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HOSTS_FILE, 'w') as f:
        pass
    console.print("Hosts list cleared!", style=COLORS[1], highlight=True)

def show_list():
    HOSTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(HOSTS_FILE, 'r') as f:
        f_hosts = [line.strip() for line in f if line.strip()]


    if not f_hosts:
        console.print()
        console.print("Hosts list is empty!", style=COLORS[1])
        console.print()
        wait_for_enter()
        return

    console.print()

    for i, host in enumerate(f_hosts):
        console.print(f"[{COLORS[2]}]{i}[/] → [{COLORS[0]}]{host}[/]")

    console.print()
    wait_for_enter()

def menu_run():
    while True:
        os.system('clear')
        banner()
        console.print()
        console.print()

        console.print('1) Populate Hostlist')
        console.print('2) Edit Hostlist')
        console.print('3) Clear All Hostlist')
        console.print('4) Show Hostlist')
        console.print('0) Exit')

        session = PromptSession()


        style = Style.from_dict({
            '': 'fg:white',
            'valid': 'fg:green',
            'invalid': 'fg:red'
        })

        class OptionValidator(Validator):
            def validate(self, document):
                text = document.text

                if text == '':
                    return
                if text not in [str(i) for i in range(5)]:
                    raise ValidationError(message='Invalid option!', cursor_position=len(text)) 

        option = session.prompt(
            HTML('\nSelect an option → '),
            validator=OptionValidator(),
            style=style
        )
        
        match option:
            case '1':
                populate_hostlist()
                continue
            case '2':
                edit_hostlist()
                continue
            case '3':
                fullclear_hostlist()
                continue
            case '4':
                show_list()
                continue
            case '0':
                break
            case _:
                break
