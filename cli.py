import typer
import uvicorn
from app.main import app

cli = typer.Typer(help="Pharmacy Inventory CLI")


@cli.command()
def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Run the FastAPI app."""
    uvicorn.run(app, host=host, port=port, reload=reload)


if __name__ == "__main__":
    cli()
