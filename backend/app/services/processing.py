import httpx
import io
from pypdf import PdfReader
from typing import Optional

class DocumentProcessor:
    async def download_pdf(self, url: str) -> Optional[bytes]:
        if not url:
            return None
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
            except Exception as e:
                print(f"Error downloading PDF from {url}: {e}")
                return None

    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(pdf_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return self._clean_text(text)
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    def _clean_text(self, text: str) -> str:
        # Basic cleaning: remove excessive whitespace, null bytes, etc.
        text = text.replace("\x00", "")
        # Normalize whitespace
        return " ".join(text.split())

document_processor = DocumentProcessor()
