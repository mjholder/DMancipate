"""
Configuration module for HCM AI Sample App.

This module centralizes all configuration variables using environment variables,
providing unified configuration for all LLM providers and client types.
"""

import os

# =============================================================================
# System Configuration
# =============================================================================

# System prompt for the AI assistant
SUMMARY_PROMPT = os.getenv("SUMMARY_PROMPT", "You are a helpful agent")

# Llama Stack distribution configuration (legacy)
LLAMA_STACK_DISTRIBUTION = os.getenv("LLAMA_STACK_DISTRIBUTION", "starter")

# Dynamic model name for Llama Stack (legacy)
LLM_MODEL_NAME = None

# =============================================================================
# Unified Inference Configuration
# =============================================================================

# API key for the inference provider (OpenAI, custom endpoints, etc.)
INFERENCE_API_KEY = os.getenv("INFERENCE_API_KEY")

# Model name to use for inference (e.g., "gpt-4", "llama3.2")
INFERENCE_MODEL_NAME = os.getenv("INFERENCE_MODEL_NAME", "gpt-3.5-turbo")

# Custom base URL for API endpoints (optional)
INFERENCE_BASE_URL = os.getenv("INFERENCE_BASE_URL")

# Temperature for response randomness (0.0 = deterministic, 1.0 = very random)
INFERENCE_TEMPERATURE = float(os.getenv("INFERENCE_TEMPERATURE", "0.7"))

# Maximum number of tokens to generate in response
INFERENCE_MAX_TOKENS = int(os.getenv("INFERENCE_MAX_TOKENS", "2048"))

# =============================================================================
# LangChain Provider Configuration
# =============================================================================

# LangChain provider type: "openai" or "ollama"
LANGCHAIN_PROVIDER = os.getenv("LANGCHAIN_PROVIDER", "openai")

# =============================================================================
# Legacy OpenAI Configuration (Backward Compatibility)
# =============================================================================

# Legacy OpenAI API key (fallback when INFERENCE_API_KEY not set)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Legacy OpenAI model name (fallback when INFERENCE_MODEL_NAME not set)
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")

# Legacy OpenAI base URL (fallback when INFERENCE_BASE_URL not set)
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

# =============================================================================
# Client Selection
# =============================================================================

# LLM client type: "openai", "langchain", or "llama_stack"
LLM_CLIENT_TYPE = os.getenv("LLM_CLIENT_TYPE", "None")

# Dynamic model configuration
_enable_ollama = os.getenv("ENABLE_OLLAMA", "__disabled__")
_enable_vllm = os.getenv("ENABLE_VLLM", "__disabled__")
_safety_model = os.getenv("SAFETY_MODEL")
_vllm_model = os.getenv("VLLM_INFERENCE_MODEL")

if _enable_ollama != "__disabled__" and _safety_model:
    LLM_MODEL_NAME = f"{_enable_ollama}/{_safety_model}"
elif _enable_vllm != "__disabled__" and _vllm_model:
    LLM_MODEL_NAME = f"{_enable_vllm}/{_vllm_model}"
