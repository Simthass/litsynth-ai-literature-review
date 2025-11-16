"""
Citation extraction and formatting tools for LitSynth
"""

from typing import List, Dict


def extract_citation(
    title: str,
    authors: List[str],
    year: int,
    venue: str = ""
) -> Dict:
    """
    Generates a properly formatted citation in APA style.
    
    This tool is used by PaperAnalyzerAgent to create standardized citations
    for academic papers that can be included in the literature review.
    
    Args:
        title: Paper title
        authors: List of author names (e.g., ["John Doe", "Jane Smith"])
        year: Publication year
        venue: Publication venue (journal/conference name)
        
    Returns:
        dict: {
            "status": "success",
            "citation": "Formatted APA citation",
            "bibtex": "BibTeX entry (optional)"
        }
    
    Example:
        >>> result = extract_citation(
        ...     title="Attention Is All You Need",
        ...     authors=["Ashish Vaswani", "Noam Shazeer"],
        ...     year=2017,
        ...     venue="NeurIPS"
        ... )
        >>> print(result["citation"])
        "Vaswani, A., & Shazeer, N. (2017). Attention Is All You Need. NeurIPS."
    """
    try:
        if not authors or len(authors) == 0:
            return {
                "status": "error",
                "citation": None,
                "message": "No authors provided"
            }
        
        # Format authors in APA style
        formatted_authors = format_authors_apa(authors)
        
        # Build the citation
        citation_parts = [
            formatted_authors,
            f"({year})",
            f"*{title}*"  # Italicized title in markdown
        ]
        
        if venue:
            citation_parts.append(f"*{venue}*")  # Italicized venue
        
        citation = ". ".join(citation_parts) + "."
        
        # Generate BibTeX entry (bonus feature)
        bibtex = generate_bibtex(title, authors, year, venue)
        
        return {
            "status": "success",
            "citation": citation,
            "bibtex": bibtex,
            "message": "Citation generated successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "citation": None,
            "bibtex": None,
            "message": f"Error generating citation: {str(e)}"
        }


def format_authors_apa(authors: List[str]) -> str:
    """
    Formats author names in APA style.
    
    Rules:
    - One author: "LastName, F."
    - Two authors: "LastName1, F., & LastName2, F."
    - Three+ authors: "LastName1, F., LastName2, F., & LastName3, F."
    
    Args:
        authors: List of full author names
        
    Returns:
        str: Formatted author string
    """
    def format_single_author(name: str) -> str:
        """Convert 'First Last' to 'Last, F.'"""
        parts = name.strip().split()
        if len(parts) >= 2:
            last_name = parts[-1]
            first_initial = parts[0][0].upper()
            return f"{last_name}, {first_initial}."
        else:
            # If only one part, assume it's the last name
            return f"{parts[0]}."
    
    formatted = [format_single_author(author) for author in authors]
    
    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]}, & {formatted[1]}"
    else:
        # Three or more authors
        all_but_last = ", ".join(formatted[:-1])
        return f"{all_but_last}, & {formatted[-1]}"


def generate_bibtex(title: str, authors: List[str], year: int, venue: str) -> str:
    """
    Generates a BibTeX entry for the paper.
    
    Args:
        title: Paper title
        authors: List of author names
        year: Publication year
        venue: Publication venue
        
    Returns:
        str: BibTeX entry
    """
    # Create a citation key (first author last name + year)
    first_author = authors[0].split()[-1].lower() if authors else "unknown"
    cite_key = f"{first_author}{year}"
    
    # Format authors for BibTeX (Last, First and Last, First)
    bibtex_authors = " and ".join(authors)
    
    bibtex = f"""@article{{{cite_key},
  title={{{title}}},
  author={{{bibtex_authors}}},
  year={{{year}}},
  venue={{{venue}}}
}}"""
    
    return bibtex


# Test function for development
if __name__ == "__main__":
    print("Testing citation formatter...")
    
    # Test 1: Two authors
    result = extract_citation(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer"],
        year=2017,
        venue="NeurIPS"
    )
    print(f"\nTest 1 - Two Authors:")
    print(f"Status: {result['status']}")
    print(f"Citation: {result['citation']}")
    print(f"BibTeX:\n{result['bibtex']}")
    
    # Test 2: Many authors
    result = extract_citation(
        title="BERT: Pre-training of Deep Bidirectional Transformers",
        authors=["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
        year=2019,
        venue="NAACL"
    )
    print(f"\nTest 2 - Multiple Authors:")
    print(f"Citation: {result['citation']}")