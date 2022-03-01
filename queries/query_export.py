import click
import requests

template = u"""/*
Name: {name}
Data source: {data_source}
Created By: {created_by}
Last Update At: {last_updated_at}
Visualizations: {visualizations}
*/

{query}"""


def get_queries(url, api_key):
    queries = [] 
    headers = {'Authorization': 'Key {}'.format(api_key)}
    path = "{}/api/queries".format(url)
    has_more = True
    page = 1
    while has_more:
        response = requests.get(path, headers=headers, params={'page': page}).json()
        queries.extend(response['results'])
        has_more = page * response['page_size'] + 1 <= response['count']
        page += 1

    return queries

def get_visualizations(queries, url, api_key):
    headers = {'Authorization' : 'Key {}'.format(api_key)}
    for query in queries:
        path = "{}/api/queries/{}".format(url, query['id'])
        response = requests.get(path, headers=headers, params={}).json()
        query['visualizations'] = response['visualizations']

def save_queries(queries):
    for query in queries:
        filename = 'query_{}.sql'.format(query['id'])
        with open(filename, 'w') as f:
            content = template.format(name=query['name'],
                       data_source=query['data_source_id'],
                       created_by=query['user']['name'],
                       last_updated_at=query['updated_at'],
                       visualizations=query['visualizations'],
                       query=query['query'])
            print(content)
            f.write(content)
            f.close()


@click.command()
@click.option('--redash-url')
@click.option('--api-key', help="API Key")
def main(redash_url, api_key):
    queries = get_queries(redash_url, api_key)    
    # Pull the visualization for each  query. Append it to that query's item
    get_visualizations(queries, redash_url, api_key) 
    save_queries(queries)


if __name__ == '__main__':
    main()
