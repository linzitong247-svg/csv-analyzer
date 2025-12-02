import pandas as pd
import streamlit as st
from utils import dataframe_agent


def create_chart(input_data, chart_type):
    try:
        # 处理不同的数据格式
        data = input_data["data"]
        if len(data) == 2 and all(isinstance(item, list) for item in data):
            # 如果是 [[x值列表], [y值列表]] 格式，转换为 [[x1,y1], [x2,y2]] 格式
            x_values, y_values = data
            data = [[x, y] for x, y in zip(x_values, y_values)]

        df_data = pd.DataFrame(data, columns=input_data["columns"])
        df_data.set_index(input_data["columns"][0], inplace=True)
        if chart_type == "bar":
            st.bar_chart(df_data)
        elif chart_type == "line":
            st.line_chart(df_data)
        elif chart_type == "scatter":
            st.scatter_chart(df_data)
    except Exception as e:
        st.error(f"生成图表时出错：{str(e)}")

st.title("💡RIRINA-CSV数据分析智能工具")
#侧边栏
with st.sidebar:
    deepseek_api_key = st.text_input("请输入Deepseek API密钥：", type="password")
    st.markdown("[获取Deepseek API密钥](https://platform.deepseek.com/usage)")
#文件上传器
data = st.file_uploader("上传你的数据文件（CSV格式）：", type="csv")
#文件可视化
if data:
    st.session_state["df"] = pd.read_csv(data)#把csv读取为，再将df作为变量储存进会话状态
    with st.expander("原始数据"):
        st.dataframe(st.session_state["df"])
#问题输入框
query = st.text_area("请输入你关于以上表格的问题，或数据提取请求，或可视化要求（支持表格、散点图、折线图、条形图）：")
button = st.button("生成回答")

if button and deepseek_api_key and "df" in st.session_state:
    with st.spinner("AI正在思考中，请稍等..."):
        response_dict = dataframe_agent(deepseek_api_key, st.session_state["df"], query)

        # 处理原始输出
        if "raw_output" in response_dict:
            import json
            import re

            raw_output = response_dict["raw_output"]
            print("原始输出:", raw_output)  # 调试用

            # 尝试从原始输出中提取JSON
            try:
                # 查找JSON部分（处理代码块格式）
                json_match = re.search(r'```json\s*(.*?)\s*```', raw_output, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # 直接查找JSON对象
                    json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                    else:
                        json_str = raw_output

                response_dict = json.loads(json_str.strip())
            except Exception as e:
                print(f"JSON解析错误: {e}")
                # 如果解析失败，显示原始输出
                response_dict = {"answer": raw_output}

        # 安全地检查各个键是否存在
        if response_dict.get("answer"):
            st.write(response_dict["answer"])
        if "table" in response_dict:
            try:
                st.table(pd.DataFrame(response_dict["table"]["data"],
                                      columns=response_dict["table"]["columns"]))
            except Exception as e:
                st.error(f"显示表格时出错：{str(e)}")
        if "bar" in response_dict:
            create_chart(response_dict["bar"], "bar")
        if "line" in response_dict:
            create_chart(response_dict["line"], "line")
        if "scatter" in response_dict:
            create_chart(response_dict["scatter"], "scatter")

        # 如果没有找到任何有效的键，显示原始响应
        if not any(key in response_dict for key in ["answer", "table", "bar", "line", "scatter"]):
            st.warning("AI响应格式异常，显示原始响应：")
            st.write(response_dict)