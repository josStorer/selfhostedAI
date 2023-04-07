# **简体中文 | [English](./README.md)**

# 自托管AI

该项目的API接口兼容openai, 各类使用openai的开源项目能够非常方便适配, 此外我也呼吁大家使用相似的方式开发兼容性API接口,
便于相关应用的发展

前往[release](https://github.com/josStorer/selfhostedAI/releases)下载封装过的包

使用`update.bat`更新本程序 (不含模型)

定义`ngrok_token`环境变量以将API暴露到外网

## 使用示例

前往 https://github.com/josStorer/chatGPTBox, 并切换至如下API模式即可快速体验:

<img width=350 src="https://user-images.githubusercontent.com/13366013/230396985-5c55d8bc-55e6-4cc4-a5fa-792838d5b8ea.png"/>

## 聊天

1. [ChatGLM 6B Int4](https://github.com/THUDM/ChatGLM-6B)
    - [离线包](https://github.com/josStorer/selfhostedAI/releases),
      可选[百度网盘](https://pan.baidu.com/s/1wchIUHgne3gncIiLIeKBEQ?pwd=1111)
        - 该包基于ChatGLM, 遵循Apache-2.0协议开源, 内置模型为 https://huggingface.co/silver/chatglm-6b-int4-slim 的裁切版
        - 解压后直接双击对应模型文件运行, 例如`llama.bat`启动llama模型, `chatglm.bat`启动chatglm模型
    - [自托管](https://huggingface.co/spaces/josStorer/ChatGLM-6B-Int4-API-OpenAI-Compatible)
        - 点击上方链接进入Huggingface, 复制空间, 将CPU切换到第二个八核进行快速体验, 此时API地址为, `你的名字-仓库名.hf.space`,
          例如我复制后名字设为`test`, 那么我的url就是 `https://josstorer-test.hf.space/chat/completions`
    - 配合ChatGPTBox使用时, 需要将模型名设为chatglm-6b-int4

2. [llama.cpp](https://github.com/ggerganov/llama.cpp)
    - [离线包](https://github.com/josStorer/selfhostedAI/releases), 
      可选[百度网盘](https://pan.baidu.com/s/1wchIUHgne3gncIiLIeKBEQ?pwd=1111)
        - 该包基于llama.cpp, 内置命令行交互示例为我[修改的版本](https://github.com/josStorer/llama.cpp-unicode-windows), 以支持windows的unicode输入, 内置模型来自[Chinese-LLaMA-Alpaca](https://github.com/ymcui/Chinese-LLaMA-Alpaca)
        - github离线包请自己在wsl或linux环境下, 执行`get_llama_model.sh`获取模型, 如果已有模型的, 直接替换`models/llama.cpp/ggml-model-q4_0.bin`文件即可
        - 百度网盘离线包, 解压后直接双击对应模型批处理文件运行, 例如`llama.bat`启动llama模型, `chatglm.bat`启动chatglm模型
    - 配合ChatGPTBox使用时, 需要将模型名设为llama-7b-int4
