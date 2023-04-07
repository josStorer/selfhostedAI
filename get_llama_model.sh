pip install git+https://github.com/huggingface/transformers.git
pip install torch
pip install peft
pip install sentencepiece

git clone https://github.com/ymcui/Chinese-LLaMA-Alpaca repos/Chinese-LLaMA-Alpaca
git clone https://github.com/ggerganov/llama.cpp repos/llama.cpp

python3 ./repos/Chinese-LLaMA-Alpaca/scripts/merge_llama_with_chinese_lora.py \
    --base_model 'decapoda-research/llama-7b-hf' \
    --lora_model 'ziqingyang/chinese-alpaca-lora-7b' \
    --output_dir repos/7B-combined

cd repos/llama.cpp
make

cd ../..
python3 repos/llama.cpp/convert-pth-to-ggml.py repos/7B-combined 1

./repos/llama.cpp/quantize ./repos/7B-combined/ggml-model-f16.bin ./models/llama.cpp/ggml-model-q4_0.bin 2