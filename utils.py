import json
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import re
PROMPT_TEMPLATE = """
你是一位数据分析助手。请按照以下步骤执行：

**执行流程：**
1. 思考：分析用户问题，确定需要执行什么操作
2. 行动：使用 python_repl_ast 工具执行代码
3. 观察：查看代码执行结果
4. 重复1-3步直到获得完整答案
5. 最终答案：在最后一步返回JSON格式结果，并在JSON前加上 `Final Answer:`

**重要规则：**
- 在思考过程中绝对不要返回JSON格式
- 只有在最终答案时才返回JSON，并且必须以 `Final Answer:` 开头
- 所有回答内容必须使用中文
- 列名和说明文字也要用中文

**JSON格式要求（仅在最后一步使用）：**

对于文字回答：
{{"answer": "你的答案"}}

对于表格：
{{"table": {{"columns": ["列1", "列2"], "data": [["值1", "值2"]]}}}}

对于条形图：
{{"bar": {{"columns": ["A", "B"], "data": [25, 40]}}}}

对于折线图：
{{"line": {{"columns": ["A", "B"], "data": [25, 40]}}}}

对于散点图：
{{"scatter": {{"columns": ["A", "B"], "data": [25, 40]}}}}

**当前任务：**
用户请求：{query}

请开始执行，记住：只有在最后一步才能返回JSON，并且必须以 `Final Answer:` 开头！"""

def dataframe_agent(deepseek_api_key,df,query):#对请求进行封装
    model = ChatOpenAI(model="deepseek-chat",
                       openai_api_key=deepseek_api_key,
                       base_url="https://api.deepseek.com/v1",
                       temperature=0
                       )
    agent=create_pandas_dataframe_agent(llm=model,
                                        df=df,
                                        allow_dangerous_code=True,
                                        max_iterations=10,
                                        early_stopping_method="force",
                                        verbose=True,
                                        handle_parsing_errors=True)#看执行过程
    prompt = PROMPT_TEMPLATE.format(query=query)
    try:
       response = agent.invoke({"input": prompt}, handle_parsing_errors=True)
       output = response["output"]
       return {"raw_output": output}

    except Exception as e:
        print(f"Agent执行错误: {e}")
        return {"answer": f"处理请求时发生错误：{str(e)}"}