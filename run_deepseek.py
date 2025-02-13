from openai import OpenAI
import pandas as pd
import time
import argparse
import json

# 虚拟lm-studio本地服务器地址，设置为全局变量
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

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

以下为reagents中可能出现的试剂名：
(NH4)2SO4
0.1 M SODIUM ACETATE
0.8 M 1,6-HEXANEDIOL
1,2-propanediol
1,6-hexanediol
1,6-hexanodiol
1-NM-PP1
10 MM TRIS/CL
2-METHYL-2,4-PENTANEDIOL
2-METHYL-2,4-PENTANEDIOL (MPD)
2-propanol
2MM AMPPCP
3-PGA
4.6 MG/ML SSUMPK
5 MM COCl2
5 MM MGCL2
acetate
ADP
AMMONIUM ACETATE
ammonium citrate
ammonium citrate dibasic
Ammonium citrate tribasic
ammonium fluoride
ammonium sulfate
Ammonium sulfate ((NH4)2SO4)
Ammonium Sulphate
AMP-PCP
AMP-PNP
AMPPNP
arginine/glutamine mix
ATP
barium acetate
benzamidine hydrochloride
betaine
bicine
Bis Tris Propane
Bis-Tris
Bis-Tris propane
Bis-Tris Propane (pH 7)
BIS-TRIS PROPERTIES
BIS-TRIS:HCl
BisTRIS
BisTris Propane
BisTris propane/citric acid
BisTris-propane
BTPROP
Ca acetate
CA(OAC)2
CaCl2
calcium acetate
CDCL2
CHC buffer
Citrate
citric acid
Cmp3
Cobalt (II) chloride
cobalt chloride
Creatine
DMSO
DTT
ETGLY
Ethanol
ethylene glycol
Glycerol
Glycine
GTP
H2O
HEPES
IMIDAZOLE
iso-propanol
isopropanol
KANAMYCIN
KCl
KSCN
landthanide
LI2SO4
LiCl
Lithium acetate
lithium chloride
lithium sulfate
Lithium sulfate monohydrate
LITHIUM SULPHATE
MAGNESIUM ACETATE
magnesium chloride
magnesium sulfate
MEGA-8
Mega8
MES
MES monohydrate
MES pH
Mes-Bistris
MesBisTris
methanol
Mg Acetate
Mg(CH3COO)2
MgAcetate
MGADP
MgCl
MgCl2
MgSO4
MIB buffer
mmePEG 2000
MMT
MOPS
MPD
MPEG 2000
mPEG5000
MSH
Na Citrate
Na formate
NA(MALONATE)
Na-acetate
Na-HEPES
Na/K phosphate
Na/K Tartrate
Na3-Citrate
Na3C6H5O7
Na3Cit
NAAC
NACACOD
NaCl
NAG
NaK tartrate
NaMalonate
NaN3
NH4SO4
nickel, chloride hexahydrate
PE 2MM DTT
PEG 1000
PEG 10000
PEG 200
PEG 2000
PEG 20000
PEG 20K
PEG 3000
PEG 3350
PEG 3K-20K
PEG 400
PEG 4000
PEG 5K MNE
PEG 6000
PEG 8000
PEG 8K
PEG MME 2K
peg-3350
PEG1000
PEG10K
PEG1500
PEG2000 MME
PEG20000
PEG200DME
PEG300
PEG3350
PEG400
PEG4000
PEG4K
PEG5000 MME
PEG6000
PEG8000
peg_3350
PEGMME 550
Phosphate-citrate buffer
PKI
PKI(5-24)
polyethylene glycol
POLYETHYLENE GLYCOL 3000
polyethylene glycol 3350
POLYETHYLENE GLYCOL 4K
Polyethylene glycol monomethyl ether 2000
potassium dihydrogen phosphate
potassium phosphate
potassium phosphate dibasic
potassium thiocyanate
PR ACETATE
proline
PROTEIN
protein solution
PROTEIN SOLUTION (2UL)
reservoir solution
SODIUM ACETATE
sodium acetate (NaOAc)
sodium acetate tri-hydrate
sodium cacodylate
SODIUM CHLORIDE
sodium citrate
sodium citrate tribasic dihydrate
SODIUM CITRATE/HCL
sodium dihydrogen phosphate
sodium formate
sodium hepes
sodium nitrate
sodium phophonoacetate
sodium phosphate
sodium phosphate monobasic monohydrate
Sodium Potassium Phosphate
sodium propionate
sodium sulfate
sodium tartrate
sodium/potassium phosphate
Sokalan CP42
SPG buffer (Succinic acid, sodium dihydrogen phosphate and glycine)
SUCCINATE
SUMPK
Tacsimate
tascimate
TCEP
TEA buffer
triethanolamine-HCl
TRIS
Tris HCl
tris sodium citrate dehydrate
Tris(100mM)
Tris-Cl
TRIS-HCL
TRIS/CL
Tris/HCl
TrisHCl
UMP
zinc chloride
Zwittergent 3-14


用户输入的文本为：
"""


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
"""


# 大模型处理自然语言文本
def llm_process(original_sent):
    # 模型的超参数在LM Studio的UI界面调整，注意模型名字
    # 因为propmt_1内含有很多大括号，可能导致无法正常使用format组合字符串
    content = propmt_1 + original_sent
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-8b",
        messages=[
          {"role": "user", "content": content}
        ]
    )
    return completion.choices[0].message.content


def process_csv(input_csv_path, output_csv_path, is_check, is_refine):
    # 读取CSV文件
    df = pd.read_csv(input_csv_path, header=0, delimiter=',')

    # 将大模型结构化后的数据分类。ph和temperature和method可以和rcsb提供的原始值比对验证
    extracted_pH_lst = []
    extracted_temperature_lst = []
    extracted_method_lst = []
    extracted_reagents_lst = []
    refined_json_lst = []

    count_row = 1


    def append_all_null():
        extracted_pH_lst.append('null')
        extracted_temperature_lst.append('null')
        extracted_method_lst.append('null')
        extracted_reagents_lst.append('null')
        refined_json_lst.append('null')


    for row in df["exptl_crystal_grow.pdbx_details"]:
        # exptl_crystal_grow.pdbx_details可能为空
        if type(row) == float:
            print(f"第{count_row}条数据exptl_crystal_grow.pdbx_details为空")
            append_all_null()
            count_row = count_row + 1
            continue

        json_structure = llm_process(row)

        try:
            output = json.loads(json_structure)
        except json.decoder.JSONDecodeError:
            print(f"第{count_row}条数据模型输出结果为非法json结构")
            append_all_null()
            count_row = count_row + 1
            continue

        # 提取大模型输出的json格式中的特定值
        try:
            pH_value = output['pH']
            extracted_pH_lst.append(pH_value)
        except KeyError:
            extracted_pH_lst.append('null')
            print(f"第{count_row}条数据ph模型没生成")

        try:
            temperature_value = output['temperature']
            extracted_temperature_lst.append(temperature_value)
        except KeyError:
            extracted_temperature_lst.append('null')
            print(f"第{count_row}条数据temperature模型没生成")

        try:
            reagents_dict = output['reagents']
            extracted_reagents_lst.append(reagents_dict)
        except KeyError:
            extracted_reagents_lst.append('null')
            print(f"第{count_row}条数据reagents模型没生成")

        try:
            method_value = output['method']
            extracted_method_lst.append(method_value)
        except KeyError:
            extracted_method_lst.append('null')
            print(f"第{count_row}条数据method_value模型没生成")

        if is_check:
            evaluateData()
        if is_refine:
            try:
                refined_json = refineData(json_structure, row)
                refined_json_lst.append(refined_json)
            except:
                refined_json_lst.append('null')
                print(f"第{count_row}条数据refine失败")

        print(f"已经完成了{count_row}条数据")
        count_row = count_row + 1

    df["exptl_crystal_grow.pdbx_details_extracted.pH"] = extracted_pH_lst
    df["exptl_crystal_grow.pdbx_details_extracted.temperature"] = extracted_temperature_lst
    df["exptl_crystal_grow.pdbx_details_extracted.method"] = extracted_method_lst
    df["exptl_crystal_grow.pdbx_details_extracted.reagents"] = extracted_reagents_lst
    df["exptl_crystal_grow.pdbx_details_refined"] = refined_json_lst

    # 写入输出CSV文件
    df.to_csv(output_csv_path, index=False)


def refineData(json_structure, original_sent):
    # 模型的超参数在LM Studio的UI界面调整，注意模型名字
    # 如果显存够大，可以在refine的阶段使用和之前不同的模型（更改模型名称即可）
    content = propmt_refine + json_structure + '\n需要你检查的json结构为：\n' + original_sent
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-8b",
        messages=[
          {"role": "user", "content": content}
        ]
    )
    return completion.choices[0].message.content


# TODO: 一个不依赖大模型检测模型是否出现幻觉/遗漏的方法
def evaluateData():
    return 0


if __name__ == "__main__":
    # 使用argparse来处理命令行参数
    parser = argparse.ArgumentParser(description="调用DeepSeek-R1模型进行蛋白质晶体生长条件数据的转换")
    parser.add_argument("input_csv_path", type=str, help="输入的CSV文件路径")
    parser.add_argument("output_csv_path", type=str, help="输出的CSV文件路径")
    parser.add_argument("is_check_data", type=bool, help="布尔值，是否执行输出检查", default=False)
    parser.add_argument("is_refine_data", type=bool, help="布尔值，是否执行输出调优", default=False)

    args = parser.parse_args()
    start_time = time.time()

    # 确保敲入的文件名不含非法字符
    assert not any(char in '\\/:*?"<>|' for char in args.input_csv_path)
    assert not any(char in '\\/:*?"<>|' for char in args.output_csv_path)

    process_csv(args.input_csv_path, args.output_csv_path, args.is_check_data, args.is_refine_data)
    print(f"CSV saved to {args.output_csv_path}")
    end_time = time.time()
    print(f"程序运行用时：{end_time-start_time}秒")

