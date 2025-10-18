#!/usr/bin/env python3
"""
SEO Report Builder
Generates comprehensive SEO audit reports in markdown format
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import glob

class SEOReportBuilder:
    def __init__(self, analysis_data: Dict, crawl_data: List[Dict]):
        self.analysis_data = analysis_data
        self.crawl_data = crawl_data
        self.metrics = analysis_data['metrics']
        self.issues = analysis_data['issues']
        self.issue_summary = analysis_data['issue_summary']
        self.issues_by_category = analysis_data['issues_by_category']
    
    def generate_report(self) -> str:
        """Generate comprehensive SEO report"""
        report = []
        
        # Header
        report.append("# Comprehensive SEO Audit Report")
        report.append(f"**Website:** drsayuj.info")
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Pages Analyzed:** {self.metrics['total_pages']}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        report.append(f"This comprehensive SEO audit analyzed {self.metrics['total_pages']} pages of drsayuj.info, ")
        report.append(f"a neurosurgery practice website. The audit identified {len(self.issues)} issues across ")
        report.append("technical SEO, content quality, performance, and accessibility categories.")
        report.append("")
        
        # Overall Score
        report.append("### Overall SEO Score")
        report.append("")
        score = self.calculate_overall_score()
        report.append(f"**Overall Score: {score}/100**")
        report.append("")
        
        # Issue Summary
        report.append("### Issue Summary")
        report.append("")
        for severity in ['critical', 'high', 'medium', 'low']:
            count = self.issue_summary.get(severity, 0)
            if count > 0:
                report.append(f"- **{severity.capitalize()}:** {count} issues")
        report.append("")
        
        # Key Metrics Dashboard
        report.append("## Key Metrics Dashboard")
        report.append("")
        report.append("| Metric | Current | Target | Status |")
        report.append("|--------|---------|--------|--------|")
        
        metrics_table = [
            ("HTTPS Coverage", f"{self.metrics['https_percentage']:.1f}%", "100%", "✅" if self.metrics['https_percentage'] == 100 else "❌"),
            ("Title Tag Coverage", f"{self.metrics['title_percentage']:.1f}%", "100%", "✅" if self.metrics['title_percentage'] == 100 else "❌"),
            ("Meta Description Coverage", f"{self.metrics['meta_desc_percentage']:.1f}%", "100%", "✅" if self.metrics['meta_desc_percentage'] == 100 else "❌"),
            ("Canonical Tag Coverage", f"{self.metrics['canonical_percentage']:.1f}%", "100%", "✅" if self.metrics['canonical_percentage'] == 100 else "❌"),
            ("H1 Tag Coverage", f"{self.metrics['h1_percentage']:.1f}%", "100%", "✅" if self.metrics['h1_percentage'] == 100 else "❌"),
            ("Structured Data Coverage", f"{self.metrics['structured_data_percentage']:.1f}%", "80%", "✅" if self.metrics['structured_data_percentage'] >= 80 else "❌"),
            ("Alt Text Coverage", f"{self.metrics['alt_text_percentage']:.1f}%", "100%", "✅" if self.metrics['alt_text_percentage'] == 100 else "❌"),
            ("Average Load Time", f"{self.metrics['average_load_time']:.2f}s", "<3s", "✅" if self.metrics['average_load_time'] < 3 else "❌"),
            ("Average Word Count", f"{self.metrics['average_word_count']:.0f}", ">300", "✅" if self.metrics['average_word_count'] > 300 else "❌"),
        ]
        
        for metric, current, target, status in metrics_table:
            report.append(f"| {metric} | {current} | {target} | {status} |")
        
        report.append("")
        
        # Critical Issues
        critical_issues = [issue for issue in self.issues if issue['severity'] == 'critical']
        if critical_issues:
            report.append("## 🚨 Critical Issues")
            report.append("")
            report.append("These issues must be addressed immediately as they significantly impact SEO performance:")
            report.append("")
            
            for i, issue in enumerate(critical_issues, 1):
                report.append(f"### {i}. {issue['description']}")
                report.append("")
                report.append(f"**Category:** {issue['category'].title()}")
                report.append(f"**Affected Pages:** {len(issue['affected_pages'])}")
                report.append("")
                report.append("**Recommendation:**")
                report.append(f"{issue['recommendation']}")
                report.append("")
                if len(issue['affected_pages']) <= 5:
                    report.append("**Affected URLs:**")
                    for url in issue['affected_pages']:
                        report.append(f"- {url}")
                else:
                    report.append(f"**Affected URLs:** {len(issue['affected_pages'])} pages (see detailed report)")
                report.append("")
        
        # High Priority Issues
        high_issues = [issue for issue in self.issues if issue['severity'] == 'high']
        if high_issues:
            report.append("## ⚠️ High Priority Issues")
            report.append("")
            report.append("These issues should be addressed within the next 2 weeks:")
            report.append("")
            
            for i, issue in enumerate(high_issues, 1):
                report.append(f"### {i}. {issue['description']}")
                report.append("")
                report.append(f"**Category:** {issue['category'].title()}")
                report.append(f"**Affected Pages:** {len(issue['affected_pages'])}")
                report.append("")
                report.append("**Recommendation:**")
                report.append(f"{issue['recommendation']}")
                report.append("")
        
        # Medium Priority Issues
        medium_issues = [issue for issue in self.issues if issue['severity'] == 'medium']
        if medium_issues:
            report.append("## 📋 Medium Priority Issues")
            report.append("")
            report.append("These issues should be addressed within the next month:")
            report.append("")
            
            for i, issue in enumerate(medium_issues, 1):
                report.append(f"### {i}. {issue['description']}")
                report.append("")
                report.append(f"**Category:** {issue['category'].title()}")
                report.append(f"**Affected Pages:** {len(issue['affected_pages'])}")
                report.append("")
                report.append("**Recommendation:**")
                report.append(f"{issue['recommendation']}")
                report.append("")
        
        # Low Priority Issues
        low_issues = [issue for issue in self.issues if issue['severity'] == 'low']
        if low_issues:
            report.append("## 💡 Low Priority Issues")
            report.append("")
            report.append("These issues can be addressed when time permits:")
            report.append("")
            
            for i, issue in enumerate(low_issues, 1):
                report.append(f"### {i}. {issue['description']}")
                report.append("")
                report.append(f"**Category:** {issue['category'].title()}")
                report.append(f"**Affected Pages:** {len(issue['affected_pages'])}")
                report.append("")
                report.append("**Recommendation:**")
                report.append(f"{issue['recommendation']}")
                report.append("")
        
        # Technical SEO Analysis
        report.append("## Technical SEO Analysis")
        report.append("")
        
        # HTTPS Analysis
        report.append("### HTTPS Implementation")
        report.append("")
        if self.metrics['https_percentage'] == 100:
            report.append("✅ **Excellent:** All pages are served over HTTPS")
        else:
            report.append(f"❌ **Issue:** {100 - self.metrics['https_percentage']:.1f}% of pages are not using HTTPS")
            report.append("")
            report.append("**Impact:** Search engines prioritize HTTPS sites, and browsers show security warnings for non-HTTPS pages.")
        report.append("")
        
        # Canonical Tags
        report.append("### Canonical Tags")
        report.append("")
        if self.metrics['canonical_percentage'] == 100:
            report.append("✅ **Excellent:** All pages have canonical tags")
        else:
            report.append(f"❌ **Issue:** {100 - self.metrics['canonical_percentage']:.1f}% of pages are missing canonical tags")
            report.append("")
            report.append("**Impact:** Missing canonical tags can lead to duplicate content issues and diluted link equity.")
        report.append("")
        
        # Content Analysis
        report.append("## Content Quality Analysis")
        report.append("")
        
        # Title Tags
        report.append("### Title Tags")
        report.append("")
        if self.metrics['title_percentage'] == 100:
            report.append("✅ **Excellent:** All pages have title tags")
        else:
            report.append(f"❌ **Issue:** {100 - self.metrics['title_percentage']:.1f}% of pages are missing title tags")
            report.append("")
            report.append("**Impact:** Title tags are crucial for SEO and appear in search results. Missing titles significantly hurt rankings.")
        report.append("")
        
        # Meta Descriptions
        report.append("### Meta Descriptions")
        report.append("")
        if self.metrics['meta_desc_percentage'] == 100:
            report.append("✅ **Excellent:** All pages have meta descriptions")
        else:
            report.append(f"❌ **Issue:** {100 - self.metrics['meta_desc_percentage']:.1f}% of pages are missing meta descriptions")
            report.append("")
            report.append("**Impact:** Meta descriptions improve click-through rates from search results.")
        report.append("")
        
        # Heading Structure
        report.append("### Heading Structure")
        report.append("")
        if self.metrics['h1_percentage'] == 100:
            report.append("✅ **Excellent:** All pages have H1 tags")
        else:
            report.append(f"❌ **Issue:** {100 - self.metrics['h1_percentage']:.1f}% of pages are missing H1 tags")
            report.append("")
            report.append("**Impact:** H1 tags help search engines understand page content and improve accessibility.")
        report.append("")
        
        # Performance Analysis
        report.append("## Performance Analysis")
        report.append("")
        
        report.append("### Page Load Times")
        report.append("")
        avg_load_time = self.metrics['average_load_time']
        if avg_load_time < 2:
            report.append("✅ **Excellent:** Average load time is under 2 seconds")
        elif avg_load_time < 3:
            report.append("⚠️ **Good:** Average load time is under 3 seconds")
        else:
            report.append("❌ **Issue:** Average load time is over 3 seconds")
            report.append("")
            report.append("**Impact:** Slow loading pages hurt user experience and search rankings. Core Web Vitals are ranking factors.")
        report.append("")
        
        # Accessibility Analysis
        report.append("## Accessibility Analysis")
        report.append("")
        
        report.append("### Image Alt Text")
        report.append("")
        alt_percentage = self.metrics['alt_text_percentage']
        if alt_percentage == 100:
            report.append("✅ **Excellent:** All images have alt text")
        else:
            report.append(f"❌ **Issue:** {100 - alt_percentage:.1f}% of images are missing alt text")
            report.append("")
            report.append("**Impact:** Missing alt text hurts accessibility and prevents search engines from understanding image content.")
        report.append("")
        
        # Structured Data Analysis
        report.append("## Structured Data Analysis")
        report.append("")
        
        schema_percentage = self.metrics['structured_data_percentage']
        if schema_percentage >= 80:
            report.append("✅ **Good:** Most pages have structured data")
        elif schema_percentage >= 50:
            report.append("⚠️ **Moderate:** Some pages have structured data")
        else:
            report.append("❌ **Issue:** Most pages are missing structured data")
            report.append("")
            report.append("**Impact:** Structured data helps search engines understand content and can enable rich snippets.")
        report.append("")
        
        # Recommendations
        report.append("## Priority Recommendations")
        report.append("")
        
        # Group recommendations by impact and effort
        recommendations = self.generate_recommendations()
        
        report.append("### Immediate Actions (Next 1-2 weeks)")
        report.append("")
        for rec in recommendations['immediate']:
            report.append(f"- {rec}")
        report.append("")
        
        report.append("### Short-term Actions (Next month)")
        report.append("")
        for rec in recommendations['short_term']:
            report.append(f"- {rec}")
        report.append("")
        
        report.append("### Long-term Actions (Next quarter)")
        report.append("")
        for rec in recommendations['long_term']:
            report.append(f"- {rec}")
        report.append("")
        
        # Local SEO Recommendations
        report.append("## Local SEO Recommendations")
        report.append("")
        report.append("For a medical practice in Hyderabad, focus on:")
        report.append("")
        report.append("### Google Business Profile")
        report.append("- Verify and optimize Google Business Profile")
        report.append("- Ensure NAP (Name, Address, Phone) consistency")
        report.append("- Upload high-quality photos of the practice")
        report.append("- Encourage and respond to patient reviews")
        report.append("")
        
        report.append("### Local Content Strategy")
        report.append("- Create location-specific landing pages")
        report.append("- Target keywords like 'neurosurgeon Hyderabad', 'spine surgery near me'")
        report.append("- Include local schema markup (MedicalBusiness, LocalBusiness)")
        report.append("- Build local citations and directory listings")
        report.append("")
        
        # E-E-A-T Recommendations
        report.append("## E-E-A-T (Experience, Expertise, Authoritativeness, Trust) Recommendations")
        report.append("")
        report.append("For medical content, ensure:")
        report.append("")
        report.append("- **Experience:** Showcase Dr. Sayuj's experience and case studies")
        report.append("- **Expertise:** Include detailed medical information and procedures")
        report.append("- **Authoritativeness:** Cite medical sources and research")
        report.append("- **Trust:** Display credentials, certifications, and patient testimonials")
        report.append("")
        
        # Monitoring and Maintenance
        report.append("## Monitoring and Maintenance")
        report.append("")
        report.append("### Weekly Tasks")
        report.append("- Monitor Google Search Console for crawl errors")
        report.append("- Check for new 404 errors")
        report.append("- Review Core Web Vitals in PageSpeed Insights")
        report.append("")
        
        report.append("### Monthly Tasks")
        report.append("- Analyze organic traffic trends")
        report.append("- Review and respond to Google Business Profile reviews")
        report.append("- Update content for freshness")
        report.append("- Check for new backlink opportunities")
        report.append("")
        
        report.append("### Quarterly Tasks")
        report.append("- Comprehensive SEO audit")
        report.append("- Competitor analysis")
        report.append("- Content strategy review")
        report.append("- Technical SEO assessment")
        report.append("")
        
        return "\n".join(report)
    
    def calculate_overall_score(self) -> int:
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
    
    def generate_recommendations(self) -> Dict[str, List[str]]:
        """Generate prioritized recommendations"""
        recommendations = {
            'immediate': [],
            'short_term': [],
            'long_term': []
        }
        
        # Immediate actions based on critical issues
        critical_issues = [issue for issue in self.issues if issue['severity'] == 'critical']
        for issue in critical_issues:
            if 'HTTPS' in issue['description']:
                recommendations['immediate'].append("Implement HTTPS redirects for all pages")
            elif 'title' in issue['description'].lower():
                recommendations['immediate'].append("Add title tags to all pages")
            elif 'error' in issue['description'].lower():
                recommendations['immediate'].append("Fix broken pages and implement proper redirects")
        
        # Short-term actions based on high priority issues
        high_issues = [issue for issue in self.issues if issue['severity'] == 'high']
        for issue in high_issues:
            if 'meta description' in issue['description'].lower():
                recommendations['short_term'].append("Add meta descriptions to all pages")
            elif 'canonical' in issue['description'].lower():
                recommendations['short_term'].append("Add canonical tags to all pages")
            elif 'H1' in issue['description']:
                recommendations['short_term'].append("Add H1 tags to all pages")
        
        # Long-term actions
        recommendations['long_term'].extend([
            "Implement comprehensive structured data markup",
            "Optimize images and implement lazy loading",
            "Create location-specific landing pages",
            "Build high-quality backlinks from medical sites",
            "Develop content calendar for regular updates"
        ])
        
        return recommendations

def main():
    """Main function to generate the report"""
    import glob
    
    # Find the most recent analysis file
    analysis_files = glob.glob("/Users/dr.sayujkrishnan/Documents/openai-chatkit-advanced-samples/reports/seo/*/analysis.json")
    if not analysis_files:
        print("No analysis data found. Please run analyze_crawl.py first.")
        return
    
    latest_analysis_file = max(analysis_files, key=os.path.getctime)
    print(f"Generating report from: {latest_analysis_file}")
    
    # Load analysis data
    with open(latest_analysis_file, 'r') as f:
        analysis_data = json.load(f)
    
    # Find corresponding crawl data
    crawl_files = glob.glob("/Users/dr.sayujkrishnan/Documents/openai-chatkit-advanced-samples/reports/seo/*/raw_crawl.json")
    latest_crawl_file = max(crawl_files, key=os.path.getctime)
    
    with open(latest_crawl_file, 'r') as f:
        crawl_data = json.load(f)
    
    # Generate report
    report_builder = SEOReportBuilder(analysis_data, crawl_data)
    report = report_builder.generate_report()
    
    # Save report
    output_dir = os.path.dirname(latest_analysis_file)
    report_file = os.path.join(output_dir, f"{datetime.now().strftime('%Y-%m-%d')}.report.md")
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"SEO report saved to: {report_file}")
    
    # Print summary
    score = report_builder.calculate_overall_score()
    print(f"\nOverall SEO Score: {score}/100")
    print(f"Total Issues: {len(analysis_data['issues'])}")
    print(f"Critical Issues: {analysis_data['issue_summary'].get('critical', 0)}")
    print(f"High Priority Issues: {analysis_data['issue_summary'].get('high', 0)}")

if __name__ == "__main__":
    main()