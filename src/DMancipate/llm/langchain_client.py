
"""
LangChain Client for HCM AI Sample App.

This module provides a unified interface for multiple LLM providers through LangChain,
supporting OpenAI and Ollama providers with configurable parameters.
"""

import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from . import config as conf


class LangChainClient:
    """
    LangChain client implementation for multi-provider LLM access.
    
    This client abstracts different LLM providers (OpenAI, Ollama) through LangChain,
    providing a consistent interface for chat completions with streaming support.
    
    Attributes:
        llm: The initialized LangChain model instance
        instructions: System prompt for the AI assistant
    """
    def __init__(self):
        """
        Initialize the LangChain client.
        
        Sets up the LLM instance based on the configured provider and
        initializes the system instructions from configuration.
        """
        self.llm = self._initialize_llm()
        self.instructions = conf.SUMMARY_PROMPT

    def _initialize_llm(self):
        """
        Initialize the LangChain LLM based on provider configuration.
        
        Creates and configures the appropriate LangChain model instance
        (ChatOpenAI or ChatOllama) based on LANGCHAIN_PROVIDER setting.
        
        Returns:
            LangChain model instance: Configured ChatOpenAI or ChatOllama instance
            
        Raises:
            ValueError: If provider is unsupported or configuration is invalid
            ImportError: If required LangChain package is not installed
        """
        # Use LangChain specific provider configuration
        provider = conf.LANGCHAIN_PROVIDER.lower()
        api_key = conf.INFERENCE_API_KEY or conf.OPENAI_API_KEY
        model_name = conf.INFERENCE_MODEL_NAME or conf.OPENAI_MODEL_NAME
        base_url = conf.INFERENCE_BASE_URL or conf.OPENAI_BASE_URL
        
        try:
            if provider == "openai":
                from langchain_openai import ChatOpenAI
                if not api_key:
                    raise ValueError("API key is required. Set INFERENCE_API_KEY or OPENAI_API_KEY environment variable.")
                
                llm_kwargs = {
                    "model": model_name,
                    "api_key": api_key,
                    "temperature": conf.INFERENCE_TEMPERATURE,
                    "max_tokens": conf.INFERENCE_MAX_TOKENS
                }
                
                if base_url:
                    llm_kwargs["base_url"] = base_url
                
                return ChatOpenAI(**llm_kwargs)
                
            elif provider == "ollama":
                from langchain_ollama import ChatOllama
                return ChatOllama(
                    model=model_name or "llama3.2",
                    base_url=base_url or "http://localhost:11434",
                    temperature=conf.INFERENCE_TEMPERATURE
                )
                
            else:
                raise ValueError(f"Unsupported provider: {provider}. Supported providers: openai, ollama")
                
        except ImportError as e:
            raise ValueError(f"Required LangChain package not installed for provider '{provider}': {e}")

    def chat(self, prompt, enable_stream=False):
        """
        Send a chat message to the LLM using LangChain.
        
        Processes the user prompt with the configured system instructions
        and sends it to the LLM provider via LangChain.
        
        Args:
            prompt (str): The user's message to send to the LLM
            enable_stream (bool): Whether to enable streaming response.
                                If True, returns a generator for real-time streaming.
                                If False, returns complete response after processing.
            
        Returns:
            LangChain response: For non-streaming, returns AIMessage object.
                              For streaming, returns generator yielding chunks.
                              
        Raises:
            Exception: If LLM request fails or configuration is invalid
        """
        messages = [
            SystemMessage(content=self.instructions),
            HumanMessage(content=prompt)
        ]
        
        try:
            if enable_stream:
                return self.llm.stream(messages)
            else:
                return self.llm.invoke(messages)
        except Exception as e:
            print(f"Error creating LangChain chat completion: {e}")
            raise

    def streaming_response(self, response):
        """
        Process streaming response from LangChain into JSON format.
        
        Converts LangChain streaming chunks into standardized JSON format
        for consistent API responses across all client types.
        
        Args:
            response: LangChain streaming generator that yields message chunks
            
        Yields:
            str: JSON-formatted strings containing response content.
                 Each yield contains: {"content": "chunk_text"}
                 On error: {"content": "", "error": "error_message"}
        """
        try:
            for chunk in response:
                if hasattr(chunk, 'content') and chunk.content:
                    event_data = {"content": chunk.content}
                    yield f"{json.dumps(event_data)}\n"
        except Exception as e:
            fallback_data = {
                "content": "",
                "error": f"streaming error: {str(e)}"
            }
            yield f"{json.dumps(fallback_data)}\n"

    def await_response(self, response):
        """
        Extract content from non-streaming LangChain response.
        
        Processes the complete LangChain AIMessage response and extracts
        the text content for API consumption.
        
        Args:
            response: LangChain AIMessage response object containing the LLM output
            
        Returns:
            str: The extracted text content from the LLM response.
                 Returns string representation if content attribute is not available.
        """
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)