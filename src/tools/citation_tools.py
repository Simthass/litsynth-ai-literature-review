"""
Citation extraction and formatting tools for LitSynth
"""

from typing import List, Dict
from datetime import datetime

def extract_citation(
    title: str,
    authors: List[str],
    year: int,
    venue: str = ""
) -> Dict:
    """
    Improved citation extraction with validation
    """
    try:
        # Validate metadata first
        validated = validate_citation_metadata(title, authors, year, venue)
        
        title = validated["validated_title"]
        authors = validated["validated_authors"] 
        year = validated["validated_year"]
        venue = validated["validated_venue"]
        
        if validated["validation_issues"]:
            print(f"Citation validation issues: {validated['validation_issues']}")
        
        # Format authors with improved function
        formatted_authors = format_authors_apa(authors)
        
        # Build citation
        citation_parts = [
            formatted_authors,
            f"({year})",
            f"*{title}*"
        ]
        
        if venue and venue != "Unknown Venue":
            citation_parts.append(f"*{venue}*")
        
        citation = ". ".join(citation_parts) + "."
        
        # Generate BibTeX
        bibtex = generate_bibtex(title, authors, year, venue)
        
        return {
            "status": "success",
            "citation": citation,
            "bibtex": bibtex,
            "validation_issues": validated["validation_issues"],
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
    Improved author formatting with better error handling
    """
    def format_single_author(name: str) -> str:
        """Convert 'First Last' to 'Last, F.' with robust parsing"""
        if not name or name.strip() == "":
            return "Unknown"
            
        parts = name.strip().split()
        
        # Handle "et al." and other special cases
        if "et al" in name.lower():
            return "et al."
            
        # Handle single name (like "Unknown")
        if len(parts) == 1:
            return f"{parts[0]}."
            
        # Standard "First Last" format
        if len(parts) >= 2:
            last_name = parts[-1]
            first_initial = parts[0][0].upper() + "."
            return f"{last_name}, {first_initial}"
            
        return "Unknown"

    if not authors or len(authors) == 0:
        return "Unknown"
        
    # Filter out empty authors
    valid_authors = [author for author in authors if author and author.strip()]
    
    if not valid_authors:
        return "Unknown"
        
    formatted = [format_single_author(author) for author in valid_authors]

    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} & {formatted[1]}"
    else:
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
    
def validate_citation_metadata(title: str, authors: List[str], year: int, venue: str) -> Dict:
    """
    Validate citation metadata before generating citation
    """
    issues = []
    
    if not title or len(title.strip()) < 5:
        issues.append("Title too short or missing")
        title = "Unknown Title"
    
    if not authors or len(authors) == 0:
        issues.append("No authors provided")
        authors = ["Unknown"]
    else:
        # Clean author list
        authors = [author.strip() for author in authors if author and author.strip()]
        if not authors:
            authors = ["Unknown"]
    
    if not year or year < 1900 or year > 2030:
        issues.append(f"Invalid year: {year}")
        year = datetime.now().year  # Default to current year
    
    if not venue or len(venue.strip()) < 2:
        issues.append("Venue missing or too short")
        venue = "Unknown Venue"
    
    return {
        "validated_title": title,
        "validated_authors": authors,
        "validated_year": year,
        "validated_venue": venue,
        "validation_issues": issues
    }