from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool

# Initialize FastAPI
app = FastAPI()

# Define Pydantic model for request and response
class QueryRequest(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

# Initialize LLM
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

# Create prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """
        You are a research assistant that will help generate a research paper.
        Answer the user query and use necessary tools.
        Wrap the output in this format and provide no other text\n{format_instructions}
    """),
    ("human", "{query}"),
]).partial(format_instructions=parser.get_format_instructions())

# Create tools and agent
tools = [search_tool, wiki_tool, save_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# API endpoint to handle queries
@app.post("/query/")
async def query(request: QueryRequest):
    try:
        user_input = request.query
        raw_response = agent_executor.invoke({"query": user_input})
        output_text = raw_response.get("output", [{}])

        # Handle the output type
        if isinstance(output_text, list) and len(output_text) > 0 and "text" in output_text[0]:
            output_text = output_text[0]["text"]

        structured_response = parser.parse(output_text)
        return {
            "topic": structured_response.topic,
            "summary": structured_response.summary,
            "sources": structured_response.sources,
            "tools_used": structured_response.tools_used
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint for health check
@app.get("/")
def root():
    return {"message": "AI Research Assistant is running!"}
