"""
LitSynth Main Agent - Multi-agent literature review system
This is the main entry point that coordinates all the AI agents
"""

import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.adk import Agent, Runner
from google.adk.agents import ParallelAgent, LoopAgent
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
# AGENT 5: PARALLEL PAPER PROCESSOR (ParallelAgent)
# ============================================================================

# This agent spawns multiple PaperAnalyzerAgents to process papers concurrently
parallel_paper_processor = ParallelAgent(
    name="ParallelPaperProcessor",
    model=MODEL_NAME,
    instruction="""You coordinate parallel analysis of multiple academic papers.

You will receive a JSON array of papers from PaperDiscoveryAgent.
For each paper, spawn a PaperAnalyzerAgent to analyze it.
All papers will be processed simultaneously (in parallel).

Return a summary of all paper analyses.""",
    agents=[paper_analyzer_agent],  # This agent will be cloned for each paper
)

print("✓ ParallelPaperProcessor initialized")

# ============================================================================
# AGENT 6: REFINEMENT LOOP (LoopAgent)
# ============================================================================

# This agent iteratively refines the literature review until quality >= 8/10
refinement_loop = LoopAgent(
    name="RefinementLoop",
    model=MODEL_NAME,
    instruction="""You are the Quality Assurance Specialist for literature reviews.

LOOP PROCESS:
1. Receive a draft literature review
2. Use the evaluate_draft tool to assess quality (returns score 1-10)
3. If score >= 8.0: Return the final draft with "APPROVED" prefix
4. If score < 8.0: 
   - Analyze the feedback from evaluate_draft
   - Rewrite the draft to address all issues
   - Loop back to step 2

Maximum 3 iterations. Always improve based on specific feedback.""",
    tools=[evaluate_draft],
    max_iterations=3,
)

print("✓ RefinementLoop initialized")


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
    Executes a complete literature review for the given topic.
    Uses the full multi-agent pipeline.
    """
    print(f"\n{'='*60}")
    print(f"🔍 Starting Literature Review on: {topic}")
    print(f"{'='*60}\n")
    
    # Create unique session
    session_id = f"litsynth_{topic.replace(' ', '_')[:20]}"
    user_id = "default_user"
    
    # Initialize session
    session_service.create_session(
        app_name="LitSynth",
        user_id=user_id,
        session_id=session_id
    )
    
    # ========================================================================
    # PHASE 1: PAPER DISCOVERY
    # ========================================================================
    print("📊 Phase 1: Discovering relevant papers...")
    
    discovery_runner = Runner(
        agent=paper_discovery_agent,
        session_service=session_service,
        app_name="LitSynth"
    )
    
    discovery_prompt = f"Find 5 highly relevant academic papers about: {topic}. Return ONLY a JSON array with title, authors, year, venue, and URL for each paper."
    
    user_message = types.Content(
        parts=[types.Part(text=discovery_prompt)],
        role="user"
    )
    
    events = discovery_runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message
    )
    
    papers_json = ""
    for event in events:
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    papers_json += part.text
    
    print(f"✅ Found papers!\n")
    
    # Parse the JSON
    try:
        # Extract JSON from markdown code blocks if present
        if "```json" in papers_json:
            papers_json = papers_json.split("```json")[1].split("```")[0].strip()
        elif "```" in papers_json:
            papers_json = papers_json.split("```")[1].split("```")[0].strip()
        
        papers = json.loads(papers_json)
        print(f"📄 Discovered {len(papers)} papers")
    except json.JSONDecodeError:
        print("⚠️  JSON parsing failed, using mock data for demo")
        papers = [
            {"title": "Attention Is All You Need", "authors": ["Vaswani et al."], "year": 2017, "url": "https://arxiv.org/pdf/1706.03762.pdf"}
        ]
    
    # ========================================================================
    # PHASE 2: SYNTHESIS (Simplified for now - skip parallel processing)
    # ========================================================================
    print(f"\n📝 Phase 2: Synthesizing literature review...")
    
    synthesis_runner = Runner(
        agent=synthesis_agent,
        session_service=session_service,
        app_name="LitSynth"
    )
    
    # Create new session for synthesis
    synthesis_session_id = f"{session_id}_synthesis"
    session_service.create_session(
        app_name="LitSynth",
        user_id=user_id,
        session_id=synthesis_session_id
    )
    
    synthesis_prompt = f"""Create a literature review draft based on these papers:

{json.dumps(papers, indent=2)}

Write a structured literature review with:
- Introduction (context of {topic})
- Major Themes
- Key Findings
- Research Gaps
- Conclusion

Include citations in (Author, Year) format. Aim for 1000-1500 words."""
    
    synthesis_message = types.Content(
        parts=[types.Part(text=synthesis_prompt)],
        role="user"
    )
    
    events = synthesis_runner.run(
        user_id=user_id,
        session_id=synthesis_session_id,
        new_message=synthesis_message
    )
    
    draft_text = ""
    for event in events:
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    draft_text += part.text
                    print(part.text[:200] + "..." if len(part.text) > 200 else part.text)
    
    print(f"\n✅ Draft created ({len(draft_text.split())} words)")
    
    # ========================================================================
    # PHASE 3: REFINEMENT LOOP
    # ========================================================================
    print(f"\n🔄 Phase 3: Iterative refinement...")
    
    refinement_runner = Runner(
        agent=refinement_loop,
        session_service=session_service,
        app_name="LitSynth"
    )
    
    # Create session for refinement
    refinement_session_id = f"{session_id}_refinement"
    session_service.create_session(
        app_name="LitSynth",
        user_id=user_id,
        session_id=refinement_session_id
    )
    
    refinement_prompt = f"""Evaluate and refine this literature review draft:

{draft_text}

Use the evaluate_draft tool to score it. If score < 8, improve it based on feedback and re-evaluate. Loop until score >= 8 or max 3 iterations."""
    
    refinement_message = types.Content(
        parts=[types.Part(text=refinement_prompt)],
        role="user"
    )
    
    events = refinement_runner.run(
        user_id=user_id,
        session_id=refinement_session_id,
        new_message=refinement_message
    )
    
    final_review = ""
    for event in events:
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    final_review += part.text
    
    print(f"\n✅ Refinement complete!")
    
    # ========================================================================
    # FINAL OUTPUT
    # ========================================================================
    print(f"\n{'='*60}")
    print(f"📚 FINAL LITERATURE REVIEW")
    print(f"{'='*60}\n")
    print(final_review[:500] + "..." if len(final_review) > 500 else final_review)
    
    return final_review

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