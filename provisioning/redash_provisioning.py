from contextlib import contextmanager
import json
from typing import List
import requests
from redash_entites import Dashboard, Widget, Visualization, Query

KEY = "bX674YQUtxbr3LorouHdT0dcP9kxK29m0cdPwrWT"
URL = "http://143.198.1.125/api"

headers = {'Authorization': f'Key {KEY}'}
dashboards_path = f"{URL}/dashboards"
visualizations_path = f"{URL}/visualizations"
widgets_path = f"{URL}/widgets"
queries_path = f"{URL}/queries"

@contextmanager
def redash_client(redash_url, api_key):
    pass

def get_query(query_id:int) -> Query:
    pass

def get_queries() -> List[Query]:
    pass

def create_new_dashboard(dashboard_name: str) -> int:
    """Create a new dashboard on the server

    Args:
        dashboard_name (str): Name of the dashboard to be inserted

    Returns:
        int: Dashboard ID of the newly created dashboard
    """
    ret_val = -1
    res = requests.post(dashboards_path, headers=headers, 
                data=json.dumps({'name' : dashboard_name}))
    if res.status_code != 200:
        print(f"There was an error creating this dashboard. {res.content}")
    else:
        ret_val = res.json()['id']
        print(f"Created the dashboard {dashboard_name}")
    return ret_val

def post_query(query_to_post:Query) -> int:
    """Post a query to the server given a Query

    Args:
        query_to_post (Query): Query to post on the server

    Returns:
        int: Query ID of the newly inserted query
    """
    query_post_payload = {
        'name' : query_to_post.name,
        'query' : query_to_post.query,
        'data_source_id' : query_to_post.data_source_id
    }
    query_response = requests.post(queries_path, headers=headers,
            data=json.dumps(query_post_payload))

    ret_val = -1
    if query_response.status_code != 200:
        print(f"There was an error inserting this query. {query_response.content}")
    else:
        ret_val = query_response.json()['id']
        print(f"Added query!")
    
    return ret_val

def post_visualization(viz_to_post:Visualization) -> int:
    """Post a visualization to the server given a Visualization

    Args:
        viz_to_post (Visualization): _description_

    Returns:
        int: Visualization ID of the newly created visualization
    """
    viz_post_payload = {
        "query_id" : viz_to_post.query_id,
        "type" : viz_to_post.type,
        "name" : viz_to_post.name,
        "options" : viz_to_post.options,
        "description" : viz_to_post.description
    }
    viz_response = requests.post(visualizations_path, headers=headers,
            data=json.dumps(viz_post_payload))

    ret_val = -1
    if viz_response.status_code != 200:
        print(f"There was an error adding this visualization. {viz_response.content}")
    else:
        ret_val = viz_response.json()['id']
        print(f"Added visualization!")
    
    return ret_val

def post_widget(widget_to_post:Widget) -> int:
    """Post a widget to the server given a Widget

    Args:
        widget_to_post (Widget): Widget to post on the server

    Returns:
        int: Widget ID of the newly inserted widget
    """
    widget_post_payload = {
        "dashboard_id" : widget_to_post.dashboard_id,
        "visualization_id" : widget_to_post.visualization.id,
        "options" : widget_to_post.options,
        "text" : widget_to_post.text,
        "width" : widget_to_post.width
    }
    widget_response = requests.post(widgets_path, headers=headers,
            data=json.dumps(widget_post_payload))

    ret_val = -1
    if widget_response.status_code != 200:
        print(f"There was an error inserting this widget. {widget_response.content}")
    else:
        ret_val = widget_response.json()['id']
        print("Added widget!")
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
    dash_obj = Dashboard(id=dash_raw['id'], slug=dash_raw['slug'], name=dash_raw['name'], 
                    user_id=dash_raw['user_id'], widgets=[], queries=[])

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


def get_all_dashboards() -> List[Dashboard]:
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

def save_dashboards_to_file(file_name:str) -> None:
    dashboards = get_all_dashboards()
    dashboards_array = [x.to_dict() for x in dashboards]
    with open(file_name, "w") as f:
        dump = json.dumps(dashboards_array)
        f.write(dump)

def load_dashboards_from_file(file_name:str) -> List[Dashboard]:
    dashboards_list = []
    
    with open(file_name) as f:
        dashboards_raw = f.read()
        dashboards_json = json.loads(dashboards_raw)

        for dash in dashboards_json:
            queries = []
            widgets = []
            visualizations = [] 

            for query in dash['queries']:

                for viz in query['visualizations']:
                    v = Visualization(id=None, name=viz['name'], type=viz['type'], 
                            description=viz['description'], options=viz['options'], query_id=query['id'])
                    visualizations.append(v)

                q = Query(id=query['id'], name=query['name'], options=query['options'], 
                        visualizations=visualizations, query=query['query'])
                queries.append(q)
            
            for widget in dash['widgets']:
                w = Widget(id=None, dashboard_id=widget['dashboard_id'], text=widget['text'], 
                        visualization_id=widget['visualization_id'], width=widget['width'], options=widget['options'])
                widgets.append(w)

            d = Dashboard(id=None, slug=dash['slug'], name=dash['name'], user_id=dash['user_id'],
                    widgets=widgets, queries=queries)
            dashboards_list.append(d)

    print("Loaded in the dashboards")

    return dashboards_list

def import_dashboards(dashboards: List[Dashboard]):
    # Step 1 -- Create a new Dashboard. Record it's new ID
    # Step 2 -- Import the queries. Record their new IDs
    # Step 3 -- Import the visualizations. 
    #           Use new Query IDs. Record their IDs
    # Step 4 -- Import the Widgets

    query_lookup = {} # "Old ID" (int) : "New ID" (int)
    viz_lookup = {} # Same as query

    # Make one pass to import all of the queries for all of the dashboards
    # This step will also import all the visualizations\

    for dash in dashboards:
        print(f"Importing {dash.name}'s queries")

        for q in dash.queries:
            if q.id in query_lookup:
                # TODO Should we make sure that the query is the same?
                # Currently just assume that the old query IDs are consistent
                continue
            new_query_id = post_query(q)
            query_lookup[q.id] = new_query_id
            q.change_id(new_query_id)

            for viz in q.visualizations:
                print(f"Importing {q.name} visualizations")
                new_viz_id = post_visualization(viz)
                viz.id = new_viz_id
                viz_lookup[viz.id] = new_viz_id
        
    for dash in dashboards:
        new_dash_id = create_new_dashboard(dash.name)
        for w in dash.widgets:
            # Update the IDs in the imported widget.
            w.dashboard_id = new_dash_id
            old_viz_id = w.visualization_id
            w.visualization_id = viz_lookup[old_viz_id]
            new_widget_id = post_widget(w)
            w.id = new_widget_id


if __name__ == '__main__':

    dashboards = load_dashboards_from_file("dashboards_2.json")
    print(dashboards)
    import_dashboards(dashboards)

