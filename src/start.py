import click


@click.command()
@click.option("--release", "-r", type=str)
def generate(release: str) -> None:
    """Generate a new wagtail site

    CMD: generate --release <release>
    """
    click.echo(click.style(f"Generating a new wagtail site with release {release}", fg="yellow"))
    