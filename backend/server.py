from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Pydantic model for structured response
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

# Load AI Model (Claude 3.5)
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

# Create prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """
            You are a research assistant that will help generate a research paper.
            Answer the user query and use necessary tools.
            Wrap the output in this format and provide no other text\n{format_instructions}
        """),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

# Register tools
tools = [search_tool, wiki_tool, save_tool]

# Create Agent
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Request Model
class QueryRequest(BaseModel):
    query: str

# API Endpoint for query
@app.post("/query/")
async def query(request: QueryRequest):
    try:
        # Invoke the agent
        raw_response = agent_executor.invoke({"query": request.query})
        output_text = raw_response.get("output", [{}])

        if isinstance(output_text, list) and len(output_text) > 0 and "text" in output_text[0]:
            output_text = output_text[0]["text"]

        structured_response = parser.parse(output_text)
        return {
            "topic": structured_response.topic,
            "summary": structured_response.summary,
            "sources": structured_response.sources,
            "tools_used": structured_response.tools_used
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/")
async def root():
    return {"message": "AI Research Assistant is running!"}
