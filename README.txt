模型是通过LM Studio软件虚拟了一个本地服务器，然后再通过python程序run_deepseek.py进行交互推理的。
模型下载地址为：
https://huggingface.co/bartowski/DeepSeek-R1-Distill-Qwen-14B-GGUF/blob/main/DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf
https://huggingface.co/bartowski/DeepSeek-R1-Distill-Llama-8B-GGUF
因为LM Studio软件不支持safetensor格式，只支持gguf格式。而深度求索公司官方发布在hugging face上的模型格式大部分为safetensor格式，因此使用的是一位叫bartowski的开发者进行过格式转换后的版本。

依据deepseek官方在hugging face上的说明，他们不推荐在DeepSeek-R1模型及其蒸馏模型中使用system propmt。