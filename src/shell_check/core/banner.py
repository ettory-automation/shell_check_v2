import pyfiglet
from rich.console import Console
from rich.text import Text

TITLE = 'Shell Orchestrator'
FONT = 'calvin_s'
COLOR = 'cyan'

console = Console()

def banner():
    ASCIITEXT = (pyfiglet.figlet_format(TITLE.upper(), font=FONT))
    console.print(Text(ASCIITEXT, style=COLOR))
