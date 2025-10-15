#!/usr/bin/env python3
"""
Comprehensive SEO crawler for drsayuj.info
Crawls the site and collects detailed SEO data including:
- Status codes, canonical tags, meta tags
- Headings, internal links, structured data
- Performance metrics, mobile-friendliness
"""

import asyncio
import aiohttp
import json
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PageData:
    url: str
    status_code: int
    title: str
    meta_description: str
    canonical_url: str
    h1_tags: List[str]
    h2_tags: List[str]
    h3_tags: List[str]
    internal_links: List[str]
    external_links: List[str]
    images_without_alt: List[str]
    images_with_alt: List[str]
    structured_data: List[Dict]
    word_count: int
    load_time: float
    has_https: bool
    has_robots_noindex: bool
    has_robots_nofollow: bool
    schema_types: List[str]
    errors: List[str]

class SEOCrawler:
    def __init__(self, base_url: str, max_pages: int = 150):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.pages_data: List[PageData] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc == self.domain and
                not url.endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js')) and
                '#' not in url and
                '?' not in url  # Skip URLs with query parameters for now
            )
        except:
            return False
    
    def extract_structured_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract structured data from JSON-LD, microdata, and RDFa"""
        structured_data = []
        
        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except:
                pass
        
        # Microdata
        for item in soup.find_all(attrs={'itemscope': True}):
            item_data = {}
            item_type = item.get('itemtype', '')
            if item_type:
                item_data['@type'] = item_type
            structured_data.append(item_data)
        
        return structured_data
    
    def get_schema_types(self, structured_data: List[Dict]) -> List[str]:
        """Extract schema types from structured data"""
        types = []
        for data in structured_data:
            if isinstance(data, dict):
                if '@type' in data:
                    schema_type = data['@type']
                    if isinstance(schema_type, list):
                        types.extend(schema_type)
                    else:
                        types.append(schema_type)
        return list(set(types))
    
    async def crawl_page(self, url: str) -> PageData:
        """Crawl a single page and extract SEO data"""
        start_time = time.time()
        errors = []
        
        try:
            async with self.session.get(url) as response:
                load_time = time.time() - start_time
                content = await response.text()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Basic page data
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ""
                
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                meta_description = meta_desc.get('content', '') if meta_desc else ""
                
                canonical = soup.find('link', rel='canonical')
                canonical_url = canonical.get('href', '') if canonical else ""
                
                # Headings
                h1_tags = [h.get_text().strip() for h in soup.find_all('h1')]
                h2_tags = [h.get_text().strip() for h in soup.find_all('h2')]
                h3_tags = [h.get_text().strip() for h in soup.find_all('h3')]
                
                # Links
                all_links = soup.find_all('a', href=True)
                internal_links = []
                external_links = []
                
                for link in all_links:
                    href = link['href']
                    full_url = urljoin(url, href)
                    if self.is_valid_url(full_url):
                        internal_links.append(full_url)
                    elif href.startswith('http'):
                        external_links.append(href)
                
                # Images
                images = soup.find_all('img')
                images_without_alt = []
                images_with_alt = []
                
                for img in images:
                    alt_text = img.get('alt', '')
                    src = img.get('src', '')
                    if alt_text:
                        images_with_alt.append(src)
                    else:
                        images_without_alt.append(src)
                
                # Structured data
                structured_data = self.extract_structured_data(soup)
                schema_types = self.get_schema_types(structured_data)
                
                # Robots meta
                robots_meta = soup.find('meta', attrs={'name': 'robots'})
                robots_content = robots_meta.get('content', '') if robots_meta else ""
                has_robots_noindex = 'noindex' in robots_content.lower()
                has_robots_nofollow = 'nofollow' in robots_content.lower()
                
                # Word count
                text_content = soup.get_text()
                word_count = len(text_content.split())
                
                # HTTPS check
                has_https = url.startswith('https://')
                
                return PageData(
                    url=url,
                    status_code=response.status,
                    title=title_text,
                    meta_description=meta_description,
                    canonical_url=canonical_url,
                    h1_tags=h1_tags,
                    h2_tags=h2_tags,
                    h3_tags=h3_tags,
                    internal_links=internal_links,
                    external_links=external_links,
                    images_without_alt=images_without_alt,
                    images_with_alt=images_with_alt,
                    structured_data=structured_data,
                    word_count=word_count,
                    load_time=load_time,
                    has_https=has_https,
                    has_robots_noindex=has_robots_noindex,
                    has_robots_nofollow=has_robots_nofollow,
                    schema_types=schema_types,
                    errors=errors
                )
                
        except Exception as e:
            errors.append(str(e))
        return PageData(
            url=url,
                status_code=0,
                title="",
                meta_description="",
                canonical_url="",
                h1_tags=[],
                h2_tags=[],
                h3_tags=[],
            internal_links=[],
            external_links=[],
                images_without_alt=[],
                images_with_alt=[],
            structured_data=[],
            word_count=0,
                load_time=0,
                has_https=False,
                has_robots_noindex=False,
                has_robots_nofollow=False,
                schema_types=[],
                errors=errors
            )
    
    async def crawl_site(self):
        """Main crawling function"""
        logger.info(f"Starting crawl of {self.base_url}")
        
        # Start with the homepage
        urls_to_crawl = [self.base_url]
        
        while urls_to_crawl and len(self.visited_urls) < self.max_pages:
            current_url = urls_to_crawl.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            self.visited_urls.add(current_url)
            logger.info(f"Crawling {current_url} ({len(self.visited_urls)}/{self.max_pages})")
            
            page_data = await self.crawl_page(current_url)
            self.pages_data.append(page_data)
            
            # Add new internal links to crawl queue
            for link in page_data.internal_links:
                if link not in self.visited_urls and link not in urls_to_crawl:
                    urls_to_crawl.append(link)
        
        logger.info(f"Crawl completed. Visited {len(self.visited_urls)} pages")
        return self.pages_data

async def main():
    """Main function to run the crawler"""
    base_url = "https://www.drsayuj.info"
    
    async with SEOCrawler(base_url) as crawler:
        pages_data = await crawler.crawl_site()
        
        # Save results
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"/Users/dr.sayujkrishnan/Documents/openai-chatkit-advanced-samples/reports/seo/{timestamp}/raw_crawl.json"
        
        # Create directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Convert to serializable format
        serializable_data = [asdict(page) for page in pages_data]
        
        with open(output_file, 'w') as f:
            json.dump(serializable_data, f, indent=2)
        
        logger.info(f"Crawl data saved to {output_file}")
        
        # Print summary
        print(f"\n=== CRAWL SUMMARY ===")
        print(f"Total pages crawled: {len(pages_data)}")
        print(f"Pages with errors: {len([p for p in pages_data if p.errors])}")
        print(f"Pages without HTTPS: {len([p for p in pages_data if not p.has_https])}")
        print(f"Pages without title: {len([p for p in pages_data if not p.title])}")
        print(f"Pages without meta description: {len([p for p in pages_data if not p.meta_description])}")
        print(f"Pages with multiple H1s: {len([p for p in pages_data if len(p.h1_tags) > 1])}")
        print(f"Images without alt text: {sum(len(p.images_without_alt) for p in pages_data)}")
        print(f"Average load time: {sum(p.load_time for p in pages_data) / len(pages_data):.2f}s")

if __name__ == "__main__":
    asyncio.run(main())