import asyncio
import json
import time
from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI(title="OpenAI-compatible API")

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "mock-gpt-model"
    messages: List[Message]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    stream: Optional[bool] = False

async def _resp_async_generator(text_resp: str):
    tokens = text_resp.split(" ")

    for i, token in enumerate(tokens):
        # First chunk must include the role: "assistant"
        if i == 0:
            chunk = {
                "id": f"chatcmpl-{i}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "mock-gpt-model",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": token + " "},
                        "finish_reason": None,
                    }
                ],
            }
        else:
            # Subsequent chunks only include the content
            chunk = {
                "id": f"chatcmpl-{i}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "mock-gpt-model",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": token + " "},
                        "finish_reason": None if i < len(tokens) - 1 else "stop",
                    }
                ],
            }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.1)

    # Signal the end of the stream
    yield "data: [DONE]\n\n"

@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    resp_content = "As a mock AI Assistant, I can only echo your last message: " + request.messages[-1].content

    if request.stream:
        return StreamingResponse(
            _resp_async_generator(resp_content), media_type="text/event-stream"
        )

    # Non-streaming response
    return {
        "id": "chatcmpl-1337",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": resp_content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)