from contextlib import contextmanager
from curses import raw
from typing import List
import requests
from redash_entites import Dashboard, Widget, Visualization, Query

KEY = "zhtVLTQ4xaIvV89tuWbv0OH5ozyKXiFAx3oy9cK6"
URL = "http://137.184.125.113/api"
headers = {'Authorization': f'Key {KEY}'}
dashboards_path = f"{URL}/dashboards"
visualizations_path = f"{URL}/visualizations"
widgets_path = f"{URL}/widgets"

@contextmanager
def redash_client(redash_url, api_key):
    pass

def get_query(query_id:int) -> Query:
    pass

def get_queries() -> List[Query]:
    pass

def get_dashboard(dash_id:int) -> Dashboard:
    """Get a single dashboard from the server
    """
    try:
        res = requests.get(dashboards_path + f"/{dash_id}", headers=headers)
    
    except Exception as e:
        # TODO Add better handling here
        print(e)

    dash_raw = res.json()
    dash_obj = Dashboard(id=dash_raw['id'], slug=dash_raw['slug'], 
            name=dash_raw['name'], user_id=dash_raw['user_id'], widgets=[])

    widgets = []
    queries = [] 
    visualizations = []
    for rw in dash_raw['widgets']:
        if rw['visualization'] is not None:
            raw_viz = rw['visualization']

        if raw_viz['query'] is not None:
            raw_query = raw_viz['query']

        
        viz = Visualization(
                id=raw_viz['id'],
                type=raw_viz['type'],
                name=raw_viz['name'],
                description=raw_viz['description'],
                options=raw_viz['options'],
                query_id=raw_viz['query']['id']
        )
        visualizations.append(viz)

        query = Query(
            id=raw_query['id'],
            name=raw_query['name'],
            options=raw_query['options'],
            query=raw_query['query'],
            visualizations=[viz]
        )
        queries.append(query)

        widg = Widget(
                id=rw['id'],
                dashboard_id=rw['dashboard_id'],
                text=rw['text'],
                options=rw['options'],
                width=rw['width'],
                visualization=viz
        )

        widgets.append(widg)
    dash_obj.widgets = widgets
    dash_obj.queries = queries

    return dash_obj


def get_all_dashboards(get_widgets:bool = False) -> List[Dashboard]:
    """Get all of the dashboards from the server

    Returns:
        List[Dashboard]: _description_
    """
    dashboards_list = []

    raw_dashboards:dict = {}
    
    try:
        res = requests.get(dashboards_path, headers=headers)
        raw_dashboards = res.json()

    except Exception as e:
        print(e)


    if len(raw_dashboards['results']) < 1:
        return dashboards_list

    for dash in raw_dashboards['results']:
        dashboards_list.append(get_dashboard(dash['id']))
        
        
    return dashboards_list
         


if __name__ == '__main__':
    dashboards = get_all_dashboards(get_widgets=True)
    print(dashboards)