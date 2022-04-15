
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
    visualization: Visualization    # The visualization used in the widget
    width: int                      # Width of the widget
    options: Dict                   # Dictionary containing the widget options
    text: str                       # Contents of a text box

    def to_dict(self) -> Dict:
        return {
            "dashboard_id" : self.dashboard_id,
            "visualization_id" : self.visualization.id,
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

