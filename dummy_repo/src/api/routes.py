from typing import List, Dict, Any

class APIRouter:
    """
    Main router for handling incoming API requests.
    """
    def __init__(self):
        self.routes = {}

    def add_route(self, path: str, handler: callable) -> None:
        """
        Registers a new route handler.

        Args:
            path: The URL path for the route.
            handler: The function to handle the request.
        """
        self.routes[path] = handler

    def handle_request(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes an incoming request.

        Args:
            path: The requested URL path.
            payload: The request body payload.

        Returns:
            A dictionary containing the response.
        """
        if path in self.routes:
            return self.routes[path](payload)
        return {"error": "Route not found", "status": 404}
