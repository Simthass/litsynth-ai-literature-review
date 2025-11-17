"""
LitSynth Main Agent - Multi-agent literature review system
This is the main entry point that coordinates all the AI agents
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService, Session
from google.adk.tools.google_search_tool import google_search

# Our custom tools for handling PDFs, citations, and evaluation
from tools.pdf_tools import fetch_pdf
from tools.citation_tools import extract_citation
from tools.evaluation_tools import evaluate_draft

# Agent instructions and prompts
from config.prompts import AGENT_PROMPTS

# Load API keys and environment variables
load_dotenv()

# Get the Google API key - crash if it's missing
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY - check your .env file")

# Set up the AI client with our API key
client = genai.Client(api_key=API_KEY)

# Session service keeps track of conversations and context
session_service = InMemorySessionService()

# Using the latest Gemini model for all our agents
MODEL_NAME = "gemini-2.5-flash"

print("🔬 LitSynth: AI-Powered Literature Review Co-pilot")
print("=" * 60)
print(f"✓ API Key loaded")
print(f"✓ Model: {MODEL_NAME}")
print(f"✓ Session service ready")
print(f"✓ Custom tools loaded: PDF fetcher, citation extractor, draft evaluator")
print("=" * 60)


# ============================================================================
# AGENT 1: PAPER DISCOVERY AGENT - Finds relevant research papers
# ============================================================================

paper_discovery_agent = Agent(
    name="PaperDiscoveryAgent",
    model=MODEL_NAME,
    instruction=AGENT_PROMPTS["paper_discovery"],
    tools=[google_search],
)

print("✓ PaperDiscoveryAgent ready - will search for relevant papers")


# ============================================================================
# AGENT 2: PAPER ANALYZER AGENT - Reads and analyzes papers
# ============================================================================

paper_analyzer_agent = Agent(
    name="PaperAnalyzerAgent",
    model=MODEL_NAME,
    instruction=AGENT_PROMPTS["paper_analyzer"],
    tools=[fetch_pdf, extract_citation],
)

print("✓ PaperAnalyzerAgent ready - can fetch PDFs and extract citations")


# ============================================================================
# AGENT 3: SYNTHESIS AGENT - Combines insights from multiple papers
# ============================================================================

synthesis_agent = Agent(
    name="SynthesisAgent",
    model=MODEL_NAME,
    instruction=AGENT_PROMPTS["synthesis"],
    tools=[],
)

print("✓ SynthesisAgent ready - will combine findings into coherent review")


# ============================================================================
# AGENT 4: REFINEMENT AGENT - Improves and polishes the draft
# ============================================================================

refinement_agent = Agent(
    name="RefinementAgent",
    model=MODEL_NAME,
    instruction=AGENT_PROMPTS["refinement"],
    tools=[evaluate_draft],
)

print("✓ RefinementAgent ready - will evaluate and improve the draft")


# ============================================================================
# ORCHESTRATION: BUILD THE MULTI-AGENT SYSTEM
# ============================================================================

def create_research_coordinator():
    """
    Creates the main coordinator agent that manages the whole workflow.
    
    This sets up:
    - Sequential flow: Steps happen in order
    - Parallel processing: Multiple papers analyzed at once (coming soon)
    - Iterative refinement: Multiple improvement cycles (coming soon)
    - Custom tools: PDF handling, citation extraction, quality evaluation
    - Google Search: Finding relevant academic papers
    
    Returns:
        Agent: The main coordinator agent
    """
    
    # Starting with a simple sequential flow for now
    # Will add parallel processing and looping in the next update
    
    root_agent = Agent(
        name="ResearchCoordinator",
        model=MODEL_NAME,
        instruction=AGENT_PROMPTS["research_coordinator"],
        tools=[],  # Main agent delegates work to specialized agents
    )
    
    print("✓ ResearchCoordinator (main agent) ready")
    
    return root_agent


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_literature_review(topic: str):
    """
    Runs a complete literature review for the given topic.
    This is where the magic happens - all agents work together here.
    """
    print(f"\n{'='*60}")
    print(f"🔍 Starting Literature Review on: {topic}")
    print(f"{'='*60}\n")
    
    print("📊 Phase 1: Finding relevant papers...")
    
    # Set up the runner that will execute our discovery agent
    discovery_runner = Runner(
        agent=paper_discovery_agent,
        session_service=session_service,
        app_name="LitSynth"
    )
    
    # Session setup - keeps track of the conversation
    session_id = "discovery_session_1"
    user_id = "default_user"
    
    # Create a new session for this research task
    session_service.create_session(
        app_name="LitSynth",
        user_id=user_id,
        session_id=session_id
    )
    
    # Build the search prompt for the discovery agent
    discovery_prompt = f"Find 5 highly relevant academic papers about: {topic}. Return the results as a JSON array with title, authors, year, venue, and URL for each paper."
    
    # Create the message object that the agent expects
    user_message = types.Content(
        parts=[types.Part(text=discovery_prompt)],
        role="user"
    )
    
    # Run the discovery agent and capture the results
    events = discovery_runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message
    )
    
    # Process the agent's response - collect all the text it generates
    response_text = ""
    print("\n🔄 Processing agent response...\n")
    
    for event in events:
        # Check what type of event we're dealing with
        event_type = type(event).__name__
        
        # Look for text content in the event
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text
                    print(part.text)  # Show progress as we get responses
        
        # Some events might have text directly
        elif hasattr(event, 'text') and event.text:
            response_text += event.text
            print(event.text)
    
    print("\n✅ Paper Discovery Complete!")
    print("\nDiscovered Papers Summary:")
    print(response_text if response_text else "No papers found (might need to adjust the search prompt)")
    
    return response_text

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 LITSYNTH TEST RUN - Checking if everything works")
    print("="*60)
    
    # Test with a sample topic to see if the system works
    test_topic = "attention mechanisms in transformer models"
    
    try:
        result = run_literature_review(test_topic)
        print("\n" + "="*60)
        print("✅ Test completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()