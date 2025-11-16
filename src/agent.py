"""
LitSynth Main Agent Configuration
Entry point for the multi-agent literature review system
"""

import os
from dotenv import load_dotenv
from google.genai import types

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")

# Model configuration with retry settings
MODEL_CONFIG = types.GenerateContentConfig(
    temperature=0.7,
    top_p=0.95,
    max_output_tokens=8192,
    response_modalities=["TEXT"],
)

# We'll build the agents here in subsequent steps
if __name__ == "__main__":
    print("🔬 LitSynth Agent System")
    print("=" * 50)
    print("Setup complete. Ready for agent implementation.")
    print("=" * 50)