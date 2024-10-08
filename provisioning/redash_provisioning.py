from typing import Dict
import click
from redash_client import RedashClient

@click.group()
def cli():
    pass

@click.command()
@click.argument('file_name', type=click.Path())
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
    loaded_dashboards, loaded_queries = client.load_dashboards_from_file(file_name)
    priority_queries = {}
  
    imported_query_lookup = {}
    imported_visualization_lookup = {}

    #### Import all of the queries
    # Find all of the queries that rely on a Query. We want to remember which queries depend on what.
    for q in loaded_queries:
        if 'parameters' in q.options:
            for param in q.options['parameters']:
                if param['type'] == 'query':
                    if param['queryId'] in priority_queries:
                        priority_queries[param['queryId']].append(q.id)
                    else:
                        priority_queries[param['queryId']] = [q.id]
    
    # Import the priority queries first. 
    for query in priority_queries:
        for q in loaded_queries:
            if q.id == query:
                # Post independent query to server
                new_query_id = client.post_query(q)
                imported_query_lookup[q.id] = new_query_id

    # Import the rest queries now. Make sure we don't reimport a query we've already done
    for q in loaded_queries:
        if q.id in imported_query_lookup.keys():
            continue
        new_query_id = client.post_query(q)
        imported_query_lookup[q.id] = new_query_id

    # Lets go through all of the queries we just inserted and fix up their options.
    # We can also upload visualizations from each query with this step
    for q in loaded_queries:
        uploaded_query_id = imported_query_lookup[q.id]
        updated_query = False
        if 'parameters' in q.options:
            for param in q.options['parameters']:
                if param['type'] == 'query':
                    # Replace the queryId that was previously relied on, and update it
                    id_2b_replaced = param['queryId']
                    replaced_id = imported_query_lookup.get(id_2b_replaced) 
                    if replaced_id is None:
                        print(f"ERROR HERE!!! {q}")
                        continue
                    param['queryId'] = replaced_id

                    updated_query = True
        # If a query depended on another query, we've updated the relevant options
        if updated_query:
            client.update_query(uploaded_query_id, q)
        
        # Working through the visualizations
        for vis in q.visualizations:
            # Update the query id before sending it up
            vis.query_id = uploaded_query_id
            new_vis_id = client.post_visualization(vis)
            imported_visualization_lookup[vis.id] = new_vis_id
            
    ## Import all of the dashboards
    for d in loaded_dashboards:
        uploaded_dashboard_id = client.create_new_dashboard(d.name)
        
        for w in d.widgets:
            w.dashboard_id = uploaded_dashboard_id
            old_vis_id = w.visualization_id
            # Not all widgets have a visualization ID 
            if w.visualization_id is not None:
                w.visualization_id = imported_visualization_lookup.get(old_vis_id)
            client.post_widget(w)
                    
    

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
    fetched_queries = client.get_all_queries()
    priority_queries = {} # {indepenent_query : [dependent_queries]}

    for q in fetched_queries:
        if 'parameters' in q.options:
            for param in q.options['parameters']:
                if param['type'] == 'query':
                    if param['queryId'] in priority_queries:
                        priority_queries[param['queryId']].append(q.id)
                    else:
                        priority_queries[param['queryId']] = [q.id]

    client.save_dashboards_to_file(file_name, fetched_dashboards, fetched_queries)


@click.command()
@click.option('--redash-url', help="Redash URL to connect to", required=True, type=str)
@click.option('--redash-key', help="Redash API Key to use",  required=True, type=str)
def refresh_queries(redash_url, redash_key):
    client = RedashClient(redash_key=redash_key, redash_url=redash_url)
    queries = client.get_all_queries()

    updated_queries = []

    for q in queries:
        if not q.options.get('parameters'):
            try:
                client.refresh_query_results(q.id, {})
                updated_queries.append(q.id)
            except:
                print(f"Unable to refresh query ID {q.id}")
    
    for q in queries:
        if q.options.get('parameters'):
            for bq in q.options.get('parameters'):
                if bq.get('queryId') and bq.get('queryId') not in updated_queries:
                    print(f"{q.id} Requires {bq.get('queryId')} to update this query")
                    try:
                        client.refresh_query_results(bq.get('queryId'), {})
                        updated_queries.append(bq.get('queryId'))
                    except:
                        print(f"Unable to refresh {bq.get('queryId')} for {q.id}")

@click.command()
@click.option('--redash-url', help="Redash URL to connect to", required=True, type=str)
@click.option('--redash-key', help="Redash API Key to use", required=True, type=str)
def remove_dashboards(redash_url, redash_key):
    client = RedashClient(redash_key=redash_key, redash_url=redash_url)
    client.archive_dashboards()
            
@click.command()
@click.option('--redash-url', help="Redash URL to connect to", required=True, type=str)
@click.option('--redash-key', help="Redash API Key to use", required=True, type=str)
def remove_queries(redash_url, redash_key):
    client = RedashClient(redash_key=redash_key, redash_url=redash_url)
    client.archive_queries()

cli.add_command(import_dashboards)
cli.add_command(export_dashboards)
cli.add_command(refresh_queries)
cli.add_command(remove_dashboards)
cli.add_command(remove_queries)

if __name__ == '__main__':
    cli()
