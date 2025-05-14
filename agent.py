from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from rank_checker import get_ranks_for_multiple_keywords

load_dotenv()



def rank_tool_func(input_text: str) -> str:
    """
    Expects input in the format: keyword|domain
    """
    try:
        keyword, domain = input_text.split("|")
        keyword, domain = keyword.strip(), domain.strip()
        return f"The rank of {domain} for '{keyword}' is: {get_ranks_for_multiple_keywords([keyword], domain)[keyword]}"
    except Exception as e:
        return f"Error parsing input: {e}"

def get_rank_agent():
    tools = [
        Tool(
            name="WebsiteRankTool",
            func=rank_tool_func,
            description="Use this to check the ranking of a website for a given keyword. Input should be: keyword|domain"
        )
    ]

    llm  = ChatGoogleGenerativeAI(model ='gemini-1.5-pro')
    agent = initialize_agent(tools=tools,
                             llm=llm,
                             agent="zero-shot-react-description",
                             verbose=True)
    return agent
