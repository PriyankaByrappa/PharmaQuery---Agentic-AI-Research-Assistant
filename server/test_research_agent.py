
import asyncio
import sys
import os

# Add the server directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'd:/small projects/Pharma_Q/PharmaQuery/server')))

from agents.research_agent import ResearchAgent

async def test_annotations():
    agent = ResearchAgent()
    
    test_text = """
    Document Review Test Paper.
    
    The results demonstrate that the proposed method is highly effective for large scale data analysis.
    This sentence should trigger plagiarism from Journal of Academic Excellence.
    
    Redundancy test follow. This is a very important sentence that needs to be repeated for testing.
    This is a very important sentence that needs to be repeated for testing.
    
    Uncited claim: studies show that research is good for the soul.
    
    Novel contribution: we propose a novel framework for AI evaluation.
    
    Weak argument: it might possibly be better to do this.
    """
    
    print("Executing research agent...")
    result = await agent.execute("test_session", "Test Topic", uploaded_paper=test_text)
    
    if result["status"] == "success":
        data = result["data"]
        annotations = data["annotations"]
        print(f"Found {len(annotations)} annotations:")
        for a in annotations:
            print(f"- [{a['tag']}] {a['content'][:50]}...")
            if 'source_name' in a:
                print(f"  Source: {a['source_name']} ({a['source_link']})")
    else:
        print(f"Error: {result['logs'][-1]}")

if __name__ == "__main__":
    asyncio.run(test_annotations())
