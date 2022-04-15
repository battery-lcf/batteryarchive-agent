
from dataclasses import dataclass
from typing import Dict, List 


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
        for viz in self.visualizations:
            viz.query_id = new_id
        self.id = new_id

        return new_id

    def to_dict(self) -> Dict:
        return {
            "id" : self.id,
            "data_source_id" : 1,
            "name" : self.name,
            "query" : self.query,
            "visualizations" : [x.to_dict() for x in self.visualizations],
            "options" : self.options
        }


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

