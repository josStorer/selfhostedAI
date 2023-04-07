import asyncio
import json
import re
import sys
from typing import List
import os
import sysconfig
import time
import subprocess

from fastapi import FastAPI, Request, status, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


def set_torch():
    torch_path = os.path.join(sysconfig.get_paths()["purelib"], "torch\\lib")
    paths = os.environ.get("PATH", "")
    if os.path.exists(torch_path):
        print(f"torch found: {torch_path}")
        if torch_path in paths:
            print("torch already set")
        else:
            print("run:")
            os.environ['PATH'] = paths + os.pathsep + torch_path + os.pathsep
            print(f'set Path={paths + os.pathsep + torch_path + os.pathsep}')
    else:
        print("torch not found")


def init_chatglm(chatglm):
    set_torch()

    import torch
    from torch.cuda import get_device_properties
    from transformers import AutoModel, AutoTokenizer

    os.environ['TRANSFORMERS_CACHE'] = ".cache"

    chatglm["tokenizer"] = AutoTokenizer.from_pretrained(chatglm["model_path"], trust_remote_code=True,
                                                         cache_dir=chatglm["cache_dir"])
    chatglm["model"] = AutoModel.from_pretrained(chatglm["model_path"], trust_remote_code=True,
                                                 cache_dir=chatglm["cache_dir"])

    if torch.cuda.is_available() and get_device_properties(0).total_memory / 1024 ** 3 > chatglm["min_memory"]:
        if chatglm["kernel_path"]:
            chatglm["model"] = chatglm["model"].half().quantize(bits=chatglm["bits"],
                                                                kernel_file=chatglm["kernel_path"]).cuda()
        else:
            chatglm["model"] = chatglm["model"].half().quantize(bits=chatglm["bits"]).cuda()
        print("Using GPU")
    else:
        if chatglm["kernel_path"]:
            chatglm["model"] = chatglm["model"].float().quantize(bits=chatglm["bits"],
                                                                 kernel_file=chatglm["kernel_path"])
        else:
            chatglm["model"] = chatglm["model"].float().quantize(bits=chatglm["bits"])
        if torch.cuda.is_available():
            print("Total Memory: ", get_device_properties(0).total_memory / 1024 ** 3)
        else:
            print("No GPU available")
        print("Using CPU")
    chatglm["model"].eval()


def init_llama(llama):
    llama["model"] = subprocess.Popen([os.path.abspath("./models/llama.cpp/main"),
                                       "-m", llama["model_path"], "-t", str(llama["thread"]),
                                       "--color", "-ins"], stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
    while True:
        text = llama["model"].stdout.readline().decode(errors='ignore')
        print(text, end="")
        if "好的" in text:
            llama["model"].stdout.readline()
            time.sleep(1)
            break


chatglm_6b_int4 = {
    "enable": "chatglm-6b-int4" in sys.argv[1:],
    "model_name": 'chatglm-6b-int4',
    "type": 'chatglm',
    "bits": 4,
    "kernel_path": "models/models--silver--chatglm-6b-int4-slim/quantization_kernels.so",
    "model_path": "./models/models--silver--chatglm-6b-int4-slim/snapshots/02e096b3805c579caf5741a6d8eddd5ba7a74e0d",
    "cache_dir": './models',
    "min_memory": 5.5,
    "tokenizer": None,
    "model": None,
    "init": init_chatglm
}

llama_7b_int4 = {
    "enable": "llama-7b-int4" in sys.argv[1:],
    "model_name": 'llama-7b-int4',
    "type": 'llama_instruct',
    "model_path": "./models/llama.cpp/ggml-model-q4_0.bin",
    "thread": 10,
    "model": None,
    "init": init_llama,
}

models = [chatglm_6b_int4, llama_7b_int4]


def torch_gc():
    import torch

    if torch.cuda.is_available():
        with torch.cuda.device(0):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()


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
    for model in models:
        if model["enable"]:
            model["init"](model)

    if os.environ.get("ngrok_token") is not None:
        ngrok_connect()


def ngrok_connect():
    from pyngrok import ngrok, conf
    conf.set_default(conf.PyngrokConfig(ngrok_path="./ngrok"))
    ngrok.set_auth_token(os.environ["ngrok_token"])
    http_tunnel = ngrok.connect(8000)
    print(http_tunnel.public_url)


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
    global models

    def check_model(model_name):
        for model in models:
            if model_name == model['model_name']:
                return True, model
        return False, None

    exist, model = check_model(body.model)
    if not exist:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not Implemented")

    if not model["enable"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Disabled")

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

    completion_text = """The following is a conversation with an AI assistant.
The assistant is helpful, creative, clever, and very friendly. The assistant is familiar with various languages in the world.

Human: Hello, who are you?
AI: I am an AI assistant. How can I help you today?
Human: 没什么
AI: 好的, 如果有什么需要, 随时告诉我"""
    for message in body.messages:
        if message.role == 'user':
            completion_text += "\nHuman: " + message.content
        elif message.role == 'assistant':
            completion_text += "\nAI: " + message.content
    completion_text += "\nAI: "

    eval_data = {
        "conversation": "",
        "new_message": "",
        "finished": False
    }

    async def eval_chatglm():
        if body.stream:
            for response in model["model"].stream_chat(model["tokenizer"], question, history,
                                                       max_length=max(2048, body.max_tokens)):
                if await request.is_disconnected():
                    torch_gc()
                    return
                yield json.dumps({"response": response[0]})
            yield "[DONE]"
        else:
            response, _ = model["model"].chat(model["tokenizer"], question, history,
                                              max_length=max(2048, body.max_tokens))
            yield json.dumps({"response": response[0]})
        torch_gc()

    async def eval_llama_instruct():
        eval_data["conversation"] = bytearray()

        model["model"].stdin.write((user_question.replace("\n", "\\\n") + "\r\n").encode())
        model["model"].stdin.flush()
        print("> " + user_question)

        if body.stream:
            while not eval_data["conversation"].decode(errors='ignore').endswith("\n> "):
                eval_data["conversation"] += model["model"].stdout.read(1)
                eval_data["new_message"] = re.sub(r"(^(> )?\x1b\[0m)|(\x1b\[1m\x1b\[32m\r?\n?(> )?$)", "",
                                                  eval_data["conversation"].decode(errors='ignore'))
                yield json.dumps({"response": eval_data["new_message"]})
            print("\n" + eval_data["new_message"].replace("> ", ""))
            yield "[DONE]"
        else:
            while not eval_data["conversation"].decode(errors='ignore').endswith("\n> "):
                eval_data["conversation"] += model["model"].stdout.read(1)
            eval_data["new_message"] = re.sub(r"(^(> )?\x1b\[0m)|(\x1b\[1m\x1b\[32m\r?\n?(> )?$)", "",
                                              eval_data["conversation"].decode(errors='ignore'))
            print("\n" + eval_data["new_message"].replace("> ", ""))
            yield json.dumps({"response": eval_data["new_message"]})

    async def eval_general():
        while True:
            if eval_data["new_message"] != "":
                print(eval_data["new_message"])
            if await request.is_disconnected():
                break

            if eval_data["new_message"] == "[DONE]":
                yield "[DONE]"
                break
            elif eval_data["new_message"].endswith("[DONE]"):
                eval_data["new_message"] = eval_data["new_message"][:-6]
                yield json.dumps({"response": eval_data["new_message"]})
                yield "[DONE]"
                break
            else:
                yield json.dumps({"response": eval_data["new_message"]})
                eval_data["new_message"] = ""

            if eval_data["finished"]:
                break
            await asyncio.sleep(0.3)

    if model["type"] == "chatglm":
        return EventSourceResponse(eval_chatglm())
    elif model["type"] == "llama_instruct":
        return EventSourceResponse(eval_llama_instruct())


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, app_dir=".")
