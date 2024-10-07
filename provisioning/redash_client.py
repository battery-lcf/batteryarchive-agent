from typing import List, Tuple, Dict
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
        
        self.query_lookup = {}
        self.visualization_lookup = {}

    def lookup_old_queryID(self, new_query_id) -> int:
        """Return the old Query ID of a Query that has been imported.
        Note: 
            This function will only look up values that have been 
        Args:
            new_query_ID (_type_): _description_

        Returns:
            int: Returns the old query ID of the inserted query. If new_query_id is not found
                it will return None
        """
        ret_val = None
        
        if new_query_id in self.query_lookup:
            ret_val = self.query_lookup[new_query_id]

        return ret_val

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
            self.query_lookup[ret_val] = query_to_post.id
            print(f"Added query!")
        
        return ret_val

    def update_query(self, query_id:int, query_to_update:Query) -> int:
        """Update a given query. Note that this will overwrite a previous query so use carefully

        Args:
            query_id (int): Query ID to update
            query_to_update (Query): Query Object to update with

        Returns:
            int: Query ID of the updated query
        """
        query_update_payload = {
            'name' : query_to_update.name,
            'query' : query_to_update.query,
            'data_source_id' : query_to_update.data_source_id,
            'options' : query_to_update.options,
        }
        query_response = requests.post(self.queries_path + f"/{query_id}", headers=self.headers,
                data=json.dumps(query_update_payload))
        ret_val = -1
        if query_response.status_code != 200:
            print(f"There was an error inserting this query. {query_response.content}")
        else:
            ret_val = query_response.json()['id']
            print(f"Updated query!")
        
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

    def archive_dashboard_by_slug(self,dashboard_id: int) -> None:
        try:
            res = requests.delete(self.dashboards_path+f"/{dashboard_id}", headers=self.headers)
            print(res.request.url)
            if res.status_code != 200: 
                print(f"Error archiving dashboard: {res.content}")
        except Exception as e:
            raise(e)
    
    def archive_dashboards(self) -> None:
        try:
            dashboards = self.get_all_dashboards()
            for d in dashboards:
                self.archive_dashboard_by_slug(d.id)
        except Exception as e:
            raise(e)

    def refresh_query_results(self, query_id:int, params:Dict) -> None:
        """_summary_

        Args:
            query_id (int): _description_
            params (Dict): _description_
        """
        body = {"max_age": 0}
        
        try:
            res = requests.post(self.queries_path+f"/{query_id}/results", 
                                    headers=self.headers, params=params, json=body)
            if(res.status_code != 200):
                print(f"Error refreshing the query: {res.content}")
            raw_query = res.json()
            query_result = json.dumps(raw_query)

        except Exception as e:
            raise(e)

        return query_result
    
    def archive_query_by_id(self, query_id: int) -> None:
        try:
            res = requests.delete(self.queries_path+f"/{query_id}", headers=self.headers)
            if (res.status_code != 200):
                print(f"Error archiving the query: {res.content}")
        except Exception as e:
            raise(e)
    
    def archive_queries(self) -> None:
        """
        Archive all queries
        """
        try:
            queries = self.get_all_queries()
            for q in queries:
                self.archive_query_by_id(q.id)
        except Exception as e:
            raise(e)

    def get_query_results(self, query_id:int) -> Dict:
        """Get the result

        Args:
            query_id (int)
        
        """
        query_result = {}
        try:
            res = requests.get(self.queries_path+f"/{query_id}/results", headers=self.headers)
            if(res.status_code != 200):
                print(f"Error refreshing the query: {res.content}")
            raw_query = res.json()
            query_result = json.dumps(raw_query)

        except Exception as e:
            raise(e)

        return query_result

    def get_query(self, query_id:int) -> Query:
        """Get a single query from the server

        Args:
            query_id (_type_): Query ID to retrieve from the server

        Returns:
            Query: Query Object populated from the server
        """
        query = None
        try:
            res = requests.get(self.queries_path+f"/{query_id}", headers=self.headers)
            raw_query = res.json()
            query = Query(id=raw_query['id'], name=raw_query['name'], options=raw_query['options'],
                visualizations=None, query=raw_query['query'])
            
            visualiuzations = []
            for viz in raw_query['visualizations']:
                v = Visualization(id=viz['id'], name=viz['name'], type=viz['type'], 
                        description=viz['description'], options=viz['options'], query_id=query.id)
                visualiuzations.append(v)
            query.visualizations = visualiuzations


        except Exception as e:
            raise(e)

        return query

    def get_all_queries(self) -> List[Query]:
        """Get all the queries from the server

        Returns:
            List[Query]: List of queries retrieved from the server
        """
        queries_list = []
        raw_queries:dict = {}
        try:
            # TODO Create real pagination here
            res = requests.get(self.queries_path+"?page_size=100", headers=self.headers)
            raw_queries = res.json()

        except Exception as e:
            print(e)


        if len(raw_queries['results']) < 1:
            return queries_list

        for query in raw_queries['results']:
            queries_list.append(self.get_query(query['id']))
            
            
        return queries_list

    def load_dashboards_from_file(self, file_name:str) -> Tuple[List[Dashboard], List[Query]]:
        """Load Dashboards from a specified file

        Args:
            file_name (str): Filename of JSON containing dashboards 

        Returns:
            List[Dashboard]: List of loaded Dashboards from provided JSON file.
        """
        dashboards_list = []
        queries_list = []
        
        with open(file_name) as f:
            raw_file = f.read()
            raw_json = json.loads(raw_file)
            dashboards_json = raw_json['dashboards_array']
            queries_json = raw_json['queries_array']

            for dash in dashboards_json:
                queries = []
                widgets = []
                visualizations = [] 

                for query in dash['queries']:

                    for viz in query['visualizations']:
                        v = Visualization(
                            id=viz['id'], 
                            name=viz['name'], 
                            type=viz['type'], 
                            description=viz['description'], 
                            options=viz['options'], 
                            query_id=query['id'])
                        visualizations.append(v)

                    q = Query(
                            id=query['id'], 
                            name=query['name'], 
                            options=query['options'], 
                            visualizations=visualizations, 
                            query=query['query'])
                    queries.append(q)
                
                for widget in dash['widgets']:
                    w = Widget(
                            id=widget['id'], 
                            dashboard_id=widget['dashboard_id'], 
                            text=widget['text'], 
                            visualization_id=widget['visualization_id'], 
                            width=widget['width'], 
                            options=widget['options'])
                    widgets.append(w)

                d = Dashboard(
                            id=None, 
                            slug=dash['slug'], 
                            name=dash['name'], 
                            user_id=dash['user_id'],
                            widgets=widgets, 
                            queries=queries)
                dashboards_list.append(d)
                print("Loaded in the dashboards")
            
            for query in queries_json:
                visualizations = []
                for viz in query['visualizations']:
                    visualizations.append(Visualization.from_dict(viz))
                q = Query(id=query['id'], name=query['name'], options=query['options'], 
                        visualizations=visualizations, query=query['query'])
                queries_list.append(q)

        return (dashboards_list, queries_list)

    def save_dashboards_to_file(self, file_name:str, dashboards:List[Dashboard], queries:List[Query]) -> None:
        """Save dashboards as JSON 

        Args:
            file_name (str): File name to save as JSON
        """
        export_file = {
            "queries_array" : [x.to_dict() for x in queries],
            "dashboards_array" : [x.to_dict() for x in dashboards] 
        }
        with open(file_name, "w") as f:
            dump = json.dumps(export_file)
            f.write(dump)


    def import_dashboards(self, dashboards: List[Dashboard], queries: List[Query]):
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


    

