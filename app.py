import asyncio
import json
import time
from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import dotenv

dotenv.load_dotenv()

app = FastAPI(title="OpenAI-compatible API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "mock-gpt-model"
    messages: List[Message]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    stream: Optional[bool] = False


@app.get("/")
async def read_root():
    return {"message": "Welcome using OpenAI-compatible API"}


# add model lists
MODELS = ["model 1", "model 2", "model 3"]


class ModelListResponse(BaseModel):
    data: list


@app.get("/models", response_model=ModelListResponse)
async def get_models():
    return {"data": [{"id": model, "object": "model"} for model in MODELS]}


async def _post_process(text_resp: str, len_tokens: int = 0):
    # 请求图片
    image_markdown = os.getenv("IMAGE_MARKDOWN")

    # 根据 text_resp 中 , 后插入 请求图片返回
    text_resp_list = text_resp.split(",")
    image_markdown = f"result:{text_resp_list[0]},{image_markdown},{text_resp_list[1]}"

    chunk = {
        "id": f"chatcmpl-{len_tokens}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "mock-gpt-model",
        "choices": [
            {
                "index": 0,
                "delta": {"content": image_markdown + " "},
                "finish_reason": None,
            }
        ],
    }

    yield f"data: {json.dumps(chunk)}\n\n"
    await asyncio.sleep(0.1)

    # 发送数据
    data_arr = [
        {
            "documentPath": "Test.pdf",
            "documentChunk": "This is a test citation which is a chunk of the document Test.pdf",
            "pageNumber": 1,
        },
        {
            "documentPath": "Test2.pdf",
            "documentChunk": "This is a test citation which is a chunk of the document Test2.pdf",
            "pageNumber": 2,
        },
        {
            "documentPath": "Test3.pdf",
            "documentChunk": "This is a test citation which is a chunk of the document Test3.pdf",
            "pageNumber": 3,
        },
        {
            "documentPath": "Test4.pdf",
            "documentChunk": "This is a test citation which is a chunk of the document Test4.pdf",
            "pageNumber": 4,
        },
        {
            "documentPath": "Test5.pdf",
            "documentChunk": "This is a test citation which is a chunk of the document Test5.pdf",
            "pageNumber": 5,
        },
        {
            "documentPath": "Test6.pdf",
            "documentChunk": "This is a test citation which is a chunk of the document Test6.pdf",
            "pageNumber": 6,
        },
        {
            "documentPath": "Test7.pdf",
            "documentChunk": "This is a test citation which is a chunk of the document Test7.pdf",
            "pageNumber": 7,
        },
        {
            "documentPath": "Test8.pdf",
            "documentChunk": "This is a test citation which is a chunk of the document Test8.pdf",
            "pageNumber": 8,
        },
        {
            "documentPath": "Test9.pdf",
            "documentChunk": "This is a test citation which is a chunk of the document Test9.pdf",
            "pageNumber": 9,
        },
        {
            "documentPath": "Test10.pdf",
            "documentChunk": "This is a test citation which is a chunk of the document Test10.pdf",
            "pageNumber": 10,
        },
    ]

    chunk = {
        "id": f"chatcmpl-{len_tokens + 1}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "mock-gpt-model",
        "choices": [
            {
                "index": 0,
                "delta": {"content": f"\ndata_start{json.dumps(data_arr)}data_end"},
                "finish_reason": "stop",
            }
        ],
    }

    yield f"data: {json.dumps(chunk)}\n\n"
    await asyncio.sleep(0.1)


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
                        "finish_reason": None,
                    }
                ],
            }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.1)

    # 使用 async for 来正确处理异步生成器
    async for chunk in _post_process(text_resp, len(tokens)):
        yield chunk

    # Signal the end of the stream
    yield "data: [DONE]\n\n"


async def log_request_details(request: Request):
    """Extract and print all request details to the terminal."""
    headers = dict(request.headers)
    query_params = dict(request.query_params)
    cookies = dict(request.cookies)
    method = request.method
    url = str(request.url)

    # Read and decode request body
    body_bytes = await request.body()
    try:
        body = json.loads(body_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        body = "Invalid JSON or empty body"

    log_data = {
        "Method": method,
        "URL": url,
        "Headers": headers,
        "Query Params": query_params,
        "Cookies": cookies,
        "Body": body,
    }

    print("\n" + "=" * 60)
    print("📌 REQUEST DETAILS 📌")
    print("=" * 60)
    for key, value in log_data.items():
        print(
            f"🔹 {key}:\n{json.dumps(value, indent=2) if isinstance(value, dict) else value}\n"
        )
    print("=" * 60 + "\n")


@app.post("/chat/completions")
async def chat_completions(request: Request):
    raw_body = await request.body()  # Get the raw request body as bytes
    await log_request_details(request)
    # Parse the request body into the Pydantic model manually
    body = ChatCompletionRequest.model_validate_json(raw_body)

    print(f"Parsed Pydantic model: {body}")

    if not body.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    resp_content = (
        f"This is a test response, I can only echo your last message: "
        + body.messages[-1].content
    )

    if body.stream:
        return StreamingResponse(
            _resp_async_generator(resp_content), media_type="text/event-stream"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
