#!/usr/bin/env python3
"""
Comprehensive SEO Crawler for drsayuj.info
Performs in-depth analysis of all pages including structured data, performance, and technical SEO
"""

import asyncio
import aiohttp
import json
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Optional, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PageAnalysis:
    url: str
    status_code: int
    final_url: str
    content_type: str
    canonical: str
    title: str
    meta_description: str
    meta_robots: str
    h1: List[str]
    h2: List[str]
    h3: List[str]
    internal_links: List[str]
    external_links: List[str]
    images_with_alt: List[str]
    images_without_alt: List[str]
    structured_data: List[Dict]
    word_count: int
    load_time: float
    has_https: bool
    has_lazy_loading: bool
    last_modified: Optional[str]
    errors: List[str]

class ComprehensiveSEOCrawler:
    def __init__(self, base_url: str, max_pages: int = 150):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.pages_data: List[PageAnalysis] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.robots_txt: str = ""
        self.sitemap_urls: List[str] = []
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_robots_txt(self) -> str:
        """Fetch and parse robots.txt"""
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    self.robots_txt = await response.text()
                    logger.info("Robots.txt fetched successfully")
                else:
                    logger.warning(f"Robots.txt not found: {response.status}")
        except Exception as e:
            logger.error(f"Error fetching robots.txt: {e}")
        return self.robots_txt
    
    async def fetch_sitemap(self) -> List[str]:
        """Fetch and parse sitemap.xml"""
        try:
            sitemap_url = urljoin(self.base_url, '/sitemap.xml')
            async with self.session.get(sitemap_url) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'xml')
                    urls = []
                    for loc in soup.find_all('loc'):
                        url = loc.get_text().strip()
                        if self.is_valid_url(url):
                            urls.append(url)
                    self.sitemap_urls = urls
                    logger.info(f"Sitemap fetched: {len(urls)} URLs found")
                else:
                    logger.warning(f"Sitemap not found: {response.status}")
        except Exception as e:
            logger.error(f"Error fetching sitemap: {e}")
        return self.sitemap_urls
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc == self.domain and
                not url.endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.ico')) and
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
                if isinstance(data, list):
                    structured_data.extend(data)
                else:
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
    
    async def analyze_page(self, url: str) -> PageAnalysis:
        """Comprehensive analysis of a single page"""
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
                
                robots_meta = soup.find('meta', attrs={'name': 'robots'})
                robots_content = robots_meta.get('content', '') if robots_meta else ""
                
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
                images_with_alt = []
                images_without_alt = []
                
                for img in images:
                    alt_text = img.get('alt', '')
                    src = img.get('src', '')
                    if alt_text:
                        images_with_alt.append(src)
                    else:
                        images_without_alt.append(src)
                
                # Structured data
                structured_data = self.extract_structured_data(soup)
                
                # Word count
                text_content = soup.get_text()
                word_count = len(text_content.split())
                
                # HTTPS check
                has_https = url.startswith('https://')
                
                # Lazy loading check
                has_lazy_loading = any(img.get('loading') == 'lazy' for img in images)
                
                # Last modified
                last_modified = None
                lastmod_meta = soup.find('meta', attrs={'name': 'last-modified'})
                if lastmod_meta:
                    last_modified = lastmod_meta.get('content')
                
                return PageAnalysis(
                    url=url,
                    status_code=response.status,
                    final_url=str(response.url),
                    content_type=response.headers.get('content-type', ''),
                    canonical=canonical_url,
                    title=title_text,
                    meta_description=meta_description,
                    meta_robots=robots_content,
                    h1=h1_tags,
                    h2=h2_tags,
                    h3=h3_tags,
                    internal_links=internal_links,
                    external_links=external_links,
                    images_with_alt=images_with_alt,
                    images_without_alt=images_without_alt,
                    structured_data=structured_data,
                    word_count=word_count,
                    load_time=load_time,
                    has_https=has_https,
                    has_lazy_loading=has_lazy_loading,
                    last_modified=last_modified,
                    errors=errors
                )
                
        except Exception as e:
            errors.append(str(e))
            return PageAnalysis(
                url=url,
                status_code=0,
                final_url="",
                content_type="",
                canonical="",
                title="",
                meta_description="",
                meta_robots="",
                h1=[],
                h2=[],
                h3=[],
                internal_links=[],
                external_links=[],
                images_with_alt=[],
                images_without_alt=[],
                structured_data=[],
                word_count=0,
                load_time=0,
                has_https=False,
                has_lazy_loading=False,
                last_modified=None,
                errors=errors
            )
    
    async def crawl_site(self):
        """Main crawling function"""
        logger.info(f"Starting comprehensive crawl of {self.base_url}")
        
        # Fetch robots.txt and sitemap
        await self.fetch_robots_txt()
        await self.fetch_sitemap()
        
        # Start with sitemap URLs
        urls_to_crawl = self.sitemap_urls.copy()
        
        while urls_to_crawl and len(self.visited_urls) < self.max_pages:
            current_url = urls_to_crawl.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            self.visited_urls.add(current_url)
            logger.info(f"Crawling {current_url} ({len(self.visited_urls)}/{self.max_pages})")
            
            page_data = await self.analyze_page(current_url)
            self.pages_data.append(page_data)
            
            # Add new internal links to crawl queue
            for link in page_data.internal_links:
                if link not in self.visited_urls and link not in urls_to_crawl:
                    urls_to_crawl.append(link)
        
        logger.info(f"Crawl completed. Visited {len(self.visited_urls)} pages")
        return self.pages_data

async def main():
    """Main function to run the comprehensive crawler"""
    base_url = "https://www.drsayuj.info"
    
    async with ComprehensiveSEOCrawler(base_url) as crawler:
        pages_data = await crawler.crawl_site()
        
        # Save results
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"/Users/dr.sayujkrishnan/Documents/openai-chatkit-advanced-samples/reports/seo/{datetime.now().strftime('%Y-%m-%d')}/comprehensive_crawl_{timestamp}.json"
        
        # Create directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Convert to serializable format
        serializable_data = [asdict(page) for page in pages_data]
        
        # Create comprehensive output
        output_data = {
            "generated_at": datetime.now().isoformat(),
            "base_url": base_url,
            "robots_txt": crawler.robots_txt,
            "sitemap_urls": crawler.sitemap_urls,
            "url_count": len(pages_data),
            "pages": serializable_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Comprehensive crawl data saved to {output_file}")
        
        # Print summary
        print(f"\n=== COMPREHENSIVE CRAWL SUMMARY ===")
        print(f"Total pages crawled: {len(pages_data)}")
        print(f"Pages with errors: {len([p for p in pages_data if p.errors])}")
        print(f"Pages without HTTPS: {len([p for p in pages_data if not p.has_https])}")
        print(f"Pages without title: {len([p for p in pages_data if not p.title])}")
        print(f"Pages without meta description: {len([p for p in pages_data if not p.meta_description])}")
        print(f"Pages with multiple H1s: {len([p for p in pages_data if len(p.h1) > 1])}")
        print(f"Images without alt text: {sum(len(p.images_without_alt) for p in pages_data)}")
        print(f"Average load time: {sum(p.load_time for p in pages_data) / len(pages_data):.2f}s")
        print(f"Average word count: {sum(p.word_count for p in pages_data) / len(pages_data):.0f} words")

if __name__ == "__main__":
    asyncio.run(main())
