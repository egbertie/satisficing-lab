# arXiv Web Scraper (No API Required)
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_arxiv(query, max_results=3, days=7):
    """
    Scrape arXiv search results without API key
    """
    base_url = "https://arxiv.org/search/"
    params = {
        'query': query,
        'searchtype': 'all',
        'order': '-announced_date_first',
        'size': max_results
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; AcademicBot/1.0)'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Parse search results
        items = soup.find_all('li', class_='arxiv-result')
        
        for item in items[:max_results]:
            try:
                title_tag = item.find('p', class_='title')
                title = title_tag.text.strip() if title_tag else 'N/A'
                
                authors_tag = item.find('p', class_='authors')
                authors = authors_tag.text.strip() if authors_tag else 'N/A'
                
                abstract_tag = item.find('span', class_='abstract-short')
                abstract = abstract_tag.text.strip() if abstract_tag else 'N/A'
                
                link_tag = item.find('a', href=True)
                link = 'https://arxiv.org' + link_tag['href'] if link_tag else 'N/A'
                
                results.append({
                    'title': title[:150],
                    'authors': authors[:100],
                    'abstract': abstract[:200],
                    'link': link,
                    'queried_at': datetime.now().isoformat()
                })
            except Exception as e:
                continue
        
        return {
            'query': query,
            'count': len(results),
            'results': results
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'query': query,
            'count': 0,
            'results': []
        }

# Example usage
if __name__ == '__main__':
    result = scrape_arxiv('partner selection decision making', max_results=3)
    print(json.dumps(result, indent=2, ensure_ascii=False))
