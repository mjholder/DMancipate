
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
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(user_query)
        print(f"rules context: {docs}")
        raw_context = "\n".join([doc.page_content for doc in docs])
        processed_context = self.llm.invoke(f"""
        The user's query is {user_query}. Find the most relevant information from the following context and summarize it into a bullet point list.
        {raw_context}
        """)
        return processed_context.content

    def _get_monster_context(self, user_query):
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
        vectorstore = PineconeVectorStore(index_name="monster-vector", embedding=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(user_query)
        print(f"monster context: {docs}")
        raw_context = "\n".join([doc.page_content for doc in docs])
        processed_context = self.llm.invoke(f"""
        The user's query is {user_query}. Find the most relevant information from the following context and summarize it into a bullet point list.
        {raw_context}
        """)
        return processed_context.content

    def _get_campaign_context(self, user_query):
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
        history_vectorstore = PineconeVectorStore(index_name="campaign-history", embedding=embeddings)
        retriever = history_vectorstore.as_retriever(search_kwargs={"k": 10})
        history_docs = retriever.invoke(user_query)
        print(f"campaign history: {history_docs}")
        if len(history_docs) == 0:
            return "No campaign history found. This is the start of the campaign."
        raw_context = "\n".join([doc.page_content for doc in history_docs])
        processed_context = self.llm.invoke(f"""
        The user's query is {user_query}. Find the most relevant information from the following context and summarize it into a bullet point list.
        {raw_context}
        """)
        return processed_context.content

    def _get_campaign_modules_context(self, user_query):
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
        module_vectorstore = PineconeVectorStore(index_name="campaign-modules", namespace="HoardDragonQueen", embedding=embeddings)
        module_retriever = module_vectorstore.as_retriever(search_kwargs={"k": 4})
        module_docs = module_retriever.invoke(user_query)
        print(f"campaign modules: {module_docs}")
        raw_context = "\n".join([doc.page_content for doc in module_docs])
        processed_context = self.llm.invoke(f"""
        The user's query is {user_query}. Find the most relevant information from the following context and summarize it into a bullet point list.
        {raw_context}
        """)
        return processed_context.content


    def _update_campaign_vector_store(self, response):
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
        vectorstore = PineconeVectorStore(index_name="campaign-history", embedding=embeddings)
        print(f"updating campaign history: {response}")
        vectorstore.add_texts([response])

    def _get_contexts(self, action, prompt):
        if action == "start":
            return """
            The player is starting a new campaign. Choose one of the following character hooks. This will be how you introduce the campaign to the player.
            The Story Thus Far . . .
                As the Cult of the Dragon has grown bolder, its actions
                have drawn attention. Your character has stumbled into
                the Cult’s scheme in some manner or has a connection
                to dragons. The following tables provide you with bonds
                tailored to this campaign. Use them in place of or in
                addition to the ones you selected from (or created for)
                your background.
                Bond (d10)
                1. Leosin Erlanthar, a wandering monk, once saved your life.
                He’s sent urgent word for you to meet him in a small town
                called Greenest. Looks like it’s time to pay off that debt.
                2. When an orc raid drove your family from your home, the
                people of Greenest took you in. Anyone who threatens
                Greenest is your sworn enemy.
                3. Every five nights, you have a strange sequence of apocalyptic
                dreams. The world is destroyed by cold, choking fumes,
                lightning storms, waves of acid, and horrible fire. Each
                time, the dream ends with ten evil eyes glaring at you from
                the darkness. You feel a strange compulsion to travel to
                Greenest. Perhaps the answer to the riddle of your dreams
                awaits you there.
                4. Ontharr Frume, a crusading warrior and champion of good,
                is your friend and mentor. He has asked you to travel to
                Greenest in search of rumors of increasing dragon activity.
                5. You have heard rumors that your close childhood friend, a
                half-elf named Talis, has been kidnapped by a strange group
                of dragon cultists. Your investigations into the cult have
                led you to the town of Greenest. You must save her! (Talis
                appears as a villain in the full Hoard of the Dragon Queen
                adventure, so do not use this bond unless you plan on
                running the full adventure.)
                6. Being the grandchild of a renowned dragon slayer is usually
                a good way to impress people, but just last week a gang of
                ruffians attack you. You barely escaped with your life, but
                as you fled, the ruffians told you that the Cult of the Dragon
                never forgets and always avenges. You’re hoping to lie low in
                a sleepy little town called Greenest until this blows over.
                7. On his deathbed, your father confessed that he had become
                involved with a group called the Cult of the Dragon. They
                paid him to smuggle goods across the Sword Coast. Wracked
                by guilt, he begged you to investigate the cult and undo the
                evil he may have helped foster. He urged you to begin your
                search in a town called Greenest.
                8. The dragons destroyed everything you hold dear. They killed
                your family and destroyed your home. Now, with nothing
                but what you carry on your back and a horrid scar of the near
                fatal wounds you sustained in the attack, you seek revenge.
                9. You and your family were members of the Cult of the Dragon,
                until your rivals in the cult arranged to wipe you out. Though
                they slaughtered your kin, you survived, but they think
                you’re dead. Now is your chance for vengeance! Your hit
                list consists of three names: a human cultist named Frulam
                Mondath, a half-orc named Bog Luck, and a half-dragon
                named Rezmir. You have arrived in Greenest, knowing it’s
                next on the cult’s list of targets.
                10. You have a secret. You once were a gold dragon who served
                Bahamut. You were too proud and vain, to the point that
                Bahamut decided to teach you a lesson. You have been
                trapped in a weak, humanoid body, with your memories of
                your former life but a dim shadow. You remember only one
                thing with perfect clarity: Bahamut’s command to go into the
                world and prove your devotion to the cause of good. If you
                prove worthy, on your death you will return to his side in your
                true form.
            """
        contexts = []
        action_prompt = ""
        if action == "ask":
            action_prompt = "The player is asking you the DM a question. Decide what is going to happen next or answer the question based on the following context."
            contexts.append({"prompt": action_prompt, "context": self._get_campaign_modules_context(prompt)})
        if action == "talk":
            action_prompt = "The player is talking to an NPC. Determine the NPC's personality and provide a concise answer but only reveal information if the player asks for it directly. If the user is required to pass a deception or persuasion check, tell the player to do that check before allowing the action to continue."
            contexts.append({"prompt": action_prompt, "context": self._get_campaign_modules_context(prompt)})
        elif action == "attack":
            action_prompt = "The player is attacking a monster. Provide a concise answer but only reveal information that is relevant to the player's attack. Before allowing the attack to happen, make sure the player specifies their attack roll and make sure it is greater than or equal to the monsters AC. If the attack is successful, provide a concise answer on what happens as a result of the attack."
            contexts.append({"prompt": action_prompt, "context": self._get_monster_context(prompt)})
        elif action == "skill_check":
            action_prompt = "The player is performing a skill check. Provide a concise, one or two sentence answer on what the player should do to achieve the goal of the skill check. Include the revelant modifiers the player needs to add to the roll for the skill check. This should be as simple as 'Roll a Stealth check and add your wisdom modifier'"
            contexts.append({"prompt": action_prompt, "context": self._get_rules_context(prompt)})
        elif action == "use_skill":
            action_prompt = "The player is using a skill. Provide a concise response to what happens as a result of the skill being used. A key part of determining the outcome is the roll number associated with the skill. Check for a difficulty number and compare it to the roll number. If the roll number is higher than or equal to the difficulty number, the skill was successful. If the roll number is lower than the difficulty number, the skill was not successful."
            contexts.append({"prompt": action_prompt, "context": self._get_campaign_modules_context(prompt)})
        elif action == "use_item":
            action_prompt = "The player is using an item. Provide a concise answer but only reveal information that is relevant to the player's item use. If the item requires a skill check, tell the player to do that check before allowing the action to continue."
            contexts.append({"prompt": action_prompt, "context": self._get_rules_context(prompt)})
        elif action == "look":
            action_prompt = "The player is looking around. Provide a concise description on what the player is looking at. It should only be a few sentences."
            contexts.append({"prompt": action_prompt, "context": self._get_campaign_modules_context(prompt)})
        elif action == "pick_up":
            action_prompt = "The player is picking up an item. Provide a concise one sentence response the player picking up the item."
            contexts.append({"prompt": action_prompt, "context": self._get_campaign_modules_context(prompt)})
        elif action == "review":
            action_prompt = f"The player is reviewing the campaign history. Provide a concise summary of the campaign history relevant to this prompt {prompt}."

        contexts.append({"prompt": "The following context is what the player has done so far and all they know about the campaign. Do not reveal any information that is not in this context.", "context": self._get_campaign_context(prompt)})
        return contexts


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
        
        contexts = self._get_contexts(action, prompt)
        user_query = f"""
        {self.instructions}
        Here is what the player wants to do:
        {prompt}
        Use the following context to help you answer the player's question:
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