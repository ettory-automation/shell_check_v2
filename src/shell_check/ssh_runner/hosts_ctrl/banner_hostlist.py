import pyfiglet
from rich.console import Console
from rich.text import Text

TITLE = 'Set Hostlist'
FONT = 'doom'
COLOR = 'purple'

console = Console()

def banner():
    ASCIITEXT = (pyfiglet.figlet_format(TITLE, font=FONT))
    console.print(Text(ASCIITEXT, style=COLOR))
