import os
from time import sleep
from rich.console import Console
from rich import print
from rich.live import Live
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.formatted_text import HTML
from shell_check.core import banner, memory_run, disk_run, network_run, cpu_run, iops_run, kernel_run
from shell_check.ssh_runner.remote_conn import define_hostlist
from shell_check.ssh_runner.remote_conn import create_ssh_session as ssh_session

COLORS = ['red', 'green', 'purple']
console = Console()

def ensure_conn():
    global conn
    if not conn:
        conn = ssh_session()
        if not conn:
            console.print("Session aborted. Returning to main menu.", style=COLORS[0])
            return False
    return True

def show_menu():
    while True:
        os.system('clear')
        banner()

        print('\n\n')
        console.print('1) Memory Checker')
        console.print('2) CPU Consumption Details Checker')
        console.print('3) Disk Checker')
        console.print('4) Disk IOPS Checker')
        console.print('5) Network Traffic Checker')
        console.print('6) Kernel Updates Checker')
        console.print('7) Populate Hostlist File')
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
                if text not in [str(i) for i in range(8)]:
                    raise ValidationError(message='Invalid option!', cursor_position=len(text)) 

        option = session.prompt(
            HTML('\nSelect an option → '),
            validator=OptionValidator(),
            style=style
        )
        
        match option:
            case '1':
                conn = ssh_session()
                if not conn:
                    if not conn:
                        console.print("Session aborted. Returning to main menu.", style=COLORS[0])
                        continue
                
                memory_run(conn)
                continue
            case '2':
                conn = ssh_session()
                if not conn:
                    if not conn:
                        console.print("Session aborted. Returning to main menu.", style=COLORS[0])
                        continue
                cpu_run(conn)
                continue
            case '3':
                conn = ssh_session()
                if not conn:
                    if not conn:
                        console.print("Session aborted. Returning to main menu.", style=COLORS[0])
                        continue
                disk_run(conn)
                continue
            case '4':
                conn = ssh_session()
                if not conn:
                    if not conn:
                        console.print("Session aborted. Returning to main menu.", style=COLORS[0])
                        continue
                iops_run(conn)
                continue
            case '5':
                conn = ssh_session()
                if not conn:
                    if not conn:
                        console.print("Session aborted. Returning to main menu.", style=COLORS[0])
                        continue
                network_run(conn)
                continue
            case '6':
                conn = ssh_session()
                if not conn:
                    if not conn:
                        console.print("Session aborted. Returning to main menu.", style=COLORS[0])
                        continue
                kernel_run(conn)
                continue
            case '7':
                define_hostlist()
                continue
            case '0':
                with Live(console=console, refresh_per_second=4) as live:
                    msg = Text("\nExiting", style=COLORS[0])
                    live.update(msg)
                    for _ in range(4):
                        sleep(0.3)
                        msg.append(".")
                        live.update(msg)
                console.clear()
                break
            case _:
                break

if __name__ == "__main__":
    show_menu()
