import os
from firecrawl import Firecrawl
from dotenv import load_dotenv

load_dotenv()


class FirecrawlService:
    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("Missing FIRECRAWL_API_KEY environment variable")
        self.app = Firecrawl(api_key=api_key)  # Changed from FirecrawlApp

    def search_companies(self, query: str, num_results: int = 2):
        try:
            # Use scrape_options parameter (not params)
            result = self.app.search(
                query=f"{query} company pricing",
                limit=num_results,
                scrape_options={  # Changed from params
                    "formats": ["markdown"]
                }
            )
            return result
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def scrape_company_pages(self, url: str):
        try:
            # Use scrape() method instead of scrape_url()
            result = self.app.scrape(
                url,
                formats=["markdown"]
            )
            return result
        except Exception as e:
            print(f"Scrape error: {e}")
            return None

if __name__ == "__main__":

    firecrawl_service = FirecrawlService()

    result = firecrawl_service.search_companies("google")
    print(result)

# for doc in result.web:
#     print(doc.metadata.title)

# result = firecrawl_service.scrape_company_pages("https://www.google.com")
# print(result)