import os
from pathlib import Path
import typer

app = typer.Typer()


@app.command()
def main(path: Path):
    """
    Delete all files from specified playlist at PATH.
    """
    with open(str(path)) as f:
        lines = f.readlines()

    def question(q):
        return input(q).lower().strip()[0] == "y" or question(q)

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if question(f"Are you sure to delete {line}? "):
            try:
                os.remove(line)
            except FileNotFoundError as e:
                print(e)


if __name__ == "__main__":
    app()
