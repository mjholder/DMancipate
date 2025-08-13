"""
LLM Client Factory for HCM AI Sample App.

This module provides a factory pattern for creating and managing different
LLM client instances based on configuration, supporting OpenAI, LangChain,
and Llama Stack providers.
"""

from . import config as conf


class LlmClient:
    """
    LLM client factory and manager.
    
    This class implements a factory pattern to create and manage different
    LLM client instances based on the LLM_CLIENT_TYPE configuration.
    It ensures only one client instance is created per application lifecycle.
    
    Attributes:
        client: The initialized LLM client instance (OpenAI, LangChain, or Llama Stack)
        client_type: String identifier of the client type being used
    """

    client = None
    client_type = None

    def __init__(self):
        """
        Initialize the LLM client factory.
        
        Creates the appropriate client instance based on LLM_CLIENT_TYPE
        configuration and stores it for reuse.
        """
        self.client, self.client_type = self._initialize_client()

    def _initialize_client(self):
        """
        Initialize the LLM client based on configuration.
        
        Creates the appropriate client instance (OpenAI, LangChain, or Llama Stack)
        based on the LLM_CLIENT_TYPE environment variable.
        
        Returns:
            tuple: (client_instance, client_type_string)
            
        Raises:
            Exception: If client type is unsupported
            ValueError: If client initialization fails
        """
        if self.client == None or self.client_type == None:
            try:
                client_type = conf.LLM_CLIENT_TYPE
                if client_type == "openai":
                    client = self._create_openai_client()
                elif client_type == "langchain":
                    client = self._create_langchain_client()
                else:
                    raise Exception(f"{client_type} client type is not supported. Available client types: openai, langchain")
                return client, client_type
            except Exception as e:
                raise ValueError(f"Error initializing LLM client: {str(e)}")

    def _create_openai_client(self):
        """
        Create and configure the OpenAI client.
        
        Imports and initializes the OpenAI client with unified configuration
        supporting both direct OpenAI API and OpenAI-compatible endpoints.
        
        Returns:
            OpenAIClient: Configured OpenAI client instance
            
        Raises:
            ImportError: If OpenAI dependencies are not available
            ValueError: If OpenAI client initialization fails
        """
        try:
            from .open_ai_client import OpenAIClient
            return OpenAIClient()
            
        except ImportError:
            raise ValueError("OpenAI client not available.")

    def _create_langchain_client(self):
        """
        Create and configure the LangChain client.
        
        Imports and initializes the LangChain client with support for multiple
        providers (OpenAI, Ollama) through LangChain's unified interface.
        
        Returns:
            LangChainClient: Configured LangChain client instance
            
        Raises:
            ImportError: If LangChain dependencies are not available
            ValueError: If LangChain client initialization fails
        """
        try:
            from .langchain_client import LangChainClient
            return LangChainClient()
            
        except ImportError:
            raise ValueError("LangChain client not available.")


# Global LLM client instance - singleton pattern for application-wide use
llm = LlmClient()