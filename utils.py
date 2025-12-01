import json
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

PROMPT_TEMPLATE = """
你是一位数据分析助手。请按照以下步骤执行：

**执行流程：**
1. 思考：分析用户问题，确定需要执行什么操作
2. 行动：使用 python_repl_ast 工具执行代码
3. 观察：查看代码执行结果
4. 重复1-3步直到获得完整答案
5. 最终答案：在最后一步返回JSON格式结果

返回结果时必须严格按照以下JSON格式：

对于文字回答：
{"answer": "你的答案"}

对于表格：
{"table": {"columns": ["列1", "列2"], "data": [["值1", "值2"]]}}

对于条形图：
{"bar": {"columns": ["A", "B"], "data": [25, 40]}}

对于折线图：
{"line": {"columns": ["A", "B"], "data": [25, 40]}}

对于散点图：
{"scatter": {"columns": ["A", "B"], "data": [25, 40]}}

重要要求：
- 只能在最后一步返回JSON格式
- 所有回答内容必须使用中文
- 列名和说明文字也要用中文

用户请求："""

def dataframe_agent(deepseek_api_key,df,query):#对请求进行封装
    model = ChatOpenAI(model="deepseek-chat",
                       openai_api_key=deepseek_api_key,
                       base_url="https://api.deepseek.com/v1",
                       temperature=0
                       )
    agent=create_pandas_dataframe_agent(llm=model,
                                        df=df,
                                        allow_dangerous_code=True,
                                        agent_executor_kwargs={"handle_parsing_errors": True},#模型自行处理错误
                                        verbose=True)#看执行过程
    prompt = PROMPT_TEMPLATE + query
    response = agent.invoke({"input": prompt})
    # 从输出中提取JSON部分
    output = response["output"]

    # 查找JSON格式的响应
    import re
    json_match = re.search(r'\{.*\}', output, re.DOTALL)

    if json_match:
        try:
            response_dict = json.loads(json_match.group())
            return response_dict
        except json.JSONDecodeError:
            # 如果JSON解析失败，返回原始输出
            return {"answer": output}
    else:
        # 如果没有找到JSON，返回整个输出
        return {"answer": output}

