"""CLI entry point for the Film Agent."""

import os
import sys
import cmd
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from src.agent import FilmAgent
from src.data.seed_data import seed_films_database
from src.config import FILMS_DB_PATH

# Initialize rich console
console = Console()


class FilmAgentCLI(cmd.Cmd):
    """Command line interface for the film agent."""
    
    intro = 'Welcome to the Film Agent! Type "help" or "?" to list commands.'
    prompt = '\n> '
    
    def __init__(self):
        super().__init__()
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the agent and database."""
        try:
            # Check if DB exists, if not seed it
            if not os.path.exists(FILMS_DB_PATH):
                console.print("[yellow]Initializing film database...[/yellow]")
                seed_films_database()
            
            console.print("[green]Starting Film Agent...[/green]")
            self.agent = FilmAgent()
            
            # Display agent info
            info = self.agent.agent_info
            console.print(Panel(
                f"[bold]Provider:[/bold] {info.get('provider')}\n[bold]Model:[/bold] {info.get('model')}",
                title="Configuration",
                border_style="green"
            ))
            
            # Start session
            welcome_msg = self.agent.start_session()
            console.print(Panel(Markdown(welcome_msg), title="Agent", border_style="blue"))
            
        except Exception as e:
            console.print(f"[bold red]Error initializing agent:[/bold red] {e}")
            sys.exit(1)
    
    def default(self, line):
        """Handle default commands (chat messages)."""
        if not line:
            return
        
        try:
            with console.status("[bold green]Thinking...[/bold green]"):
                response = self.agent.process_query(line)
            
            console.print(Panel(Markdown(response), title="Agent", border_style="blue"))
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted[/yellow]")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            
    def do_quit(self, arg):
        """Exit the application."""
        console.print("[green]Goodbye![/green]")
        return True
    
    def do_exit(self, arg):
        """Exit the application."""
        return self.do_quit(arg)
    
    def do_clear(self, arg):
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def do_switch(self, arg):
        """Switch LLM provider. Usage: switch <provider> [model]
        Example: switch ollama llama3
        Example: switch gemini"""
        args = arg.split()
        if not args:
            console.print("[red]Usage: switch <provider> [model][/red]")
            return
            
        provider = args[0]
        model = args[1] if len(args) > 1 else None
        
        with console.status(f"[bold green]Switching to {provider}...[/bold green]"):
            result = self.agent.switch_provider(provider, model)
            
        console.print(Panel(result, title="System", border_style="yellow"))
    
    def do_models(self, arg):
        """Show current model info."""
        info = self.agent.agent_info
        console.print(Panel(
            f"[bold]Provider:[/bold] {info.get('provider')}\n[bold]Model:[/bold] {info.get('model')}",
            title="Current Configuration",
            border_style="green"
        ))


def main():
    """Main entry point."""
    try:
        cli = FilmAgentCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
