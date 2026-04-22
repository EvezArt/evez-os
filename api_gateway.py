#!/usr/bin/env python3
"""
API Gateway - Route and transform API calls
"""
from typing import Dict

class APIGateway:
    def __init__(self):
        self.routes = {}
        
    def route(self, path: str, handler):
        """Register route"""
        self.routes[path] = handler
        
    def call(self, path: str, data: Dict):
        """Call route"""
        handler = self.routes.get(path)
        if handler:
            return handler(data)
        return {"error": "route not found"}
    
    def transform(self, data, input_schema, output_schema):
        """Transform data between schemas"""
        return data

if __name__ == "__main__":
    g = APIGateway()
    g.route("/test", lambda d: d)
    print(g.call("/test", {"test": "data"}))
