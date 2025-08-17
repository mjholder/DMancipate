
"""
LangChain Client for HCM AI Sample App.

This module provides a unified interface for multiple LLM providers through LangChain,
supporting OpenAI and Ollama providers with configurable parameters.
"""

import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore
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
        self.history = []

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

    def _get_rules_context(self, user_query):
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
        vectorstore = PineconeVectorStore(index_name="dnd-vector", embedding=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        docs = retriever.invoke(user_query)
        print(f"rules context: {docs}")
        return "\n".join([doc.page_content for doc in docs])

    def _get_monster_context(self, user_query):
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
        vectorstore = PineconeVectorStore(index_name="monster-vector", embedding=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
        docs = retriever.invoke(user_query)
        print(f"monster context: {docs}")
        return "\n".join([doc.page_content for doc in docs])

    def _get_campaign_context(self, user_query):
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
        history_vectorstore = PineconeVectorStore(index_name="campaign-history", embedding=embeddings)
        retriever = history_vectorstore.as_retriever(search_kwargs={"k": 2})
        history_docs = retriever.invoke(user_query)
        print(f"campaign history: {history_docs}")
        return "\n".join([doc.page_content for doc in history_docs])
    def _get_campaign_modules_context(self, user_query):
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
        module_vectorstore = PineconeVectorStore(index_name="campaign-modules", namespace="HoardDragonQueen", embedding=embeddings)
        module_retriever = module_vectorstore.as_retriever(search_kwargs={"k": 2})
        module_docs = module_retriever.invoke(user_query)
        print(f"campaign modules: {module_docs}")
        return "\n".join([doc.page_content for doc in module_docs])


    def _update_campaign_vector_store(self, response):
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
        vectorstore = PineconeVectorStore(index_name="campaign-history", embedding=embeddings)
        print(f"updating campaign history: {response}")
        vectorstore.add_texts([response])

    def _get_contexts(self, action, prompt):
        contexts = [self._get_campaign_context(prompt)]
        action_prompt = ""
        if action == "ask":
            action_prompt = "The player is asking you the DM a question. The context you are given is for your eyes only. You should not reveal this information to the player directly. If you see something like 1d4 or 1d6, that means you need to determine what the number is. Don't tell the player. If the action requires a skill check tell the player to do that check before allowing the action to continue."
            contexts.append(self._get_campaign_modules_context(prompt))
        if action == "talk":
            action_prompt = "The player is talking to an NPC. Determine the NPC's personality and provide a concise answer but only reveal information if the player asks for it directly. If the user is required to pass a deception or persuasion check, tell the player to do that check before allowing the action to continue."
            contexts.append(self._get_campaign_modules_context(prompt))
        elif action == "attack":
            action_prompt = "The player is attacking a monster. Provide a concise answer but only reveal information that is relevant to the player's attack. Before allowing the attack to happen, make sure the player specifies their attack roll and make sure it is greater than or equal to the monsters AC. If the attack is successful, provide a concise answer on what happens as a result of the attack."
            contexts.append(self._get_monster_context(prompt))
        elif action == "skill_check":
            action_prompt = "The player is performing a skill check. Provide a concise, one or two sentence answer on what the player should do to achieve the goal of the skill check. Include the revelant modifiers the player needs to add to the roll for the skill check. This should be as simple as 'Roll a Stealth check and add your wisdom modifier'"
            contexts.append(self._get_rules_context(prompt))
        elif action == "use_skill":
            action_prompt = "The player is using a skill. Provide a concise response to what happens as a result of the skill being used. A key part of determining the outcome is the roll number associated with the skill. Check for a difficulty number and compare it to the roll number. If the roll number is higher than or equal to the difficulty number, the skill was successful. If the roll number is lower than the difficulty number, the skill was not successful."
            contexts.append(self._get_campaign_modules_context(prompt))
        elif action == "use_item":
            action_prompt = "The player is using an item. Provide a concise answer but only reveal information that is relevant to the player's item use. If the item requires a skill check, tell the player to do that check before allowing the action to continue."
            contexts.append(self._get_rules_context(prompt))
        elif action == "look":
            action_prompt = "The player is looking around. Provide a concise description on what the player is looking at. It should only be a few sentences."
            contexts.append(self._get_campaign_modules_context(prompt))
        elif action == "pick_up":
            action_prompt = "The player is picking up an item. Provide a concise one sentence response the player picking up the item."
            contexts.append(self._get_campaign_modules_context(prompt))
        elif action == "review":
            action_prompt = "The player is reviewing the campaign history. Provide a concise summary of the campaign history."
        return "\n".join(contexts), action_prompt


    def chat(self, prompt, enable_stream=False, action=None):
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

        contexts, action_prompt = self._get_contexts(action, prompt)
        quest_context = self._get_campaign_context(prompt)
        user_query = f"""
        {self.instructions}
        Here is what the player wants to do:
        {prompt}
        Only provide information that is mentioned in the following context. If it's not in that context then the player would not know about it:
        {quest_context}

        {action_prompt}
        The following are relevant information to the player's action or question.
        {contexts}
        """
        print(user_query)
        try:
            if enable_stream:
                response = self.llm.stream(user_query)
            else:
                response = self.llm.invoke(user_query)

            self.history.append((prompt, response.content))
            if action != "review":
                self._update_campaign_vector_store(response.content)
            return response
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
                elif isinstance(chunk, dict):
                    text = (
                        chunk.get("answer")
                        or chunk.get("content")
                        or chunk.get("result")
                        or chunk.get("output_text")
                        or ""
                    )
                    if text:
                        event_data = {"content": text}
                        yield f"{json.dumps(event_data)}\n"
                elif isinstance(chunk, str) and chunk:
                    event_data = {"content": chunk}
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
        if isinstance(response, dict):
            if isinstance(response.get("answer"), str):
                return response["answer"]
            if isinstance(response.get("result"), str):
                return response["result"]
            if isinstance(response.get("output_text"), str):
                return response["output_text"]
        return str(response)