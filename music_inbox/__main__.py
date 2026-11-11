import typer

from . import artwork, clean, folder2genre, genres, playlist2delete, qualitycheck, rekorbox2json

app = typer.Typer(help="Music Inbox CLI - manage and clean your music library")

# Add each file's main function as a subcommand
app.command("artwork")(artwork.main)
app.command("clean")(clean.main)
app.command("folder2genre")(folder2genre.main)
app.command("genres")(genres.main)
app.command("playlist2delete")(playlist2delete.main)
app.command("qualitycheck")(qualitycheck.main)
app.command("rekorbox2json")(rekorbox2json.main)

if __name__ == "__main__":
    app()
