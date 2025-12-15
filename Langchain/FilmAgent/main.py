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
            
        # Check for command typos
        commands = ['help', 'quit', 'exit', 'clear', 'switch', 'models']
        first_word = line.split()[0].lower()
        
        # Simple typo check (Levenshtein distance <= 2)
        for cmd_name in commands:
            if cmd_name == first_word:
                continue # exact match should have been handled by do_* methods
                
            # If it's close enough (e.g. swithc vs switch)
            if self._is_typo(first_word, cmd_name):
                console.print(f"[yellow]Did you mean '{cmd_name}'? Type '{cmd_name}' to run the command.[/yellow]")
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

    def _is_typo(self, input_str: str, target: str) -> bool:
        """Check if input is a typo of target (Levenshtein distance <= 1)."""
        if abs(len(input_str) - len(target)) > 2:
            return False
            
        # Basic Levenshtein distance implementation
        if len(input_str) < len(target):
            return self._is_typo(target, input_str)
            
        if len(target) == 0:
            return len(input_str) <= 2
            
        previous_row = range(len(target) + 1)
        for i, c1 in enumerate(input_str):
            current_row = [i + 1]
            for j, c2 in enumerate(target):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1] <= 2


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
