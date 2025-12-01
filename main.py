import pandas as pd
import streamlit as st
from utils import dataframe_agent


def create_chart(input_data, chart_type):
    df_data = pd.DataFrame(input_data["data"], columns=input_data["columns"])
    df_data.set_index(input_data["columns"][0], inplace=True)#索引是横轴
    if chart_type == "bar":#条形图
        st.bar_chart(df_data)
    elif chart_type == "line":#折线图
        st.line_chart(df_data)
    elif chart_type == "scatter":#散点图
        st.scatter_chart(df_data)

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

if button and not deepseek_api_key:
    st.info("请输入你的Deepseek API密钥")
if button and "df" not in st.session_state:
    st.info("请先上传数据文件")
if button and deepseek_api_key and "df" in st.session_state:
    with st.spinner("AI正在思考中，请稍等..."):
        response_dict = dataframe_agent(deepseek_api_key, st.session_state["df"], query)
        if "answer" in response_dict:
            st.write(response_dict["answer"])
        if "table" in response_dict:
            st.table(pd.DataFrame(response_dict["table"]["data"],
                                  columns=response_dict["table"]["columns"]))
        if "bar" in response_dict:
            create_chart(response_dict["bar"], "bar")
        if "line" in response_dict:
            create_chart(response_dict["line"], "line")
        if "scatter" in response_dict:
            create_chart(response_dict["scatter"], "scatter")
