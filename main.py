import json
from typing import List

import torch
from fastapi import FastAPI, Request, status, HTTPException
from pydantic import BaseModel
from torch.cuda import get_device_properties
from transformers import AutoModel, AutoTokenizer
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pyngrok import ngrok, conf

import os

os.environ['TRANSFORMERS_CACHE'] = ".cache"

bits = 4
kernel_path = ""
model_path = ""
cache_dir = ''
model_name = ''
min_memory = 5.5
tokenizer = None
model = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
def init():
    global tokenizer, model
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True, cache_dir=cache_dir)
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True, cache_dir=cache_dir)

    if torch.cuda.is_available() and get_device_properties(0).total_memory / 1024 ** 3 > min_memory:
        model = model.half().quantize(bits=bits).cuda()
        print("Using GPU")
    else:
        model = model.float().quantize(bits=bits)
        if torch.cuda.is_available():
            print("Total Memory: ", get_device_properties(0).total_memory / 1024 ** 3)
        else:
            print("No GPU available")
        print("Using CPU")
    model = model.eval()


class Message(BaseModel):
    role: str
    content: str


class Body(BaseModel):
    messages: List[Message]
    model: str
    stream: bool
    max_tokens: int


@app.get("/")
def read_root():
    return {"Hello": "World!"}


@app.post("/chat/completions")
async def completions(body: Body, request: Request):
    if body.model != model_name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not Implemented")

    question = body.messages[-1]
    if question.role == 'user':
        question = question.content
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No Question Found")

    user_question = ''
    history = []
    for message in body.messages:
        if message.role == 'user':
            user_question = message.content
        elif message.role == 'system' or message.role == 'assistant':
            assistant_answer = message.content
            history.append((user_question, assistant_answer))

    async def event_generator():
        for response in model.stream_chat(tokenizer, question, history, max_length=max(2048, body.max_tokens)):
            if await request.is_disconnected():
                return
            if body.stream:
                yield json.dumps({"response": response[0]})
        if body.stream:
            yield "[DONE]"
        else:
            yield json.dumps({"response": response[0]})

    return EventSourceResponse(event_generator())


def ngrok_connect():
    conf.set_default(conf.PyngrokConfig(ngrok_path="./ngrok"))
    ngrok.set_auth_token(os.environ["ngrok_token"])
    http_tunnel = ngrok.connect(8000)
    print(http_tunnel.public_url)


if __name__ == "__main__":
    # ngrok_connect()
    uvicorn.run("main:app", reload=True, app_dir=".")
