# OPENAI-FASTAPI-SERVER
This is a FastAPI server that mocks OpenAI API allowing you to develop customised API for most UI uses (e.g. [LibreChat](https://github.com/danny-avila/LibreChat)).

## Local server

```
pip install uv

uv pip sync requirements.txt

uv run app.py
```

## Run the server

```bash
sudo docker-compose up -d --build
```

## Test on the Libre-Chat

Create `librechat.yaml` in the `LibreChat` directory.

```yaml
# Configuration version (required)
version: 1.2.1

# Cache settings: Set to true to enable caching
cache: true

endpoints:
  custom:
    - name: "MyTest"
      apiKey: "mytest"
      baseURL: "http://host.docker.internal:3000"
      models:
        default: [
          "Default"
        ]
        fetch: true # fetching list of models is not supported
      titleConvo: true
      titleModel: "current_model"
```

# Notes
To apply the `librechat.yaml` file, we should create `docker-compose.override.yml` in the `LibreChat` directory by copying `docker-compose.override.yml.example` and uncomment the `services` section.

```yaml
services:
  api:
    volumes:
    - type: bind
      source: ./librechat.yaml
      target: /app/librechat.yaml
```
