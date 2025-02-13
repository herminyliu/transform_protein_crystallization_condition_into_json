# Overview

模型是通过LM Studio软件虚拟了一个本地服务器，然后再通过python程序*run_deepseek.py*进行交互推理。LM studio为一个大语言模型推理管理软件，会帮助用户管理硬件资源、提供简洁的超参数调试/system prompt设置/json结构化输出设置界面、本地部署对话界面、智能选择合适的运行架构。例如在本项目中，因为蒸馏的基底模型为Llama-8B模型，LM studio智能选择了CUDA Llama.cpp而不是普通的pytorch架构，加快了推理速度。LM Studio开启了json结构化输出模式，使用的json_schema见下文。

LM studio的关于如何和本地虚拟出来的服务器进行交互的官方文档：https://lmstudio.ai/docs/api/endpoints/openai

模型下载地址为：https://huggingface.co/bartowski/DeepSeek-R1-Distill-Llama-8B-GGUF

## Tips

- 因为LM Studio软件不支持safetensor格式，**只支持gguf格式**。而深度求索公司官方发布在hugging face上的模型格式大部分为safetensor格式，因此使用的是一位叫bartowski的开发者进行过格式转换后的版本。

- 依据deepseek官方在hugging face上的说明，他们**不推荐在DeepSeek-R1模型及其蒸馏模型中使用system prompt。推荐的temperature为0.6，在本项目中均使用0.6作为temperature值**。具体请见链接https://huggingface.co/deepseek-ai/DeepSeek-R1的**Usage Recommendations**部分。因此json_schema被包含在每一个prompt中，这个会占用prompt的token数，可能会对性能有影响。并且**考虑到Llama为基底模型，中文并不是Llama的官方支持语言（见https://huggingface.co/meta-llama/Llama-3.1-8B#model-information），而prompt中大量使用中文，这可能会对性能有影响**。

- Unlike the example given in the LM Studio Docs https://lmstudio.ai/docs/api/structured-output, the json_schema mentioned below is set on the server level not on the post request /v1/chat/completions level.

## Repo File Description

| File | Description |
| ----------- | ---------- |
| *fetch_id.py* | python脚本获得RCSB数据库上满足特定要求的蛋白质晶体ID。 |
| *fetch_data.py* | 基于*fetch_id*获得的ID，获得这些ID对应的蛋白的信息，本项目中我们关注蛋白质结晶条件的信息。 |
| *run_deepseek.py* | 和LM Studio模拟出的本地服务器交互的python脚本，包含prompt构建、处理LLM的输入输出、异常处理、csv文件写入的功能。 |
| *extract_reagents_name.py* | 获得在蛋白质结晶过程中经常出现的试剂名称可能会对LLM有所帮助，该脚本利用LLM已经结构化的部分json格式数据，提取了出现的试剂名称列表。 |
| *output_15-300.csv* | 使用下文中的prompt和json_schema，对*20241104-213743.csv*中第15条至第300条数据转化得到的结果。 |
| *reagents_name.csv* | *output_15-300.csv*中出现过的试剂名称。 |
| *20241104-213743.csv* | 原始大数据表。 |
| *test_llm_transform.csv* | 固定为脚本*run_deepseek.py*的输入，内容可变。 |
| *output_100-300_with_reagent_name.csv* | 对*20241104-213743.csv*中第15条至第300条数据转化得到的结果，但是在prompt中加入了*reagents_name.csv*中的试剂名列表 |

## json_schema the model is required to follow

"""
{
  "properties": {
    "pH": {
      "type": "number",
      "examples": [
        7.4,
        7.6,
        4.3
      ],
      "description": "The pH at which the crystal was grown."
    },
    "temperature": {
      "type": "number",
      "examples": [
        277,
        298,
        293.15
      ],
      "description": "The temperature in kelvins at which the crystal was grown."
    },
    "reagents": {
      "type": "object",
      "examples": [
        {
          "HEPES": "0.1M",
          "ammonium sulfate": "0.4M",
          "PEG400": "20%"
        },
        {
          "PEG 6000": "3%",
          "Tris": "0.1M",
          "PEG 8K": "20% (w/v) "
        },
        {
          "isopropanol": "10%",
          "calcium acetate": "0.1M"
        }
      ],
      "description": "The keys should be the names of the reagents, and the values should be the concentrations of the reagents WITH UNITS, using molar concentration, percent concentration, or unit mass per unit volume."
    },
    "method": {
      "type": "string",
      "examples": [
        "MICROBATCH",
        "VAPOR DIFFUSION, HANGING DROP",
        "HANGING DROP"
      ],
      "description": "The method used to grow the crystals."
    }
  }
}
"""

# LLM结构化数据为json格式

代码首先使用大模型生成了json结构，并且将生成的结构分成了四列储存：

- exptl_crystal_grow.pdbx_details_extracted.pH	
- exptl_crystal_grow.pdbx_details_extracted.temperature	
- exptl_crystal_grow.pdbx_details_extracted.method 
- exptl_crystal_grow.pdbx_details_extracted.reagents

有些数据可能模型没有生成，代码会记为null。

## prompt

"""
用户会输入一段英文文本，该文本描述了某蛋白质的结晶条件。你需要按照下面的json schema，运用自己的理解，将这段文本转化为json格式。json格式化输出模式已经打开，模板正为下面的json_schema。注意下面的json schema的有些元素可能为空。

{
  "properties": {
    "pH": {
      "type": "number",
      "examples": [
        7.4,
        7.6,
        4.3
      ],
      "description": "The pH at which the crystal was grown."
    },
    "temperature": {
      "type": "number",
      "examples": [
        277,
        298,
        293
      ],
      "description": "The temperature in kelvins at which the crystal was grown."
    },
    "reagents": {
      "type": "object",
      "examples": [
        {
          "HEPES": "0.1M",
          "ammonium sulfate": "0.4M",
          "PEG400": "20%"
        },
        {
          "PEG 6000": "3%",
          "Tris": "0.1M",
          "PEG 8K": "20% (w/v) "
        },
        {
          "isopropanol": "10%",
          "calcium acetate": "0.1M"
        }
      ],
      "description": "The keys should be the names of the reagents, and the values should be the concentrations of the reagents WITH UNITS, using molar concentration, percent concentration, or unit mass per unit volume."
    },
    "method": {
      "type": "string",
      "examples": [
        "MICROBATCH",
        "VAPOR DIFFUSION, HANGING DROP",
        "HANGING DROP"
      ],
      "description": "The method used to grow the crystals."
    }
  }
}

用户输入的文本为：
"""

# Refinement

随后，会使用大模型进行Refine，模型修正后的结果会储存在这一列。pH temperature method reagents这四种参数储存在exptl_crystal_grow.pdbx_details_refined列中。

## Prompt used in the Refinement

"""
用户会输入一段英文文本，该文本描述了某蛋白质的结晶条件。
该文本已经被按照下面的json schema转化为了json格式。但是转化后的json可能存在问题。
例如json结构为全空、json结构不符合json格式要求、有些出现在json结构中的字段没有出现在原始文本中、有些出现在原始文本中的字段没有出现在json结构中。请你再检查一遍。
json格式化输出模式已经打开，模板正为下面的json_schema
json_schema为：
{
  "properties": {
    "pH": {
      "type": "number",
      "examples": [
        7.4,
        7.6,
        4.3
      ],
      "description": "The pH at which the crystal was grown."
    },
    "temperature": {
      "type": "number",
      "examples": [
        277,
        298,
        293
      ],
      "description": "The temperature in kelvins at which the crystal was grown."
    },
    "reagents": {
      "type": "object",
      "examples": [
        {
          "HEPES": "0.1M",
          "ammonium sulfate": "0.4M",
          "PEG400": "20%"
        },
        {
          "PEG 6000": "3%",
          "Tris": "0.1M",
          "PEG 8K": "20% (w/v) "
        },
        {
          "isopropanol": "10%",
          "calcium acetate": "0.1M"
        }
      ],
      "description": "The keys should be the names of the reagents, and the values should be the concentrations of the reagents WITH UNITS, using molar concentration, percent concentration, or unit mass per unit volume."
    },
    "method": {
      "type": "string",
      "examples": [
        "MICROBATCH",
        "VAPOR DIFFUSION, HANGING DROP",
        "HANGING DROP"
      ],
      "description": "The method used to grow the crystals."
    }
  }
}

如果你检查后没有问题，请这样回复：{"pH": 0, "temperature": 0, "reagents": "OK", "method": "OK"}
如果你检查后发现问题，请严格按照上面的json_schema给出你的修改后的版本。
原始文本为：

需要你检查的json结构为：

"""
