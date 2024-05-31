import app.cli.commands.base as base
import typer

app = typer.Typer()
app.add_typer(base.cli, name="base")

if __name__ == "__main__":
    app()
