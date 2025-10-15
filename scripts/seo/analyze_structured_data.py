#!/usr/bin/env python3
"""
Structured Data Analysis Script
Analyzes structured data on drsayuj.info to identify FAQPage duplicate issues
"""

import asyncio
import aiohttp
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StructuredDataIssue:
    url: str
    issue_type: str
    description: str
    severity: str
    fix_recommendation: str

class StructuredDataAnalyzer:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: aiohttp.ClientSession = None
        self.issues: List[StructuredDataIssue] = []
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_page_structured_data(self, url: str) -> Dict[str, Any]:
        """Analyze structured data on a specific page"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {"url": url, "status": response.status, "structured_data": [], "issues": []}
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract all structured data
                structured_data = []
                
                # JSON-LD structured data
                for script in soup.find_all('script', type='application/ld+json'):
                    try:
                        data = json.loads(script.string)
                        structured_data.append({
                            "type": "json-ld",
                            "data": data,
                            "source": "script tag"
                        })
                    except json.JSONDecodeError:
                        continue
                
                # Microdata
                for item in soup.find_all(attrs={'itemscope': True}):
                    microdata = self.extract_microdata(item)
                    if microdata:
                        structured_data.append({
                            "type": "microdata",
                            "data": microdata,
                            "source": "microdata attributes"
                        })
                
                # RDFa
                for item in soup.find_all(attrs={'typeof': True}):
                    rdfa = self.extract_rdfa(item)
                    if rdfa:
                        structured_data.append({
                            "type": "rdfa",
                            "data": rdfa,
                            "source": "rdfa attributes"
                        })
                
                # Analyze for issues
                issues = self.analyze_structured_data_issues(url, structured_data)
                
                return {
                    "url": url,
                    "status": response.status,
                    "structured_data": structured_data,
                    "issues": issues
                }
                
        except Exception as e:
            logger.error(f"Error analyzing {url}: {str(e)}")
            return {"url": url, "error": str(e), "structured_data": [], "issues": []}
    
    def extract_microdata(self, element) -> Dict[str, Any]:
        """Extract microdata from an element"""
        microdata = {}
        
        # Get itemtype
        itemtype = element.get('itemtype')
        if itemtype:
            microdata['@type'] = itemtype
        
        # Get properties
        properties = {}
        for prop in element.find_all(attrs={'itemprop': True}):
            prop_name = prop.get('itemprop')
            prop_value = prop.get('content') or prop.get_text(strip=True)
            if prop_name and prop_value:
                properties[prop_name] = prop_value
        
        if properties:
            microdata.update(properties)
        
        return microdata if microdata else None
    
    def extract_rdfa(self, element) -> Dict[str, Any]:
        """Extract RDFa from an element"""
        rdfa = {}
        
        # Get typeof
        typeof = element.get('typeof')
        if typeof:
            rdfa['@type'] = typeof
        
        # Get properties
        properties = {}
        for prop in element.find_all(attrs={'property': True}):
            prop_name = prop.get('property')
            prop_value = prop.get('content') or prop.get_text(strip=True)
            if prop_name and prop_value:
                properties[prop_name] = prop_value
        
        if properties:
            rdfa.update(properties)
        
        return rdfa if rdfa else None
    
    def analyze_structured_data_issues(self, url: str, structured_data: List[Dict]) -> List[Dict[str, str]]:
        """Analyze structured data for common issues"""
        issues = []
        
        # Check for duplicate FAQPage schemas
        faq_pages = []
        for item in structured_data:
            if isinstance(item['data'], dict):
                if item['data'].get('@type') == 'FAQPage':
                    faq_pages.append(item)
                elif isinstance(item['data'], list):
                    for sub_item in item['data']:
                        if isinstance(sub_item, dict) and sub_item.get('@type') == 'FAQPage':
                            faq_pages.append({'data': sub_item, 'source': item['source']})
        
        if len(faq_pages) > 1:
            issues.append({
                "type": "duplicate_faqpage",
                "severity": "critical",
                "description": f"Found {len(faq_pages)} FAQPage schemas on the same page",
                "fix": "Remove duplicate FAQPage schemas, keep only one per page"
            })
        
        # Check for invalid FAQPage structure
        for item in structured_data:
            if isinstance(item['data'], dict) and item['data'].get('@type') == 'FAQPage':
                if 'mainEntity' not in item['data']:
                    issues.append({
                        "type": "invalid_faqpage",
                        "severity": "high",
                        "description": "FAQPage schema missing required 'mainEntity' property",
                        "fix": "Add 'mainEntity' array with FAQ items"
                    })
                elif not isinstance(item['data']['mainEntity'], list):
                    issues.append({
                        "type": "invalid_faqpage",
                        "severity": "high",
                        "description": "FAQPage 'mainEntity' should be an array",
                        "fix": "Convert 'mainEntity' to an array format"
                    })
        
        # Check for duplicate schemas in general
        schema_types = {}
        for item in structured_data:
            if isinstance(item['data'], dict):
                schema_type = item['data'].get('@type')
                if schema_type:
                    if schema_type not in schema_types:
                        schema_types[schema_type] = []
                    schema_types[schema_type].append(item)
        
        for schema_type, items in schema_types.items():
            if len(items) > 1 and schema_type in ['FAQPage', 'Person', 'Organization']:
                issues.append({
                    "type": "duplicate_schema",
                    "severity": "high",
                    "description": f"Found {len(items)} {schema_type} schemas on the same page",
                    "fix": f"Remove duplicate {schema_type} schemas, keep only one per page"
                })
        
        return issues
    
    async def analyze_site_structured_data(self, urls: List[str]) -> Dict[str, Any]:
        """Analyze structured data across multiple pages"""
        results = []
        
        for url in urls:
            logger.info(f"Analyzing structured data for {url}")
            result = await self.analyze_page_structured_data(url)
            results.append(result)
        
        # Aggregate issues
        all_issues = []
        for result in results:
            if 'issues' in result:
                for issue in result['issues']:
                    all_issues.append({
                        "url": result['url'],
                        "issue_type": issue['type'],
                        "severity": issue['severity'],
                        "description": issue['description'],
                        "fix_recommendation": issue['fix']
                    })
        
        return {
            "analysis_date": "2025-10-15",
            "total_pages_analyzed": len(urls),
            "total_issues_found": len(all_issues),
            "results": results,
            "issues": all_issues
        }

async def main():
    """Main function to analyze structured data"""
    base_url = "https://www.drsayuj.info"
    
    # Key pages to analyze (focusing on pages likely to have FAQ content)
    urls_to_analyze = [
        f"{base_url}/",
        f"{base_url}/services",
        f"{base_url}/conditions",
        f"{base_url}/about",
        f"{base_url}/contact",
        f"{base_url}/services/epilepsy-surgery-hyderabad",
        f"{base_url}/services/endoscopic-discectomy-hyderabad",
        f"{base_url}/conditions/slip-disc-treatment-hyderabad",
        f"{base_url}/conditions/spinal-stenosis-treatment-hyderabad",
        f"{base_url}/conditions/sciatica-treatment-hyderabad"
    ]
    
    async with StructuredDataAnalyzer(base_url) as analyzer:
        results = await analyzer.analyze_site_structured_data(urls_to_analyze)
        
        # Save results
        timestamp = "2025-10-15_11-01-00"
        output_file = f"/Users/dr.sayujkrishnan/Documents/openai-chatkit-advanced-samples/reports/seo/{timestamp}/structured_data_analysis.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Structured data analysis saved to {output_file}")
        
        # Print summary
        print(f"\n=== STRUCTURED DATA ANALYSIS SUMMARY ===")
        print(f"Pages analyzed: {results['total_pages_analyzed']}")
        print(f"Total issues found: {results['total_issues_found']}")
        
        if results['issues']:
            print(f"\n=== ISSUES FOUND ===")
            for issue in results['issues']:
                print(f"URL: {issue['url']}")
                print(f"Type: {issue['issue_type']}")
                print(f"Severity: {issue['severity']}")
                print(f"Description: {issue['description']}")
                print(f"Fix: {issue['fix_recommendation']}")
                print("-" * 50)
        else:
            print("No structured data issues found!")

if __name__ == "__main__":
    asyncio.run(main())
