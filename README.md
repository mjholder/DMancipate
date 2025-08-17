# DMancipate - AI Dungeon Master

A Flask application that provides a unified API interface for different LLM providers through a simplified client architecture. Includes a lightweight, independent CLI client for easy interaction.

## ✨ Features

- **Multi-LLM Provider Support**: OpenAI and LangChain (OpenAI, Ollama) clients
- **Unified Configuration**: Single set of environment variables for all providers
- **LangChain Integration**: Access to multiple providers through LangChain unified interface  
- **Streaming Support**: Real-time response streaming for all providers
- **Independent CLI Client**: Lightweight command-line interface separate from server code

## 🚀 Quick Start

### Installation

1. Create a virtual environment:

```bash
uv venv
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

3. Install dependencies
```bash
uv pip install -e .
```

### Run the Application

```bash
flask run
```

The application will be available at `http://localhost:5000`

## ⚙️ Configuration

The application uses environment variables for configuration. Set the appropriate variables based on your LLM provider.

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `LLM_CLIENT_TYPE` | LLM client type to use. (openai, langchain) | Yes | - |
| `SUMMARY_PROMPT` | System prompt for the assistant | No | `"You are a helpful assistant."` |

#### Unified Inference Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `INFERENCE_API_KEY` | API key for the inference provider | Yes | - |
| `INFERENCE_MODEL_NAME` | Model name to use | No | `"gpt-3.5-turbo"` |
| `INFERENCE_BASE_URL` | Custom base URL for API endpoint | No | - |
| `INFERENCE_TEMPERATURE` | Response randomness (0.0-1.0, 0.0=deterministic) | No | `0.7` |
| `INFERENCE_MAX_TOKENS` | Maximum tokens to generate in response | No | `2048` |

#### LangChain Specific Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `LANGCHAIN_PROVIDER` | LangChain provider type (openai, ollama) | When using LangChain | `"openai"` |

#### Legacy OpenAI Configuration (Optional)

| Variable | Description | Required | Used When |
|----------|-------------|----------|-----------|
| `OPENAI_API_KEY` | API key for OpenAI service (fallback) | No* | When `INFERENCE_API_KEY` not set |
| `OPENAI_MODEL_NAME` | Model name (fallback) | No* | When `INFERENCE_MODEL_NAME` not set |
| `OPENAI_BASE_URL` | Custom base URL (fallback) | No* | When `INFERENCE_BASE_URL` not set |

*Note: These are fallback variables. Use `INFERENCE_*` variables for unified configuration.

## 🔧 Provider Configuration

The application supports three different LLM client configurations:

### Option 1: OpenAI Client

```bash
export LLM_CLIENT_TYPE="openai"
export INFERENCE_API_KEY="your-api-key"
export INFERENCE_MODEL_NAME="gpt-4"
export INFERENCE_BASE_URL="https://api.openai.com/v1"  # Optional
export INFERENCE_TEMPERATURE="0.7"  # Optional
export INFERENCE_MAX_TOKENS="2048"  # Optional
export SUMMARY_PROMPT="You are a helpful assistant."
```

**Requirements:**
- OpenAI API key

### Option 2: LangChain with OpenAI

```bash
export LLM_CLIENT_TYPE="langchain"
export LANGCHAIN_PROVIDER="openai"
export INFERENCE_API_KEY="your-openai-api-key"
export INFERENCE_MODEL_NAME="gpt-4"
export INFERENCE_TEMPERATURE="0.7"  # Optional
export INFERENCE_MAX_TOKENS="2048"  # Optional
export SUMMARY_PROMPT="You are a helpful assistant."
```

**Requirements:**
- OpenAI API key

### Option 3: LangChain with Ollama

```bash
export LLM_CLIENT_TYPE="langchain"
export LANGCHAIN_PROVIDER="ollama"
export INFERENCE_MODEL_NAME="llama3.2"
export INFERENCE_BASE_URL="http://localhost:11434"
export INFERENCE_TEMPERATURE="0.7"  # Optional
export SUMMARY_PROMPT="You are a helpful assistant."
```

**Requirements:**
- Ollama running locally or remotely

## 📦 Installation

The application includes all LangChain dependencies by default:

```bash
# Install all dependencies (includes LangChain support)
pip install -e .
```

This includes support for:
- OpenAI through LangChain (`langchain-openai`)
- Ollama through LangChain (`langchain-ollama`)

## Bonfire Deployment

The application is prepared to deploy on ephemeral cluster through bonfire

```
bonfire deploy DMancipate --local-config-path {application_path}/bonfire-config.yaml
```

Also you can copy the content of `bonfire-config.yaml` into your local bonfire configuration to avoid use `--local-config-path`

## 🚢 OpenShift Deployment

The application includes an OpenShift template for easy deployment with configurable parameters.

### Template Parameters

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| `MEMORY_REQUEST` | Memory request for the API pods | `"512Mi"` |
| `MEMORY_LIMIT` | Memory limit for the API pods | `"1Gi"` |
| `CPU_REQUEST` | CPU request for the API pods | `"250m"` |
| `CPU_LIMIT` | CPU limit for the API pods | `"500m"` |
| `LLM_CLIENT_TYPE` | Type of LLM client (openai, langchain) | `"langchain"` |
| `LANGCHAIN_PROVIDER` | LangChain provider (openai, ollama) | `"openai"` |
| `INFERENCE_MODEL_NAME` | Model name for inference | `"mistral-small-24b-w8a8"` |
| `INFERENCE_BASE_URL` | Base URL for inference API | Custom endpoint |
| `INFERENCE_TEMPERATURE` | Response randomness (0.0-1.0) | `"0.7"` |
| `INFERENCE_MAX_TOKENS` | Maximum tokens to generate | `"2048"` |
| `SUMMARY_PROMPT` | System prompt for the AI assistant | `"You are a helpful assistant."` |

### Deployment Examples

#### Deploy with Default Values
```bash
oc process -f templates/service-template.yaml | oc apply -f -
```

#### Deploy with Custom Configuration
```bash
oc process -f templates/service-template.yaml \
  -p LLM_CLIENT_TYPE="openai" \
  -p INFERENCE_MODEL_NAME="gpt-4" \
  -p INFERENCE_TEMPERATURE="0.8" \
  -p INFERENCE_MAX_TOKENS="1024" \
  -p SUMMARY_PROMPT="You are an expert assistant." \
  | oc apply -f -
```

#### Deploy for Ollama Usage
```bash
oc process -f templates/service-template.yaml \
  -p LLM_CLIENT_TYPE="langchain" \
  -p LANGCHAIN_PROVIDER="ollama" \
  -p INFERENCE_MODEL_NAME="llama3.2" \
  -p INFERENCE_BASE_URL="http://ollama-service:11434" \
  -p MEMORY_LIMIT="2Gi" \
  | oc apply -f -
```

#### Deploy for Production Workload
```bash
oc process -f templates/service-template.yaml \
  -p MEMORY_REQUEST="1Gi" \
  -p MEMORY_LIMIT="2Gi" \
  -p CPU_REQUEST="500m" \
  -p CPU_LIMIT="1000m" \
  -p INFERENCE_MODEL_NAME="gpt-4" \
  -p INFERENCE_TEMPERATURE="0.5" \
  | oc apply -f -
```

### Template Management

#### View Available Parameters
```bash
oc process --parameters -f templates/service-template.yaml
```

#### Process Template without Applying
```bash
oc process -f templates/service-template.yaml \
  -p LLM_CLIENT_TYPE="openai" \
  -p INFERENCE_MODEL_NAME="gpt-4"
```

#### Update Existing Deployment
```bash
oc process -f templates/service-template.yaml \
  -p INFERENCE_TEMPERATURE="0.9" \
  | oc apply -f -
```

### Secret Configuration

The template creates a secret with the API key. Update the secret with your actual API key:

```bash
# Create or update the secret
oc create secret generic DMancipate-secret \
  --from-literal=INFERENCE_API_KEY="your-actual-api-key" \
  --dry-run=client -o yaml | oc apply -f -

# Or patch existing secret
oc patch secret DMancipate-secret \
  -p '{"data":{"INFERENCE_API_KEY":"'$(echo -n "your-actual-api-key" | base64)'"}}'
```

### Monitoring and Health Checks

The deployment includes:
- **Liveness Probe**: Checks `/health` endpoint every 10 seconds
- **Readiness Probe**: Checks `/health` endpoint every 5 seconds
- **Resource Limits**: Configurable CPU and memory limits
- **Security Context**: Runs as non-root user

### Accessing the Application

After deployment, the application will be available through the OpenShift route:

```bash
# Get the route URL
oc get route DMancipate -o jsonpath='{.spec.host}'

# Test the health endpoint
curl https://$(oc get route DMancipate -o jsonpath='{.spec.host}')/health

# Test the chat endpoint
curl -X POST https://$(oc get route DMancipate -o jsonpath='{.spec.host}')/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?", "enable_stream": "False"}'
```

## 💻 CLI Interface

DMancipate includes a lightweight command-line interface for easy interaction with your DM chatbot. The CLI is completely separate from the server code and only requires basic HTTP client dependencies.

### Installation

The CLI is available as an optional component. You can install it along with the main package:

```bash
# Install the main package with CLI support
uv pip install -e ".[cli]"

# Or install everything for development
uv pip install -e ".[cli,dev]"
```

**Note**: The CLI (`dmancipate_cli`) is independent of the main DMancipate server package and only requires `requests` for HTTP communication.

### Usage

```bash
dmancipate <action> <prompt> [options]
```

**Available Actions:**
- `talk` - General conversation with the DM
- `attack` - Describe an attack action
- `skill_check` - Request a skill check
- `use_item` - Use an item from inventory
- `look` - Examine surroundings or objects
- `pick_up` - Pick up items
- `ask` - Ask the DM questions about rules/stats
- `reset` - Delete all campaign history (no prompt required)

**Options:**
- `--host` - API server host (default: localhost)
- `--port` - API server port (default: 5000)
- `--check-health` - Check if API server is running

### Examples

```bash
# Start a conversation with the DM
dmancipate talk "Hello DM, I'm a level 1 rogue entering a tavern"

# Make an attack
dmancipate attack "I swing my short sword at the goblin"

# Make a skill check
dmancipate skill_check "I try to pick the lock on the treasure chest"

# Look around
dmancipate look "I examine the mysterious door for traps"

# Ask about game mechanics
dmancipate ask "What are the stats for a goblin warrior?"

# Use an item
dmancipate use_item "I drink a healing potion"

# Pick up items
dmancipate pick_up "I take the gold coins from the table"

# Reset campaign history (deletes all game history)
dmancipate reset

# Check if the API server is running
dmancipate talk "test" --check-health

# Connect to a remote server
dmancipate talk "Hello" --host api.mydmserver.com --port 8080
```

### Prerequisites

The CLI requires the DMancipate API server to be running. Start the server first:

```bash
flask run
```

Then use the CLI from another terminal to interact with your DM chatbot.

## 📡 API Endpoints

### Health Check

Check if the application is running:

```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "message": "HCM AI Sample App is running!"
}
```

### Chat API

#### Reset Campaign History

Delete all campaign history from the game:

```bash
curl -X DELETE http://localhost:5000/chat
```

**Response:**
```json
{
  "message": "Campaign history reset successfully"
}
```

#### Non-Streaming Chat

Send a message and get a complete response:

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is artificial intelligence?",
    "enable_stream": "False"
  }'
```

**Response:**
```json
{
  "result": "Artificial intelligence (AI) is a branch of computer science..."
}
```

#### Streaming Chat

Send a message and get a streamed response:

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a short story about space exploration",
    "enable_stream": "True"
  }'
```

**Response:** Stream of JSON objects:
```json
{"content": "In"}
{"content": " the"}
{"content": " year"}
{"content": " 2150..."}
```

### Request Parameters

#### For Chat Requests (POST /chat)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | The message to send to the LLM |
| `enable_stream` | string | Yes | `"True"` for streaming, `"False"` for complete response |
| `action` | string | Yes | Action type: "talk", "attack", "skill_check", "use_item", "look", "pick_up", "ask" |

#### For Reset Requests (DELETE /chat)

No parameters required. This endpoint deletes all documents from the "campaign-history" index.

## 📁 Project Structure

The project is organized into two independent components:

```
src/
├── DMancipate/           # Main API server package
│   ├── api.py           # Flask REST API endpoints
│   ├── llm/             # LLM client implementations
│   ├── assets/          # D&D reference materials
│   └── ingestion.py     # Document processing
└── dmancipate_cli/      # Independent CLI client package  
    ├── __init__.py      # CLI package metadata
    └── cli.py           # Command-line interface implementation
```

**Key Separation Benefits:**
- 🔗 **Independent**: CLI doesn't import or depend on server code
- 🪶 **Lightweight**: CLI only requires `requests` (no Flask, LLM libraries, etc.)
- 🚀 **Deployable**: Server and CLI can be deployed/distributed separately
- 🔧 **Maintainable**: Clear separation of client and server concerns

## 🛠️ Architecture

The application uses a unified client architecture that abstracts different LLM providers:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask API     │    │    LLM Client   │    │   LLM Provider  │
│                 │    │                 │    │                 │
│  ┌─────────────┐│    │  ┌─────────────┐│    │  ┌─────────────┐│
│  │ ChatApi     ││────│  │ llm.client  ││────│  │ OpenAI      ││
│  └─────────────┘│    │  └─────────────┘│    │  │ LangChain   ││
└─────────────────┘    └─────────────────┘    │  │ ├─OpenAI   ││
                                              │  │ └─Ollama   ││
                                              │  └─────────────┘│
                                              └─────────────────┘
```

### Key Components

- **Flask API**: Handles HTTP requests and responses via ChatApi
- **LLM Client**: Unified interface (`llm.client`) for different LLM providers
- **LLM Providers**: Support for OpenAI and LangChain (OpenAI/Ollama)

### Features

- ✅ **Unified Interface**: Same API regardless of LLM provider type
- ✅ **Unified Configuration**: Single set of environment variables across providers
- ✅ **Streaming Support**: Real-time response streaming for all providers
- ✅ **Multiple Client Types**: OpenAI and LangChain (multi-provider)
- ✅ **LangChain Integration**: Access to OpenAI, Ollama through LangChain
- ✅ **Flexible Model Support**: Local models via Ollama, cloud models via APIs
- ✅ **Error Handling**: Comprehensive error handling and validation

## 🧪 Testing

### Test with curl

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test chat endpoint
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?", "enable_stream": "False"}'
```

## 🚨 Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `500`: Internal Server Error (LLM provider error)

### Error Response Format

```json
{
  "error": "Error description here"
}
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.