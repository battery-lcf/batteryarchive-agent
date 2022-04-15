from numpy import require
import click
from redash_client import RedashClient

@click.group()
def cli():
    pass

@click.command()
@click.argument('file_name', type=click.File())
@click.option('--redash-url', help="Redash URL to connect to", required=True, type=str)
@click.option('--redash-key', help="Redash API Key to use",  required=True, type=str)
def import_dashboards(file_name, redash_url, redash_key):
    """Import Dashboards from provided file to the provided server

    Args:
        file_name (_type_): Filename to JSON of dashboards to import
        redash_url (_type_): Redash URL to import to
        redash_key (_type_): Redash API Key to import with
    """
    client = RedashClient(redash_key=redash_key, redash_url=redash_url)
    loaded_dashboards = client.load_dashboards_from_file(file_name)
    client.import_dashboards(loaded_dashboards)
    

@click.command()
@click.argument('file_name', type=click.Path())
@click.option('--redash-url', help="Redash URL to connect to", required=True, type=str)
@click.option('--redash-key', help="Redash API Key to use",  required=True, type=str)
def export_dashboards(file_name, redash_url, redash_key):
    """Export Dashboards from the provided server into a JSON file

    Args:
        file_name (_type_): JSON File to dump to \n
        redash_url (_type_): Redash URL to export from \n
        redash_key (_type_): Redash API key to export with \n
    """
    client = RedashClient(redash_key=redash_key, redash_url=redash_url)
    fetched_dashboards = client.get_all_dashboards()
    client.save_dashboards_to_file(file_name, fetched_dashboards)

cli.add_command(import_dashboards)
cli.add_command(export_dashboards)

if __name__ == '__main__':
    cli()
