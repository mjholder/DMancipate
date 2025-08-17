"""
Flask API endpoints for HCM AI Sample App.

This module defines the REST API endpoints for health checking and
chat functionality with LLM providers, supporting both streaming
and non-streaming responses.
"""

import os
from .llm.llm_client import llm
from flask import request, jsonify, Response, stream_with_context
from flask_restful import Resource
from pinecone import Pinecone


class HealthCheckApi(Resource):
    """
    Health check endpoint for application monitoring.
    
    Provides a simple endpoint to verify that the application
    is running and responsive.
    """
    
    def get(self):
        """
        Health check endpoint.
        
        Returns a simple JSON response indicating the application status.
        
        Returns:
            tuple: JSON response and HTTP status code (200)
                  {"message": "HCM AI Sample App is running!"}
        """
        return {"message": "HCM AI Sample App is running!"}, 200


class ChatApi(Resource):
    """
    Chat API endpoint for LLM interactions.
    
    Handles chat requests with support for both streaming and non-streaming
    responses across different LLM providers (OpenAI, LangChain, Llama Stack).
    """
    def __init__(self):
        self.allowed_actions = ["talk", "attack", "skill_check", "use_item", "look", "pick_up", "ask", "review", "use_skill"]

    def post(self):
        """
        Handle chat completion requests.
        
        Processes incoming chat requests with support for both streaming
        and non-streaming responses. Validates request parameters and
        forwards the request to the configured LLM client.
        
        Request JSON format:
            {
                "prompt": "User message to send to the LLM",
                "enable_stream": "True" or "False" (string, case-insensitive),
                "action": "talk", "attack", "skill_check", "use_item", "look", "pick_up" (string, case-insensitive)
            }
        
        Returns:
            For streaming (enable_stream=True):
                Response: Server-Sent Events stream with JSON chunks
                         Each chunk: {"content": "text_fragment"}
            
            For non-streaming (enable_stream=False):
                JSON: {"result": "complete_response_text"}
            
            For errors:
                JSON: {"error": "error_description"} with appropriate HTTP status
        """
        try:
            prompt, enable_stream, action = self._parse_parameters()
        except ValueError as e:
            return {"error": str(e)}, 400

        try:
            response = llm.client.chat(prompt, enable_stream, action)

            if enable_stream:
                return Response(stream_with_context(llm.client.streaming_response(response)), mimetype="application/json")
            else:
                content = llm.client.await_response(response)
                return jsonify({"result": content})
        except Exception as e:
            return {"error": str(e)}, 500

    def delete(self):
        """
        Reset campaign history by deleting all documents from the campaign-history index.
        
        This endpoint removes all game history stored in the Pinecone "campaign-history" 
        index, effectively resetting the campaign to a fresh state.
        
        Returns:
            JSON: {"message": "Campaign history reset successfully"} on success
            JSON: {"error": "error_description"} with appropriate HTTP status on error
        """
        try:
            # Initialize Pinecone client
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                return {"error": "Pinecone API key not configured"}, 500
            
            pc = Pinecone(api_key=api_key)
            index = pc.Index("campaign-history")
            
            # Delete all documents from the campaign-history index
            index.delete(delete_all=True)
            
            return {"message": "Campaign history reset successfully"}, 200
            
        except Exception as e:
            return {"error": f"Failed to reset campaign history: {str(e)}"}, 500

    def _parse_parameters(self):
        """
        Parse and validate request parameters.
        
        Extracts and validates the 'prompt' and 'enable_stream' parameters
        from the JSON request body.
        
        Returns:
            tuple: (prompt: str, enable_stream: bool)
            
        Raises:
            ValueError: If JSON body is missing, parameters are invalid,
                       or required parameters are not provided
        """

        data = request.get_json()

        if not data:
            raise ValueError ("Missing JSON body")

        prompt = data.get("prompt")
        enable_stream = data.get("enable_stream", "False")
        action = data.get("action")

        if action not in self.allowed_actions:
            raise ValueError (f"Invalid action: {action}")
        if enable_stream not in ("True", "False", "true", "false"):
            raise ValueError (f"Invalid boolean value for 'enable_stream': {enable_stream}")
        if prompt is None:
            raise ValueError ("Missing 'prompt' parameter")

        return prompt, self._parse_bool(enable_stream), action

    def _parse_bool(self, value):
        """
        Parse string boolean values to actual boolean.
        
        Converts string representations of boolean values to actual boolean types.
        Accepts both "True"/"False" and "true"/"false" formats.
        
        Args:
            value (str): String representation of boolean ("True", "False", "true", "false")
            
        Returns:
            bool: True if value is "True" or "true", False otherwise
        """
        return value == "True" or value == "true"