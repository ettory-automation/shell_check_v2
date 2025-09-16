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

COLORS = ['red', 'green', 'purple']

console = Console()

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
                if text not in [str(i) for i in range(7)]:
                    raise ValidationError(message='Invalid option!', cursor_position=len(text)) 

        option = session.prompt(
            HTML('\nSelect an option → '),
            validator=OptionValidator(),
            style=style
        )
        
        match option:
            case '1':
                memory_run()
                continue
            case '2':
                cpu_run()
                continue
            case '3':
                disk_run()
                continue
            case '4':
                iops_run()
                continue
            case '5':
                network_run()
                continue
            case '6':
                kernel_run()
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
