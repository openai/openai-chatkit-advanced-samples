#!/usr/bin/env python3
"""
Comprehensive SEO Analyzer
Analyzes crawled data and generates detailed SEO insights and recommendations
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from collections import Counter, defaultdict
import re
from dataclasses import dataclass

@dataclass
class SEOIssue:
    severity: str  # critical, high, medium, low
    category: str  # technical, content, performance, accessibility, structured_data
    description: str
    affected_pages: List[str]
    recommendation: str
    impact: str
    ease: str

class ComprehensiveSEOAnalyzer:
    def __init__(self, crawl_data: Dict):
        self.crawl_data = crawl_data
        self.pages = crawl_data.get('pages', [])
        self.issues: List[SEOIssue] = []
        self.metrics = {}
        self.structured_data_analysis = {}
        
    def analyze_all(self):
        """Run all analysis functions"""
        self.analyze_technical_seo()
        self.analyze_content_quality()
        self.analyze_performance()
        self.analyze_accessibility()
        self.analyze_structured_data()
        self.analyze_local_seo()
        self.calculate_metrics()
        self.generate_recommendations()
        
    def analyze_technical_seo(self):
        """Analyze technical SEO issues"""
        # HTTPS issues
        non_https_pages = [p['url'] for p in self.pages if not p['has_https']]
        if non_https_pages:
            self.issues.append(SEOIssue(
                severity="critical",
                category="technical",
                description="Pages not using HTTPS",
                affected_pages=non_https_pages,
                recommendation="Implement HTTPS redirects for all pages",
                impact="high",
                ease="medium"
            ))
        
        # Missing canonical tags
        missing_canonical = [p['url'] for p in self.pages if not p['canonical']]
        if missing_canonical:
            self.issues.append(SEOIssue(
                severity="high",
                category="technical",
                description="Pages missing canonical tags",
                affected_pages=missing_canonical,
                recommendation="Add canonical tags to all pages to prevent duplicate content issues",
                impact="high",
                ease="medium"
            ))
        
        # Canonical mismatches
        canonical_mismatches = []
        for page in self.pages:
            if page['canonical'] and page['canonical'] != page['url']:
                canonical_mismatches.append(page['url'])
        
        if canonical_mismatches:
            self.issues.append(SEOIssue(
                severity="high",
                category="technical",
                description="Pages with canonical URL mismatches",
                affected_pages=canonical_mismatches,
                recommendation="Align canonical URLs with actual page URLs",
                impact="high",
                ease="medium"
            ))
        
        # Robots noindex issues
        noindex_pages = [p['url'] for p in self.pages if 'noindex' in p['meta_robots'].lower()]
        if noindex_pages:
            self.issues.append(SEOIssue(
                severity="high",
                category="technical",
                description="Pages with noindex directive",
                affected_pages=noindex_pages,
                recommendation="Review and remove noindex from pages that should be indexed",
                impact="high",
                ease="low"
            ))
        
        # Status code issues
        error_pages = [p['url'] for p in self.pages if p['status_code'] >= 400]
        if error_pages:
            self.issues.append(SEOIssue(
                severity="critical",
                category="technical",
                description="Pages returning error status codes",
                affected_pages=error_pages,
                recommendation="Fix broken pages and implement proper redirects",
                impact="high",
                ease="medium"
            ))
    
    def analyze_content_quality(self):
        """Analyze content quality issues"""
        # Missing titles
        missing_titles = [p['url'] for p in self.pages if not p['title']]
        if missing_titles:
            self.issues.append(SEOIssue(
                severity="critical",
                category="content",
                description="Pages missing title tags",
                affected_pages=missing_titles,
                recommendation="Add unique, descriptive title tags to all pages",
                impact="high",
                ease="low"
            ))
        
        # Title length issues
        long_titles = [p['url'] for p in self.pages if len(p['title']) > 60]
        if long_titles:
            self.issues.append(SEOIssue(
                severity="medium",
                category="content",
                description="Pages with titles longer than 60 characters",
                affected_pages=long_titles,
                recommendation="Optimize titles to 50-60 characters for better search display",
                impact="medium",
                ease="medium"
            ))
        
        # Missing meta descriptions
        missing_meta_desc = [p['url'] for p in self.pages if not p['meta_description']]
        if missing_meta_desc:
            self.issues.append(SEOIssue(
                severity="high",
                category="content",
                description="Pages missing meta descriptions",
                affected_pages=missing_meta_desc,
                recommendation="Add compelling meta descriptions (150-160 characters) to all pages",
                impact="high",
                ease="medium"
            ))
        
        # Meta description length issues
        long_meta_desc = [p['url'] for p in self.pages if len(p['meta_description']) > 160]
        if long_meta_desc:
            self.issues.append(SEOIssue(
                severity="medium",
                category="content",
                description="Pages with meta descriptions longer than 160 characters",
                affected_pages=long_meta_desc,
                recommendation="Optimize meta descriptions to 150-160 characters",
                impact="medium",
                ease="medium"
            ))
        
        # Multiple H1 tags
        multiple_h1_pages = [p['url'] for p in self.pages if len(p['h1']) > 1]
        if multiple_h1_pages:
            self.issues.append(SEOIssue(
                severity="medium",
                category="content",
                description="Pages with multiple H1 tags",
                affected_pages=multiple_h1_pages,
                recommendation="Use only one H1 tag per page for better SEO structure",
                impact="medium",
                ease="medium"
            ))
        
        # Missing H1 tags
        missing_h1_pages = [p['url'] for p in self.pages if len(p['h1']) == 0]
        if missing_h1_pages:
            self.issues.append(SEOIssue(
                severity="high",
                category="content",
                description="Pages missing H1 tags",
                affected_pages=missing_h1_pages,
                recommendation="Add descriptive H1 tags to all pages",
                impact="high",
                ease="medium"
            ))
        
        # Thin content
        thin_content_pages = [p['url'] for p in self.pages if p['word_count'] < 300]
        if thin_content_pages:
            self.issues.append(SEOIssue(
                severity="medium",
                category="content",
                description="Pages with thin content (less than 300 words)",
                affected_pages=thin_content_pages,
                recommendation="Expand content to provide more value to users",
                impact="medium",
                ease="high"
            ))
        
        # Duplicate titles
        title_counts = Counter(p['title'] for p in self.pages if p['title'])
        duplicate_titles = [title for title, count in title_counts.items() if count > 1]
        if duplicate_titles:
            affected_pages = [p['url'] for p in self.pages if p['title'] in duplicate_titles]
            self.issues.append(SEOIssue(
                severity="high",
                category="content",
                description="Duplicate title tags found",
                affected_pages=affected_pages,
                recommendation="Create unique title tags for each page",
                impact="high",
                ease="medium"
            ))
    
    def analyze_performance(self):
        """Analyze performance issues"""
        # Slow loading pages
        slow_pages = [p['url'] for p in self.pages if p['load_time'] > 3.0]
        if slow_pages:
            self.issues.append(SEOIssue(
                severity="medium",
                category="performance",
                description="Pages with slow load times (>3 seconds)",
                affected_pages=slow_pages,
                recommendation="Optimize images, minify CSS/JS, and implement caching",
                impact="medium",
                ease="medium"
            ))
        
        # Very slow pages
        very_slow_pages = [p['url'] for p in self.pages if p['load_time'] > 5.0]
        if very_slow_pages:
            self.issues.append(SEOIssue(
                severity="high",
                category="performance",
                description="Pages with very slow load times (>5 seconds)",
                affected_pages=very_slow_pages,
                recommendation="Critical performance optimization needed",
                impact="high",
                ease="medium"
            ))
    
    def analyze_accessibility(self):
        """Analyze accessibility issues"""
        # Images without alt text
        pages_with_images_no_alt = [p['url'] for p in self.pages if p['images_without_alt']]
        if pages_with_images_no_alt:
            self.issues.append(SEOIssue(
                severity="medium",
                category="accessibility",
                description="Images missing alt text",
                affected_pages=pages_with_images_no_alt,
                recommendation="Add descriptive alt text to all images for accessibility and SEO",
                impact="medium",
                ease="medium"
            ))
    
    def analyze_structured_data(self):
        """Analyze structured data implementation"""
        # Collect all structured data types
        all_schema_types = []
        for page in self.pages:
            for item in page['structured_data']:
                if isinstance(item, dict) and '@type' in item:
                    schema_type = item['@type']
                    if isinstance(schema_type, list):
                        all_schema_types.extend(schema_type)
                    else:
                        all_schema_types.append(schema_type)
        
        schema_counts = Counter(all_schema_types)
        self.structured_data_analysis = {
            'total_schemas': len(all_schema_types),
            'unique_schema_types': len(schema_counts),
            'schema_distribution': dict(schema_counts)
        }
        
        # Check for duplicate FAQPage schemas
        faq_pages = []
        for page in self.pages:
            faq_count = 0
            for item in page['structured_data']:
                if isinstance(item, dict) and item.get('@type') == 'FAQPage':
                    faq_count += 1
            if faq_count > 1:
                faq_pages.append(page['url'])
        
        if faq_pages:
            self.issues.append(SEOIssue(
                severity="critical",
                category="structured_data",
                description="Pages with duplicate FAQPage schemas",
                affected_pages=faq_pages,
                recommendation="Consolidate duplicate FAQPage schemas into single schema per page",
                impact="high",
                ease="medium"
            ))
        
        # Pages without structured data
        pages_without_schema = [p['url'] for p in self.pages if not p['structured_data']]
        if pages_without_schema:
            self.issues.append(SEOIssue(
                severity="low",
                category="structured_data",
                description="Pages without structured data",
                affected_pages=pages_without_schema,
                recommendation="Implement relevant schema markup (Person, MedicalBusiness, etc.)",
                impact="low",
                ease="medium"
            ))
    
    def analyze_local_seo(self):
        """Analyze local SEO elements"""
        # Check for local business schema
        local_business_pages = []
        for page in self.pages:
            for item in page['structured_data']:
                if isinstance(item, dict) and item.get('@type') in ['LocalBusiness', 'MedicalBusiness', 'Hospital']:
                    local_business_pages.append(page['url'])
                    break
        
        if not local_business_pages:
            self.issues.append(SEOIssue(
                severity="medium",
                category="local_seo",
                description="No local business schema markup found",
                affected_pages=["Homepage and key service pages"],
                recommendation="Implement LocalBusiness or MedicalBusiness schema markup",
                impact="medium",
                ease="medium"
            ))
    
    def calculate_metrics(self):
        """Calculate overall SEO metrics"""
        total_pages = len(self.pages)
        
        self.metrics = {
            'total_pages': total_pages,
            'pages_with_https': len([p for p in self.pages if p['has_https']]),
            'pages_with_titles': len([p for p in self.pages if p['title']]),
            'pages_with_meta_descriptions': len([p for p in self.pages if p['meta_description']]),
            'pages_with_canonical': len([p for p in self.pages if p['canonical']]),
            'pages_with_h1': len([p for p in self.pages if p['h1']]),
            'pages_with_structured_data': len([p for p in self.pages if p['structured_data']]),
            'total_images': sum(len(p['images_with_alt']) + len(p['images_without_alt']) for p in self.pages),
            'images_with_alt': sum(len(p['images_with_alt']) for p in self.pages),
            'images_without_alt': sum(len(p['images_without_alt']) for p in self.pages),
            'average_load_time': sum(p['load_time'] for p in self.pages) / total_pages if total_pages > 0 else 0,
            'average_word_count': sum(p['word_count'] for p in self.pages) / total_pages if total_pages > 0 else 0,
            'total_internal_links': sum(len(p['internal_links']) for p in self.pages),
            'total_external_links': sum(len(p['external_links']) for p in self.pages),
        }
        
        # Calculate percentages
        self.metrics['https_percentage'] = (self.metrics['pages_with_https'] / total_pages * 100) if total_pages > 0 else 0
        self.metrics['title_percentage'] = (self.metrics['pages_with_titles'] / total_pages * 100) if total_pages > 0 else 0
        self.metrics['meta_desc_percentage'] = (self.metrics['pages_with_meta_descriptions'] / total_pages * 100) if total_pages > 0 else 0
        self.metrics['canonical_percentage'] = (self.metrics['pages_with_canonical'] / total_pages * 100) if total_pages > 0 else 0
        self.metrics['h1_percentage'] = (self.metrics['pages_with_h1'] / total_pages * 100) if total_pages > 0 else 0
        self.metrics['structured_data_percentage'] = (self.metrics['pages_with_structured_data'] / total_pages * 100) if total_pages > 0 else 0
        self.metrics['alt_text_percentage'] = (self.metrics['images_with_alt'] / self.metrics['total_images'] * 100) if self.metrics['total_images'] > 0 else 0
    
    def generate_recommendations(self):
        """Generate prioritized recommendations"""
        # Group issues by impact and ease
        high_impact_easy = [issue for issue in self.issues if issue.impact == "high" and issue.ease == "low"]
        high_impact_medium = [issue for issue in self.issues if issue.impact == "high" and issue.ease == "medium"]
        medium_impact_easy = [issue for issue in self.issues if issue.impact == "medium" and issue.ease == "low"]
        
        self.recommendations = {
            'immediate_actions': high_impact_easy,
            'short_term_actions': high_impact_medium,
            'medium_term_actions': medium_impact_easy,
            'all_issues': self.issues
        }
    
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
    
    def calculate_seo_score(self) -> int:
        """Calculate overall SEO score out of 100"""
        score = 0
        max_score = 100
        
        # Technical SEO (30 points)
        score += (self.metrics['https_percentage'] / 100) * 10
        score += (self.metrics['canonical_percentage'] / 100) * 10
        score += (self.metrics['structured_data_percentage'] / 100) * 10
        
        # Content Quality (40 points)
        score += (self.metrics['title_percentage'] / 100) * 10
        score += (self.metrics['meta_desc_percentage'] / 100) * 10
        score += (self.metrics['h1_percentage'] / 100) * 10
        score += min(self.metrics['average_word_count'] / 300, 1) * 10
        
        # Performance (20 points)
        if self.metrics['average_load_time'] < 2:
            score += 20
        elif self.metrics['average_load_time'] < 3:
            score += 15
        elif self.metrics['average_load_time'] < 5:
            score += 10
        else:
            score += 5
        
        # Accessibility (10 points)
        score += (self.metrics['alt_text_percentage'] / 100) * 10
        
        return int(score)

def main():
    """Main function to run the comprehensive analysis"""
    import glob
    
    # Find the most recent comprehensive crawl file
    crawl_files = glob.glob("/Users/dr.sayujkrishnan/Documents/openai-chatkit-advanced-samples/reports/seo/*/comprehensive_crawl_*.json")
    if not crawl_files:
        print("No comprehensive crawl data found. Please run comprehensive_crawler.py first.")
        return
    
    latest_file = max(crawl_files, key=os.path.getctime)
    print(f"Analyzing comprehensive crawl data from: {latest_file}")
    
    # Load crawl data
    with open(latest_file, 'r') as f:
        crawl_data = json.load(f)
    
    # Run analysis
    analyzer = ComprehensiveSEOAnalyzer(crawl_data)
    analyzer.analyze_all()
    
    # Create output directory
    output_dir = os.path.dirname(latest_file)
    
    # Save analysis results
    analysis_file = os.path.join(output_dir, "comprehensive_analysis.json")
    with open(analysis_file, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'base_url': crawl_data['base_url'],
            'page_total': len(crawl_data['pages']),
            'seo_score': analyzer.calculate_seo_score(),
            'metrics': analyzer.metrics,
            'structured_data_analysis': analyzer.structured_data_analysis,
            'issues': [{
                'severity': issue.severity,
                'category': issue.category,
                'description': issue.description,
                'affected_pages': issue.affected_pages,
                'recommendation': issue.recommendation,
                'impact': issue.impact,
                'ease': issue.ease
            } for issue in analyzer.issues],
            'recommendations': {
                'immediate_actions': [{
                    'description': issue.description,
                    'affected_pages': issue.affected_pages,
                    'recommendation': issue.recommendation
                } for issue in analyzer.recommendations['immediate_actions']],
                'short_term_actions': [{
                    'description': issue.description,
                    'affected_pages': issue.affected_pages,
                    'recommendation': issue.recommendation
                } for issue in analyzer.recommendations['short_term_actions']],
                'medium_term_actions': [{
                    'description': issue.description,
                    'affected_pages': issue.affected_pages,
                    'recommendation': issue.recommendation
                } for issue in analyzer.recommendations['medium_term_actions']]
            },
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
    
    print(f"Comprehensive analysis saved to: {analysis_file}")
    
    # Print summary
    print(f"\n=== COMPREHENSIVE SEO ANALYSIS SUMMARY ===")
    print(f"Total pages analyzed: {analyzer.metrics['total_pages']}")
    print(f"Overall SEO Score: {analyzer.calculate_seo_score()}/100")
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
