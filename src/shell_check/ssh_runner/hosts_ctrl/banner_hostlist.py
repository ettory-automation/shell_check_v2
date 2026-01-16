import pyfiglet
from rich.console import Console
from rich.text import Text

TITLE = 'Set Host Target'
FONT = 'calvin_s'
COLOR = 'purple'

console = Console()

def banner():
    ASCIITEXT = (pyfiglet.figlet_format(TITLE.upper(), font=FONT))
    console.print(Text(ASCIITEXT, style=COLOR))
