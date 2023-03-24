# **简体中文 | [English](./README.md)**

# 自托管AI

该项目的API接口兼容openai, 各类使用openai的开源项目能够非常方便适配, 此外我也呼吁大家使用相似的方式开发兼容性API接口,
便于相关应用的发展

## 使用示例

前往 https://github.com/josStorer/chatGPTBox, 并切换至如下API模式即可快速体验:

<img width=350 src="https://user-images.githubusercontent.com/13366013/227125297-a933d37b-9af8-49a3-907d-9bd769cbabea.png">

## 聊天

1. [ChatGLM 6B Int4](https://github.com/THUDM/ChatGLM-6B)
    - [离线包](https://github.com/josStorer/selfhostedAI/releases),
      可选[百度网盘](https://pan.baidu.com/s/1wchIUHgne3gncIiLIeKBEQ?pwd=1111)
        - 该包基于ChatGLM, 遵循Apache-2.0协议开源, 内置模型为 https://huggingface.co/silver/chatglm-6b-int4-slim 的裁切版,
          解压后直接双击run.bat启动
    - [自托管](https://huggingface.co/spaces/josStorer/ChatGLM-6B-Int4-API-OpenAI-Compatible)
        - 点击上方链接进入Huggingface, 复制空间, 将CPU切换到第二个八核进行快速体验, 此时API地址为, `你的名字-仓库名.hf.space`,
          例如我复制后名字设为`test`, 那么我的url就是 `https://josstorer-test.hf.space/chat/completions`

