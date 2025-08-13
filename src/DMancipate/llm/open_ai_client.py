"""
OpenAI Client for HCM AI Sample App.

This module provides a direct interface to OpenAI's API with support for
chat completions and streaming responses using configurable parameters.
"""

import json

from openai import OpenAI
from . import config as conf


class OpenAIClient:
    """
    OpenAI client implementation for direct API access.
    
    This client provides direct access to OpenAI's chat completion API
    with support for both streaming and non-streaming responses.
    
    Attributes:
        client: The OpenAI API client instance
        model: The model name to use for completions
        instructions: System prompt for the AI assistant
    """
    def __init__(self):
        """
        Initialize the OpenAI client.
        
        Sets up the OpenAI API client using unified configuration with
        fallback to legacy OpenAI-specific environment variables.
        
        Raises:
            ValueError: If no API key is provided in configuration
        """
        # Use unified configuration with fallback to legacy
        api_key = conf.INFERENCE_API_KEY or conf.OPENAI_API_KEY
        base_url = conf.INFERENCE_BASE_URL or conf.OPENAI_BASE_URL
        
        if not api_key:
            raise ValueError("API key is required. Set INFERENCE_API_KEY or OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )
        self.model = conf.INFERENCE_MODEL_NAME or conf.OPENAI_MODEL_NAME
        self.instructions = conf.SUMMARY_PROMPT

    def chat(self, prompt, enable_stream=False):
        """
        Send a chat message to OpenAI's API.
        
        Processes the user prompt with system instructions and sends it
        to OpenAI's chat completion endpoint with configurable parameters.
        
        Args:
            prompt (str): The user's message to send to the LLM
            enable_stream (bool): Whether to enable streaming response.
                                If True, returns a generator for real-time streaming.
                                If False, returns complete response after processing.
            
        Returns:
            openai.ChatCompletion: For non-streaming, returns complete response object.
                                  For streaming, returns generator yielding chunks.
                                  
        Raises:
            Exception: If OpenAI API request fails or configuration is invalid
        """
        messages = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=enable_stream,
                temperature=conf.INFERENCE_TEMPERATURE,
                max_tokens=conf.INFERENCE_MAX_TOKENS
            )
            return response
        except Exception as e:
            print(f"Error creating OpenAI chat completion: {e}")
            raise

    def streaming_response(self, response):
        """
        Process streaming response from OpenAI into JSON format.
        
        Converts OpenAI streaming chunks into standardized JSON format
        for consistent API responses across all client types.
        
        Args:
            response: OpenAI streaming generator that yields completion chunks
            
        Yields:
            str: JSON-formatted strings containing response content.
                 Each yield contains: {"content": "chunk_text"}
                 On error: {"content": "", "error": "error_message"}
        """
        try:
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    event_data = {"content": content}
                    yield f"{json.dumps(event_data)}\n"
        except Exception as e:
            fallback_data = {
                "content": "",
                "error": f"streaming error: {str(e)}"
            }
            yield f"{json.dumps(fallback_data)}\n"

    def await_response(self, response):
        """
        Extract content from non-streaming OpenAI response.
        
        Processes the complete OpenAI chat completion response and extracts
        the text content for API consumption.
        
        Args:
            response: OpenAI ChatCompletion response object containing the LLM output
            
        Returns:
            str: The extracted text content from the first choice in the response
        """
        return response.choices[0].message.content