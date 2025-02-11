模型是通过LM Studio软件虚拟了一个本地服务器，然后再通过python程序run_deepseek.py进行交互推理的。LM Studio开启了json结构化输出模式。temperature=0.6（deepseek官方推荐0.5-0.7）

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


模型下载地址为：
https://huggingface.co/bartowski/DeepSeek-R1-Distill-Llama-8B-GGUF

因为LM Studio软件不支持safetensor格式，只支持gguf格式。而深度求索公司官方发布在hugging face上的模型格式大部分为safetensor格式，因此使用的是一位叫bartowski的开发者进行过格式转换后的版本。

依据deepseek官方在hugging face上的说明，他们不推荐在DeepSeek-R1模型及其蒸馏模型中使用system propmt。

代码首先使用大模型生成了json结构，并且将生成的结构分成了四列储存：
exptl_crystal_grow.pdbx_details_extracted.pH	
exptl_crystal_grow.pdbx_details_extracted.temperature	
exptl_crystal_grow.pdbx_details_extracted.method 
exptl_crystal_grow.pdbx_details_extracted.reagents
有些数据可能模型没有生成，代码会记为null

本次生成的propmt为：
propmt_1 = """
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

随后，会使用大模型进行二次验证，模型修正后的结果会储存在这一列。pH temperature method reagents这四种参数储存在一起
exptl_crystal_grow.pdbx_details_refined


propmt_refine = """
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
