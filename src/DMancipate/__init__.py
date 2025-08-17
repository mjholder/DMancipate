"""
HCM AI Sample App - Flask Application Factory.

This module provides the Flask application factory and initialization
for a multi-LLM provider chat application with unified API interface.
"""

import logging

from .api import HealthCheckApi, ChatApi
from flask import Flask
from flask_cors import CORS
from flask_restful import Api


def create_app():
    """
    Create and configure the Flask application.
    
    Sets up the Flask app with CORS support, REST API endpoints,
    and logging configuration for the HCM AI Sample App.
    
    Returns:
        Flask: Configured Flask application instance with:
               - CORS enabled for cross-origin requests
               - REST API endpoints for health check and chat
               - Logging configured for application monitoring
    """
    app = Flask("DMancipate")
    app.config["CORS_HEADER"] = "Content-Type"
    CORS(app)

    api = Api(app)
    _initialize_routes(api)

    logger = logging.getLogger("DMancipate")
    logger.info("HCM AI Sample App running!")

    return app


def _initialize_routes(api: Api):
    """
    Initialize API routes for the application.
    
    Registers REST API endpoints with the Flask-RESTful API instance.
    
    Args:
        api (Api): Flask-RESTful API instance to register routes with
        
    Routes:
        GET /health: Health check endpoint for monitoring
        POST /chat: Chat completion endpoint for LLM interactions
    """
    api.add_resource(HealthCheckApi, "/health", methods=["GET"])
    api.add_resource(ChatApi, "/chat", methods=["POST", "DELETE"])


# Global app instance for direct import - supports various deployment scenarios
app = create_app()