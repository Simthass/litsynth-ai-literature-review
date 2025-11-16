"""
Literature review draft evaluation tools for LitSynth
"""

import re
from typing import Dict, List


def evaluate_draft(draft_text: str, paper_titles: List[str] = None) -> Dict:
    """
    Evaluates a literature review draft against quality criteria.
    
    This tool is used by the RefinementLoop agent to assess draft quality
    and provide specific feedback for improvement. Scoring is based on
    multiple dimensions of academic writing quality.
    
    Args:
        draft_text: The literature review text to evaluate
        paper_titles: List of paper titles that should be covered (optional)
        
    Returns:
        dict: {
            "status": "success",
            "score": float (1-10),
            "feedback": {
                "structure": str,
                "coverage": str,
                "citations": str,
                "clarity": str,
                "length": str
            },
            "improvements_needed": List[str],
            "passed": bool (True if score >= 8)
        }
    
    Scoring Breakdown (10 points total):
        - Structure (2 pts): Has required sections with headers
        - Length (2 pts): Meets minimum word count (800-2000 words)
        - Citations (2 pts): Sufficient citations (min 5)
        - Coverage (2 pts): Discusses all provided papers
        - Clarity (2 pts): Readability and coherence
    """
    try:
        # Initialize scoring
        scores = {
            "structure": 0,
            "length": 0,
            "citations": 0,
            "coverage": 0,
            "clarity": 0
        }
        feedback = {}
        improvements = []
        
        # === 1. STRUCTURE EVALUATION (2 points) ===
        required_sections = [
            "introduction",
            "theme", 
            "finding",
            "gap",
            "conclusion"
        ]
        
        found_sections = []
        draft_lower = draft_text.lower()
        
        for section in required_sections:
            if section in draft_lower:
                found_sections.append(section)
        
        structure_score = (len(found_sections) / len(required_sections)) * 2
        scores["structure"] = structure_score
        
        if structure_score >= 1.5:
            feedback["structure"] = f"✓ Good structure with {len(found_sections)}/{len(required_sections)} key sections"
        else:
            feedback["structure"] = f"✗ Weak structure: only {len(found_sections)}/{len(required_sections)} sections found"
            missing = [s for s in required_sections if s not in found_sections]
            improvements.append(f"Add sections discussing: {', '.join(missing)}")
        
        # === 2. LENGTH EVALUATION (2 points) ===
        word_count = len(draft_text.split())
        
        if 1000 <= word_count <= 2000:
            scores["length"] = 2.0
            feedback["length"] = f"✓ Optimal length: {word_count} words"
        elif 800 <= word_count < 1000:
            scores["length"] = 1.5
            feedback["length"] = f"~ Slightly short: {word_count} words (aim for 1000+)"
            improvements.append("Expand discussion to reach 1000+ words")
        elif word_count < 800:
            scores["length"] = 1.0
            feedback["length"] = f"✗ Too short: {word_count} words (minimum 800)"
            improvements.append("Significantly expand content (need 800+ words)")
        else:  # > 2000
            scores["length"] = 1.5
            feedback["length"] = f"~ Too long: {word_count} words (aim for 1000-2000)"
            improvements.append("Condense to 1000-2000 words for better readability")
        
        # === 3. CITATIONS EVALUATION (2 points) ===
        # Count different citation patterns
        # Pattern 1: (Author, Year) or (Author et al., Year)
        apa_citations = len(re.findall(r'\([A-Z][a-z]+(?:\s+et\s+al\.)?,\s*\d{4}\)', draft_text))
        
        # Pattern 2: [1], [2], etc.
        numbered_citations = len(re.findall(r'\[\d+\]', draft_text))
        
        # Pattern 3: Author (Year) format
        narrative_citations = len(re.findall(r'[A-Z][a-z]+\s+\(\d{4}\)', draft_text))
        
        total_citations = apa_citations + numbered_citations + narrative_citations
        
        if total_citations >= 10:
            scores["citations"] = 2.0
            feedback["citations"] = f"✓ Excellent citation usage: {total_citations} citations"
        elif total_citations >= 5:
            scores["citations"] = 1.5
            feedback["citations"] = f"~ Adequate citations: {total_citations} (aim for 10+)"
            improvements.append("Add more citations to support claims")
        else:
            scores["citations"] = 1.0
            feedback["citations"] = f"✗ Insufficient citations: {total_citations} (minimum 5)"
            improvements.append("Add citations for all key claims (need 5+ citations)")
        
        # === 4. COVERAGE EVALUATION (2 points) ===
        if paper_titles:
            covered_papers = sum(1 for title in paper_titles if any(word.lower() in draft_lower for word in title.split() if len(word) > 4))
            coverage_ratio = covered_papers / len(paper_titles)
            scores["coverage"] = coverage_ratio * 2
            
            if coverage_ratio >= 0.8:
                feedback["coverage"] = f"✓ Good coverage: {covered_papers}/{len(paper_titles)} papers discussed"
            else:
                feedback["coverage"] = f"✗ Incomplete coverage: only {covered_papers}/{len(paper_titles)} papers mentioned"
                improvements.append("Discuss all provided papers in the review")
        else:
            # If no paper list provided, give full points (benefit of doubt)
            scores["coverage"] = 2.0
            feedback["coverage"] = "✓ Coverage check skipped (no paper list provided)"
        
        # === 5. CLARITY EVALUATION (2 points) ===
        # Simple heuristics for readability
        sentences = re.split(r'[.!?]+', draft_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) == 0:
            avg_sentence_length = 0
        else:
            avg_sentence_length = word_count / len(sentences)
        
        # Check for academic markers
        academic_markers = [
            "however", "moreover", "furthermore", "therefore", "consequently",
            "research", "study", "findings", "approach", "methodology"
        ]
        marker_count = sum(1 for marker in academic_markers if marker in draft_lower)
        
        # Scoring clarity
        clarity_score = 0
        if 15 <= avg_sentence_length <= 25:  # Optimal sentence length
            clarity_score += 1.0
        elif 10 <= avg_sentence_length < 30:
            clarity_score += 0.5
        
        if marker_count >= 5:  # Good use of academic language
            clarity_score += 1.0
        elif marker_count >= 3:
            clarity_score += 0.5
        
        scores["clarity"] = clarity_score
        
        if clarity_score >= 1.5:
            feedback["clarity"] = f"✓ Clear academic writing (avg sentence: {avg_sentence_length:.1f} words)"
        else:
            feedback["clarity"] = f"~ Clarity could improve (avg sentence: {avg_sentence_length:.1f} words)"
            if avg_sentence_length > 30:
                improvements.append("Shorten sentences for better readability")
            elif avg_sentence_length < 10:
                improvements.append("Use more complex sentences for academic tone")
            if marker_count < 3:
                improvements.append("Use more transitional phrases and academic language")
        
        # === CALCULATE FINAL SCORE ===
        final_score = sum(scores.values())
        passed = final_score >= 8.0
        
        return {
            "status": "success",
            "score": round(final_score, 1),
            "max_score": 10.0,
            "breakdown": scores,
            "feedback": feedback,
            "improvements_needed": improvements,
            "passed": passed,
            "message": f"Evaluation complete. Score: {final_score:.1f}/10.0"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "score": 0,
            "feedback": {},
            "improvements_needed": [],
            "passed": False,
            "message": f"Error evaluating draft: {str(e)}"
        }


# Test function for development
if __name__ == "__main__":
    print("Testing draft evaluation tool...")
    
    # Test 1: Good quality draft
    good_draft = """
    Introduction
    
    Transformer architectures have revolutionized natural language processing (Smith, 2020). 
    This review examines recent advances in attention mechanisms and their applications.
    
    Major Themes
    
    Research shows that self-attention enables models to capture long-range dependencies (Jones et al., 2021).
    Moreover, multi-head attention provides multiple representation subspaces (Brown, 2019).
    Furthermore, positional encoding remains crucial for sequence modeling (Davis, 2022).
    
    Key Findings
    
    Studies demonstrate that transformers outperform RNNs on most benchmarks (Wilson, 2020).
    However, computational costs remain a challenge for deployment (Taylor, 2021).
    Recent work explores efficient attention mechanisms (Anderson, 2023).
    
    Research Gaps
    
    Current research lacks comprehensive analysis of multilingual performance.
    Additionally, theoretical understanding of attention mechanisms needs development.
    
    Conclusion
    
    Transformer architectures represent a paradigm shift in NLP (Miller, 2022).
    Future research should address efficiency and theoretical foundations.
    Therefore, continued investigation into attention mechanisms is essential (Lee, 2023).
    """
    
    result = evaluate_draft(good_draft)
    print(f"\nTest 1 - Good Quality Draft:")
    print(f"Status: {result['status']}")
    print(f"Score: {result['score']}/10.0")
    print(f"Passed: {result['passed']}")
    print(f"\nFeedback:")
    for dimension, comment in result['feedback'].items():
        print(f"  {dimension}: {comment}")
    print(f"\nImprovements needed: {result['improvements_needed']}")
    
    # Test 2: Poor quality draft
    poor_draft = """
    This is about transformers. They are good. Many people use them.
    Transformers work well. They are better than old methods.
    """
    
    result = evaluate_draft(poor_draft)
    print(f"\n\nTest 2 - Poor Quality Draft:")
    print(f"Score: {result['score']}/10.0")
    print(f"Passed: {result['passed']}")
    print(f"\nImprovements needed:")
    for improvement in result['improvements_needed']:
        print(f"  - {improvement}")