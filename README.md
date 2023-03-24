# **[简体中文](./README_ZH.md) | English**

# Self-Hosted AI

The API interface of this project is compatible with openai, and various open-source projects using openai can be easily
adapted. In addition, I also call on everyone to develop compatible API interfaces in a similar way, which is conducive
to the development of related applications.

## Usage Example

Go to https://github.com/josStorer/chatGPTBox, and switch to the following API mode to quickly experience:

<img width=350 src="https://user-images.githubusercontent.com/13366013/227125297-a933d37b-9af8-49a3-907d-9bd769cbabea.png">

## Chat

1. [ChatGLM 6B Int4](https://github.com/THUDM/ChatGLM-6B)
    - [Offline](https://github.com/josStorer/selfhostedAI/releases)
        - This package is based on ChatGLM, open-sourced under the Apache-2.0 license. The built-in model is a trimmed
          version of https://huggingface.co/silver/chatglm-6b-int4-slim. After unzipping, simply double-click run.bat to
          launch.
    - [Self-Hosted](https://huggingface.co/spaces/josStorer/ChatGLM-6B-Int4-API-OpenAI-Compatible)
        - Click the link above to go to Huggingface, copy the space, switch the CPU to the second 8-core for a fast
          experience, at this time the API address is, `[your name]-[repository name].hf.space`,
          for example, if I copy and set the name to `test`, then my URL would
          be `https://josstorer-test.hf.space/chat/completions`
