import click
import requests
import json
import os
import re
import ast

# This is the basic requirement that we have for a visualization. Without all of these fields it will not work. 
"""
{
    "query_id" : 5,
    "type" : "TABLE",
    "name" : "Testing API",
    "options" : {},
    "description" : ""
}
"""
def save_queries(url, api_key):
    headers = {'Authorization': 'Key {}'.format(api_key), 'Content-Type': 'application/json'}

    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    print(len(files), files)

    saved_visualizations = {}

    for f in files:
        if f.startswith('query_') and f.endswith('.sql'):
            start = f.index('_') + 1
            end = f.index('.')
            path = "{}/api/queries".format(url)
            query_headers = get_headers(f)
            query_name = re.search("Name: (.+)", query_headers).group(1)
            print(query_name)
            query_str = get_query_str(f)
            payload = {'query': query_str, 'data_source_id': 1, 'name': query_name}
            print(payload)
            response = requests.post(path, headers=headers, data=json.dumps(payload))
            print(response.content)
            # If we were able to POST the query, get it's ID number
            if(response.status_code == 200):
                query_id = response.json()['id']
                # Save each of the visualizations so we can get to them later
                saved_visualizations[query_id]= get_visualization_str(f)
                if len(saved_visualizations) > 0:
                    print(f"Saving visualizations from query {query_id}")

    for query_id in saved_visualizations.keys():
        try:
            payload = {
                "query_id" : query_id,
                "type" : saved_visualizations[query_id]['type'],
                "name" : saved_visualizations[query_id]['name'],
                "options" : saved_visualizations[query_id]['options'],
                "description" : saved_visualizations[query_id]['description']
            }
            path = f"{url}/api/visualizations"
            viz_response = requests.post(path, headers=headers, data=json.dumps(payload))
            if(viz_response.status_code != 200):
                print(f"There was an error adding this visualization. {viz_response.content}")
            else:
                print(f"Visualization added to query #{query_id} -- {payload}")
        except KeyError as e:
            print(e)

def get_query_str(filename):
    query = ''
    with open(filename, 'r') as f:
        lines = f.readlines()
        for i in range(7, len(lines)):
            query += lines[i]
    return query

def get_visualization_str(filename):
    visualizations = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        vis_obj = {}
        for line in lines:
            if "Visualizations" in line:
                vis_str = line[15:].strip()
                vis_obj = ast.literal_eval(vis_str)

                for vis in vis_obj:
                    # Go through each visualization saved. Create a viz object from each item
                    visualizations.append(vis)
    return visualizations

def get_headers(filename):
    query = ''
    with open(filename, 'r') as f:
        lines = f.readlines()
        for i in range(1, 7):
            query += lines[i]
    return query

@click.command()
@click.option('--redash-url')
@click.option('--api-key')
def main(redash_url, api_key):
    save_queries(redash_url, api_key)


if __name__ == '__main__':
    main()
