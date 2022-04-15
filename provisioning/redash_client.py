from typing import List
import requests
import json

from redash_entites import Dashboard, Query, Visualization, Widget

class RedashClient():

    def __init__(self, redash_key:str, redash_url:str="http://localhost/api") -> None:
        self.widgets_path = f"{redash_url}/widgets"
        self.queries_path = f"{redash_url}/queries"
        self.visualizations_path = f"{redash_url}/visualizations"
        self.dashboards_path = f"{redash_url}/dashboards"

        self.headers = {
            'Authorization' : f'Key {redash_key}',
            'Content-Type' : 'application/json'
        }

    def create_new_dashboard(self, dashboard_name: str) -> int:
        """Create a new dashboard on the server

        Args:
            dashboard_name (str): Name of the dashboard to be inserted

        Returns:
            int: Dashboard ID of the newly created dashboard
        """
        ret_val = -1
        res = requests.post(self.dashboards_path, headers=self.headers, 
                    data=json.dumps({'name' : dashboard_name}))
        if res.status_code != 200:
            print(f"There was an error creating this dashboard. {res.content}")
        else:
            ret_val = res.json()['id']
            print(f"Created the dashboard {dashboard_name}")
        return ret_val

    def post_query(self, query_to_post:Query) -> int:
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
        query_response = requests.post(self.queries_path, headers=self.headers,
                data=json.dumps(query_post_payload))

        ret_val = -1
        if query_response.status_code != 200:
            print(f"There was an error inserting this query. {query_response.content}")
        else:
            ret_val = query_response.json()['id']
            print(f"Added query!")
        
        return ret_val

    def post_visualization(self, viz_to_post:Visualization) -> int:
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
        viz_response = requests.post(self.visualizations_path, headers=self.headers,
                data=json.dumps(viz_post_payload))

        ret_val = -1
        if viz_response.status_code != 200:
            print(f"There was an error adding this visualization. {viz_response.content}")
        else:
            ret_val = viz_response.json()['id']
            print(f"Added visualization!")
        
        return ret_val

    def post_widget(self, widget_to_post:Widget) -> int:
        """Post a widget to the server given a Widget

        Args:
            widget_to_post (Widget): Widget to post on the server

        Returns:
            int: Widget ID of the newly inserted widget
        """
        widget_post_payload = {
            "dashboard_id" : widget_to_post.dashboard_id,
            "visualization_id" : widget_to_post.visualization_id,
            "options" : widget_to_post.options,
            "text" : widget_to_post.text,
            "width" : widget_to_post.width
        }
        widget_response = requests.post(self.widgets_path, headers=self.headers,
                data=json.dumps(widget_post_payload))

        ret_val = -1
        if widget_response.status_code != 200:
            print(f"There was an error inserting this widget. {widget_response.content}")
        else:
            ret_val = widget_response.json()['id']
            print("Added widget!")
        
        return ret_val

    def get_dashboard(self, dash_id:int) -> Dashboard:
        """Get a single dashboard from the server

        Args:
            dash_id (int): Dashboard ID to retrieve from the server

        Returns:
            Dashboard: Dashboard object containing the dashboard from the server
        """
        try:
            res = requests.get(self.dashboards_path + f"/{dash_id}", headers=self.headers)
        
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
                    visualization_id=rw['visualization']['id']
            )

            widgets.append(widg)
        dash_obj.widgets = widgets
        dash_obj.queries = queries

        return dash_obj

    def get_all_dashboards(self) -> List[Dashboard]:
        """Get all of the dashboards from the server

        Returns:
            List[Dashboard]: List of Dashboards from the server
        """
        dashboards_list = []

        raw_dashboards:dict = {}
        
        try:
            res = requests.get(self.dashboards_path, headers=self.headers)
            raw_dashboards = res.json()

        except Exception as e:
            print(e)


        if len(raw_dashboards['results']) < 1:
            return dashboards_list

        for dash in raw_dashboards['results']:
            dashboards_list.append(self.get_dashboard(dash['id']))
            
            
        return dashboards_list

    def load_dashboards_from_file(self, file_name:str) -> List[Dashboard]:
        """Load Dashboards from a specified file

        Args:
            file_name (str): Filename of JSON containing dashboards 

        Returns:
            List[Dashboard]: List of loaded Dashboards from provided JSON file.
        """
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

    def save_dashboards_to_file(self, file_name:str, dashboards:List[Dashboard]) -> None:
        """Save dashboards as JSON 

        Args:
            file_name (str): File name to save as JSON
        """
        dashboards_array = [x.to_dict() for x in dashboards]
        with open(file_name, "w") as f:
            dump = json.dumps(dashboards_array)
            f.write(dump)


    def import_dashboards(self, dashboards: List[Dashboard]):
        """Import dashboards into the server

        Args:
            dashboards (List[Dashboard]): List of Dashboards to import into the server
        """
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
                new_query_id = self.post_query(q)
                query_lookup[q.id] = new_query_id
                # change_id updates the query_id of child visualizations
                q.change_id(new_query_id)

                for viz in q.visualizations:
                    print(f"Importing {q.name} visualizations")
                    new_viz_id = self.post_visualization(viz)
                    viz_lookup[viz.id] = new_viz_id
                    viz.id = new_viz_id
            
        for dash in dashboards:
            new_dash_id = self.create_new_dashboard(dash.name)
            for w in dash.widgets:
                # Update the IDs in the imported widget.
                w.dashboard_id = new_dash_id
                old_viz_id = w.visualization_id
                w.visualization_id = viz_lookup.get(old_viz_id)
                new_widget_id = self.post_widget(w)
                w.id = new_widget_id


    

