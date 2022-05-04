
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
from numpy import VisibleDeprecationWarning 


@dataclass
class Visualization:
    """ 
        Visualizaton Data Class
    """
    id: int
    name: str
    type: str
    description: str 
    options: Dict
    query_id: int

    def to_dict(self) -> Dict:
        return{
            "id" : self.id,
            "query_id" : self.query_id,
            "type" : self.type,
            "name" : self.name,
            "options" : self.options,
            "description" : self.description
        }
    
    @classmethod
    def from_dict(cls, viz_dict) -> Visualization:
        return cls(
            id=viz_dict['id'],
            query_id=viz_dict['query_id'],
            type=viz_dict['type'],
            name=viz_dict['name'],
            options=viz_dict['options'],
            description=viz_dict['description']
        )


@dataclass
class Query:
    """
        Query Data Class
    """
    id: int
    name: str
    options: Dict 
    query: str
    visualizations: List[Visualization]
    data_source_id: int = 1

    def change_id(self, new_id:int) -> int:
        """Change the query ID of the query. 
        Also changes the query_id of all children visualizations

        Args:
            new_id (int): new id of the query

        Returns:
            int: _description_
        """
        # Change the ID in the visualizations
        for viz in self.visualizations:
            viz.query_id = new_id

        # Change the ID of the object                    
        self.id = new_id

        return new_id

    def to_dict(self) -> Dict:
        """Return a dictionary representation of the query. Currently sets data_source_id to 1

        Returns:
            Dict: Query dictionary. 
        """
        return {
            "id" : self.id,
            "data_source_id" : 1,
            "name" : self.name,
            "query" : self.query,
            "visualizations" : [x.to_dict() for x in self.visualizations],
            "options" : self.options
        }

    @classmethod
    def from_dict(cls, query_dict:Dict) -> Query:
        """Return a Query from a provided dict

        Args:
            query_dict (dict): Query dictiornary as returned from the API

        Returns:
            Query: Query object 
        """
        visualizations = []

        for v in query_dict['visualizations']:
            viz_obj = Visualization.from_dict(v)
            visualizations.append(viz_obj)

        return cls(
            id=query_dict.get('id'),
            name=query_dict.get('name'),
            query=query_dict.get('query'),
            visualizations=visualizations,
            options=query_dict.get('options')
        )


@dataclass
class Widget:
    """
        Widget Data Class
    """
    id: int                         # Widget ID
    dashboard_id: int               # Dashboard that the widget belongs to
    visualization_id: int           # The visualization used in the widget
    width: int                      # Width of the widget
    options: Dict                   # Dictionary containing the widget options
    text: str                       # Contents of a text box

    def to_dict(self) -> Dict:
        return {
            "id" : self.id,
            "dashboard_id" : self.dashboard_id,
            "visualization_id" : self.visualization_id,
            "options" : self.options,
            "text" : self.text,
            "width" : self.width,
        }

    @classmethod
    def from_dict(cls, widget_dict: Dict):
        return cls(
            id=widget_dict.get("id"),
            dashboard_id=widget_dict.get("dashboard_id"),
            visualization_id=widget_dict.get("visualization_id"),
            width=widget_dict.get("width"),
            options=widget_dict.get("options"),
            text=widget_dict.get("text")
        )

@dataclass
class Dashboard:
    """ 
        Dashboard Data Class
    """
    id: int                 # Dashboard ID Number
    slug: str               # URL Slug for the dashboard
    name: str               # Name of the Dashboard
    user_id: int            # User_ID associated with the dashboard. This will be 1 typically
    widgets: List[Widget]   # The widgets that go into the dashboard
    queries: List[Query]

    def to_dict(self) -> Dict:
        return {
            "name" : self.name,
            "slug" : self.slug,
            "user_id" : self.user_id,
            "widgets" : [x.to_dict() for x in self.widgets],
            "queries" : [x.to_dict() for x in self.queries],
        }

    @classmethod
    def from_dict(cls, dashboard_dict:Dict):
        return cls(
            id=dashboard_dict.get("id"),
            slug=dashboard_dict.get("slug"),
            name=dashboard_dict.get("name"),
            user_id=dashboard_dict.get("user_id"),
            widgets=dashboard_dict.get("widgets"),
            queries=dashboard_dict.get("queries")
        )

