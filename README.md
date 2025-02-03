# This is a mock OpenAI API server

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

