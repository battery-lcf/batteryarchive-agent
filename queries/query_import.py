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
    for f in files:
        if f.startswith('query_') and f.endswith('.sql'):
            start = f.index('_') + 1
            end = f.index('.')
            query_id = f[start:end]
            path = "{}/api/queries".format(url)
            query_headers = get_headers(f)
            query_name = re.search("Name: (.+)", query_headers).group(1)
            print(query_name)
            query_str = get_query_str(f)
            payload = {'query': query_str, 'data_source_id': 1, 'name': query_name}
            print(payload)
            response = requests.post(path, headers=headers, data=json.dumps(payload))
            print(response.content)
            if(response.status_code == 200):
                visualizations = get_visualization_str(f)
                for viz in visualizations:
                    try:
                        payload = {
                            "query_id" : query_id,
                            "type" : viz.type,
                            "name" : viz.name,
                            "options" : viz.options,
                            "description" : viz.description
                        }
                        viz_response = requests.post(path, headers=headers, data=json.dumps(payload))
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
            if line[:15] == "Visualizations: ":
                vis_str = line[15:]
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
