#!/usr/bin/env python3
"""
SEO Analysis Script
Analyzes crawled data and generates comprehensive SEO insights
"""

import json
import os
from typing import List, Dict, Any
from collections import Counter, defaultdict
import re
from dataclasses import dataclass

@dataclass
class SEOIssue:
    severity: str  # critical, high, medium, low
    category: str  # technical, content, performance, accessibility
    description: str
    affected_pages: List[str]
    recommendation: str

class SEOAnalyzer:
    def __init__(self, crawl_data: List[Dict]):
        self.crawl_data = crawl_data
        self.issues: List[SEOIssue] = []
        self.metrics = {}
        
    def analyze_all(self):
        """Run all analysis functions"""
        self.analyze_technical_seo()
        self.analyze_content_quality()
        self.analyze_performance()
        self.analyze_accessibility()
        self.analyze_structured_data()
        self.calculate_metrics()
        
    def analyze_technical_seo(self):
        """Analyze technical SEO issues"""
        # HTTPS issues
        non_https_pages = [p['url'] for p in self.crawl_data if not p['has_https']]
        if non_https_pages:
            self.issues.append(SEOIssue(
                severity="critical",
                category="technical",
                description="Pages not using HTTPS",
                affected_pages=non_https_pages,
                recommendation="Implement HTTPS redirects for all pages"
            ))
        
        # Missing canonical tags
        missing_canonical = [p['url'] for p in self.crawl_data if not p['canonical_url']]
        if missing_canonical:
            self.issues.append(SEOIssue(
                severity="high",
                category="technical",
                description="Pages missing canonical tags",
                affected_pages=missing_canonical,
                recommendation="Add canonical tags to all pages to prevent duplicate content issues"
            ))
        
        # Robots noindex issues
        noindex_pages = [p['url'] for p in self.crawl_data if p['has_robots_noindex']]
        if noindex_pages:
            self.issues.append(SEOIssue(
                severity="high",
                category="technical",
                description="Pages with noindex directive",
                affected_pages=noindex_pages,
                recommendation="Review and remove noindex from pages that should be indexed"
            ))
        
        # Status code issues
        error_pages = [p['url'] for p in self.crawl_data if p['status_code'] >= 400]
        if error_pages:
            self.issues.append(SEOIssue(
                severity="critical",
                category="technical",
                description="Pages returning error status codes",
                affected_pages=error_pages,
                recommendation="Fix broken pages and implement proper redirects"
            ))
    
    def analyze_content_quality(self):
        """Analyze content quality issues"""
        # Missing titles
        missing_titles = [p['url'] for p in self.crawl_data if not p['title']]
        if missing_titles:
            self.issues.append(SEOIssue(
                severity="critical",
                category="content",
                description="Pages missing title tags",
                affected_pages=missing_titles,
                recommendation="Add unique, descriptive title tags to all pages"
            ))
        
        # Missing meta descriptions
        missing_meta_desc = [p['url'] for p in self.crawl_data if not p['meta_description']]
        if missing_meta_desc:
            self.issues.append(SEOIssue(
                severity="high",
                category="content",
                description="Pages missing meta descriptions",
                affected_pages=missing_meta_desc,
                recommendation="Add compelling meta descriptions (150-160 characters) to all pages"
            ))
        
        # Multiple H1 tags
        multiple_h1_pages = [p['url'] for p in self.crawl_data if len(p['h1_tags']) > 1]
        if multiple_h1_pages:
            self.issues.append(SEOIssue(
                severity="medium",
                category="content",
                description="Pages with multiple H1 tags",
                affected_pages=multiple_h1_pages,
                recommendation="Use only one H1 tag per page for better SEO structure"
            ))
        
        # Missing H1 tags
        missing_h1_pages = [p['url'] for p in self.crawl_data if len(p['h1_tags']) == 0]
        if missing_h1_pages:
            self.issues.append(SEOIssue(
                severity="high",
                category="content",
                description="Pages missing H1 tags",
                affected_pages=missing_h1_pages,
                recommendation="Add descriptive H1 tags to all pages"
            ))
        
        # Thin content
        thin_content_pages = [p['url'] for p in self.crawl_data if p['word_count'] < 300]
        if thin_content_pages:
            self.issues.append(SEOIssue(
                severity="medium",
                category="content",
                description="Pages with thin content (less than 300 words)",
                affected_pages=thin_content_pages,
                recommendation="Expand content to provide more value to users"
            ))
        
        # Duplicate titles
        title_counts = Counter(p['title'] for p in self.crawl_data if p['title'])
        duplicate_titles = [title for title, count in title_counts.items() if count > 1]
        if duplicate_titles:
            affected_pages = [p['url'] for p in self.crawl_data if p['title'] in duplicate_titles]
            self.issues.append(SEOIssue(
                severity="high",
                category="content",
                description="Duplicate title tags found",
                affected_pages=affected_pages,
                recommendation="Create unique title tags for each page"
            ))
    
    def analyze_performance(self):
        """Analyze performance issues"""
        # Slow loading pages
        slow_pages = [p['url'] for p in self.crawl_data if p['load_time'] > 3.0]
        if slow_pages:
            self.issues.append(SEOIssue(
                severity="medium",
                category="performance",
                description="Pages with slow load times (>3 seconds)",
                affected_pages=slow_pages,
                recommendation="Optimize images, minify CSS/JS, and implement caching"
            ))
        
        # Very slow pages
        very_slow_pages = [p['url'] for p in self.crawl_data if p['load_time'] > 5.0]
        if very_slow_pages:
            self.issues.append(SEOIssue(
                severity="high",
                category="performance",
                description="Pages with very slow load times (>5 seconds)",
                affected_pages=very_slow_pages,
                recommendation="Critical performance optimization needed"
            ))
    
    def analyze_accessibility(self):
        """Analyze accessibility issues"""
        # Images without alt text
        pages_with_images_no_alt = [p['url'] for p in self.crawl_data if p['images_without_alt']]
        if pages_with_images_no_alt:
            self.issues.append(SEOIssue(
                severity="medium",
                category="accessibility",
                description="Images missing alt text",
                affected_pages=pages_with_images_no_alt,
                recommendation="Add descriptive alt text to all images for accessibility and SEO"
            ))
    
    def analyze_structured_data(self):
        """Analyze structured data implementation"""
        # Pages without structured data
        pages_without_schema = [p['url'] for p in self.crawl_data if not p['schema_types']]
        if pages_without_schema:
            self.issues.append(SEOIssue(
                severity="low",
                category="technical",
                description="Pages without structured data",
                affected_pages=pages_without_schema,
                recommendation="Implement relevant schema markup (Person, MedicalBusiness, etc.)"
            ))
    
    def calculate_metrics(self):
        """Calculate overall SEO metrics"""
        total_pages = len(self.crawl_data)
        
        self.metrics = {
            'total_pages': total_pages,
            'pages_with_https': len([p for p in self.crawl_data if p['has_https']]),
            'pages_with_titles': len([p for p in self.crawl_data if p['title']]),
            'pages_with_meta_descriptions': len([p for p in self.crawl_data if p['meta_description']]),
            'pages_with_canonical': len([p for p in self.crawl_data if p['canonical_url']]),
            'pages_with_h1': len([p for p in self.crawl_data if p['h1_tags']]),
            'pages_with_structured_data': len([p for p in self.crawl_data if p['schema_types']]),
            'total_images': sum(len(p['images_with_alt']) + len(p['images_without_alt']) for p in self.crawl_data),
            'images_with_alt': sum(len(p['images_with_alt']) for p in self.crawl_data),
            'images_without_alt': sum(len(p['images_without_alt']) for p in self.crawl_data),
            'average_load_time': sum(p['load_time'] for p in self.crawl_data) / total_pages if total_pages > 0 else 0,
            'average_word_count': sum(p['word_count'] for p in self.crawl_data) / total_pages if total_pages > 0 else 0,
            'total_internal_links': sum(len(p['internal_links']) for p in self.crawl_data),
            'total_external_links': sum(len(p['external_links']) for p in self.crawl_data),
        }
        
        # Calculate percentages
        self.metrics['https_percentage'] = (self.metrics['pages_with_https'] / total_pages * 100) if total_pages > 0 else 0
        self.metrics['title_percentage'] = (self.metrics['pages_with_titles'] / total_pages * 100) if total_pages > 0 else 0
        self.metrics['meta_desc_percentage'] = (self.metrics['pages_with_meta_descriptions'] / total_pages * 100) if total_pages > 0 else 0
        self.metrics['canonical_percentage'] = (self.metrics['pages_with_canonical'] / total_pages * 100) if total_pages > 0 else 0
        self.metrics['h1_percentage'] = (self.metrics['pages_with_h1'] / total_pages * 100) if total_pages > 0 else 0
        self.metrics['structured_data_percentage'] = (self.metrics['pages_with_structured_data'] / total_pages * 100) if total_pages > 0 else 0
        self.metrics['alt_text_percentage'] = (self.metrics['images_with_alt'] / self.metrics['total_images'] * 100) if self.metrics['total_images'] > 0 else 0
    
    def get_issue_summary(self):
        """Get summary of issues by severity"""
        summary = defaultdict(int)
        for issue in self.issues:
            summary[issue.severity] += 1
        return dict(summary)
    
    def get_issues_by_category(self):
        """Get issues grouped by category"""
        categories = defaultdict(list)
        for issue in self.issues:
            categories[issue.category].append(issue)
        return dict(categories)

def main():
    """Main function to run the analysis"""
    import sys
    import glob
    
    # Find the most recent crawl file
    crawl_files = glob.glob("/Users/dr.sayujkrishnan/Documents/openai-chatkit-advanced-samples/reports/seo/*/raw_crawl.json")
    if not crawl_files:
        print("No crawl data found. Please run crawl_site.py first.")
        return
    
    latest_file = max(crawl_files, key=os.path.getctime)
    print(f"Analyzing crawl data from: {latest_file}")
    
    # Load crawl data
    with open(latest_file, 'r') as f:
        crawl_data = json.load(f)
    
    # Run analysis
    analyzer = SEOAnalyzer(crawl_data)
    analyzer.analyze_all()
    
    # Create output directory
    output_dir = os.path.dirname(latest_file)
    
    # Save analysis results
    analysis_file = os.path.join(output_dir, "analysis.json")
    with open(analysis_file, 'w') as f:
        json.dump({
            'metrics': analyzer.metrics,
            'issues': [{
                'severity': issue.severity,
                'category': issue.category,
                'description': issue.description,
                'affected_pages': issue.affected_pages,
                'recommendation': issue.recommendation
            } for issue in analyzer.issues],
            'issue_summary': analyzer.get_issue_summary(),
            'issues_by_category': {
                category: [{
                    'severity': issue.severity,
                    'description': issue.description,
                    'affected_pages': issue.affected_pages,
                    'recommendation': issue.recommendation
                } for issue in issues]
                for category, issues in analyzer.get_issues_by_category().items()
            }
        }, f, indent=2)
    
    print(f"Analysis saved to: {analysis_file}")
    
    # Print summary
    print(f"\n=== SEO ANALYSIS SUMMARY ===")
    print(f"Total pages analyzed: {analyzer.metrics['total_pages']}")
    print(f"Total issues found: {len(analyzer.issues)}")
    
    issue_summary = analyzer.get_issue_summary()
    for severity, count in issue_summary.items():
        print(f"{severity.capitalize()} issues: {count}")
    
    print(f"\n=== KEY METRICS ===")
    print(f"HTTPS coverage: {analyzer.metrics['https_percentage']:.1f}%")
    print(f"Title tag coverage: {analyzer.metrics['title_percentage']:.1f}%")
    print(f"Meta description coverage: {analyzer.metrics['meta_desc_percentage']:.1f}%")
    print(f"Canonical tag coverage: {analyzer.metrics['canonical_percentage']:.1f}%")
    print(f"H1 tag coverage: {analyzer.metrics['h1_percentage']:.1f}%")
    print(f"Structured data coverage: {analyzer.metrics['structured_data_percentage']:.1f}%")
    print(f"Alt text coverage: {analyzer.metrics['alt_text_percentage']:.1f}%")
    print(f"Average load time: {analyzer.metrics['average_load_time']:.2f}s")
    print(f"Average word count: {analyzer.metrics['average_word_count']:.0f} words")

if __name__ == "__main__":
    main()