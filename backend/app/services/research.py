import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

class ArxivClient:
    BASE_URL = "https://export.arxiv.org/api/query"

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
        return self._parse_response(response.text)

    def _parse_response(self, xml_content: str) -> List[Dict[str, Any]]:
        root = ET.fromstring(xml_content)
        # XML namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            published = entry.find('atom:published', ns).text
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns).text
                authors.append(name)
            
            link = entry.find("atom:link[@title='pdf']", ns)
            pdf_url = link.attrib['href'] if link is not None else None
            
            if not pdf_url:
                # Fallback to alternate link or construct it
                id_text = entry.find('atom:id', ns).text
                # typically http://arxiv.org/abs/2101.00001 -> http://arxiv.org/pdf/2101.00001
                if "/abs/" in id_text:
                    pdf_url = id_text.replace("/abs/", "/pdf/")

            papers.append({
                "source": "arXiv",
                "title": title,
                "abstract": summary,
                "authors": authors,
                "published_date": published,
                "pdf_url": pdf_url,
                "external_id": entry.find('atom:id', ns).text
            })
            
        return papers

            
        return papers

class SemanticScholarClient:
    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        params = {
            "query": query,
            "limit": max_results,
            "fields": "title,abstract,authors,year,externalIds,openAccessPdf"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                return self._parse_response(data)
            except Exception as e:
                print(f"Semantic Scholar error: {e}")
                return []

    def _parse_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        papers = []
        for entry in data.get("data", []):
            authors = [author["name"] for author in entry.get("authors", [])]
            
            pdf_info = entry.get("openAccessPdf")
            pdf_url = pdf_info.get("url") if pdf_info else None
            
            papers.append({
                "source": "Semantic Scholar",
                "title": entry.get("title"),
                "abstract": entry.get("abstract") or "No abstract available",
                "authors": authors,
                "published_date": str(entry.get("year")),
                "pdf_url": pdf_url,
                "external_id": entry.get("paperId")
            })
        return papers

class PubmedClient:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        # 1. Search for IDs
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Search IDs
                id_resp = await client.get(self.BASE_URL, params=search_params)
                id_resp.raise_for_status()
                id_data = id_resp.json()
                id_list = id_data.get("esearchresult", {}).get("idlist", [])
                
                if not id_list:
                    return []
                
                # Get Summaries
                ids = ",".join(id_list)
                summary_params = {
                    "db": "pubmed",
                    "id": ids,
                    "retmode": "json"
                }
                sum_resp = await client.get(self.SUMMARY_URL, params=summary_params)
                sum_resp.raise_for_status()
                sum_data = sum_resp.json()
                
                return self._parse_response(sum_data, id_list)
            except Exception as e:
                print(f"PubMed error: {e}")
                return []

    def _parse_response(self, data: Dict[str, Any], id_list: List[str]) -> List[Dict[str, Any]]:
        papers = []
        result = data.get("result", {})
        
        for pmid in id_list:
            if pmid not in result:
                continue
            item = result[pmid]
            
            # Construct a link to the article (often available via DOI or PubMed directly)
            # This is a simplification; authentic PDF retrieval from PubMed is complex.
            # We'll link to the abstract page.
            pdf_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            
            authors = [a.get("name", "") for a in item.get("authors", []) if "name" in a]
            
            papers.append({
                "source": "PubMed",
                "title": item.get("title", "No title"),
                "abstract": "Abstract not available in summary (requires fetch)", # esummary doesn't give full abstract
                "authors": authors,
                "published_date": item.get("pubdate", ""),
                "pdf_url": pdf_url,
                "external_id": pmid
            })
        return papers

class ResearchService:
    def __init__(self):
        self.arxiv = ArxivClient()
        self.semantic = SemanticScholarClient()
        self.pubmed = PubmedClient()

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        # Results distribution
        # If max_results=5, we try to get 2 from each or balanced.
        limit_per_source = (max_results // 3) + 1
        
        import asyncio
        arxiv_future = self.arxiv.search(query, max_results=limit_per_source)
        semantic_future = self.semantic.search(query, max_results=limit_per_source)
        pubmed_future = self.pubmed.search(query, max_results=limit_per_source)
        
        # Use return_exceptions=True to prevent one failure from crashing the whole search
        results = await asyncio.gather(arxiv_future, semantic_future, pubmed_future, return_exceptions=True)
        
        # Combine and flatten
        all_papers = []
        for res in results:
            if isinstance(res, Exception):
                print(f"Research source error: {res}")
                continue
            all_papers.extend(res)
            
        return all_papers[:max_results]

research_client = ResearchService()
