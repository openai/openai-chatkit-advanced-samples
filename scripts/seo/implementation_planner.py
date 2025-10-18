#!/usr/bin/env python3
"""
SEO Implementation Planner
Creates detailed implementation plans for identified SEO issues
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class SEOImplementationPlanner:
    def __init__(self, analysis_data: Dict):
        self.analysis_data = analysis_data
        self.issues = analysis_data.get('issues', [])
        self.metrics = analysis_data.get('metrics', {})
        
    def create_implementation_plan(self) -> Dict[str, Any]:
        """Create comprehensive implementation plan"""
        
        # Group issues by priority
        critical_issues = [i for i in self.issues if i['severity'] == 'critical']
        high_issues = [i for i in self.issues if i['severity'] == 'high']
        medium_issues = [i for i in self.issues if i['severity'] == 'medium']
        low_issues = [i for i in self.issues if i['severity'] == 'low']
        
        return {
            'generated_at': datetime.now().isoformat(),
            'base_url': self.analysis_data.get('base_url', ''),
            'seo_score': self.analysis_data.get('seo_score', 0),
            'total_issues': len(self.issues),
            'implementation_phases': {
                'phase_1_critical': {
                    'timeline': '0-1 weeks',
                    'priority': 'Critical',
                    'issues': critical_issues,
                    'actions': self._create_phase_actions(critical_issues, 'critical')
                },
                'phase_2_high': {
                    'timeline': '1-2 weeks',
                    'priority': 'High',
                    'issues': high_issues,
                    'actions': self._create_phase_actions(high_issues, 'high')
                },
                'phase_3_medium': {
                    'timeline': '2-4 weeks',
                    'priority': 'Medium',
                    'issues': medium_issues,
                    'actions': self._create_phase_actions(medium_issues, 'medium')
                },
                'phase_4_low': {
                    'timeline': '1-3 months',
                    'priority': 'Low',
                    'issues': low_issues,
                    'actions': self._create_phase_actions(low_issues, 'low')
                }
            },
            'technical_requirements': self._create_technical_requirements(),
            'content_requirements': self._create_content_requirements(),
            'monitoring_plan': self._create_monitoring_plan(),
            'success_metrics': self._create_success_metrics()
        }
    
    def _create_phase_actions(self, issues: List[Dict], priority: str) -> List[Dict]:
        """Create specific actions for a phase"""
        actions = []
        
        for issue in issues:
            action = {
                'issue_description': issue['description'],
                'category': issue['category'],
                'affected_pages_count': len(issue.get('affected_pages', [])),
                'recommendation': issue['recommendation'],
                'implementation_steps': self._get_implementation_steps(issue),
                'estimated_effort': self._estimate_effort(issue),
                'tools_needed': self._get_tools_needed(issue),
                'validation_method': self._get_validation_method(issue)
            }
            actions.append(action)
        
        return actions
    
    def _get_implementation_steps(self, issue: Dict) -> List[str]:
        """Get specific implementation steps for an issue"""
        category = issue['category']
        description = issue['description']
        
        if 'canonical' in description.lower():
            return [
                "1. Review current canonical tag implementation",
                "2. Identify pages with mismatched canonical URLs",
                "3. Update canonical tags to match actual page URLs",
                "4. Test canonical tag functionality",
                "5. Verify in Google Search Console"
            ]
        elif 'noindex' in description.lower():
            return [
                "1. Identify pages with noindex directives",
                "2. Review business requirements for each page",
                "3. Remove noindex from pages that should be indexed",
                "4. Update robots meta tags",
                "5. Request re-indexing in Search Console"
            ]
        elif 'title' in description.lower() and 'longer' in description.lower():
            return [
                "1. Audit current title tag lengths",
                "2. Identify titles over 60 characters",
                "3. Rewrite titles to 50-60 characters",
                "4. Ensure keywords are front-loaded",
                "5. Maintain uniqueness across all pages"
            ]
        elif 'meta description' in description.lower():
            return [
                "1. Audit current meta description lengths",
                "2. Identify descriptions over 160 characters",
                "3. Rewrite descriptions to 150-160 characters",
                "4. Include compelling CTAs",
                "5. Ensure uniqueness across all pages"
            ]
        elif 'thin content' in description.lower():
            return [
                "1. Identify pages with less than 300 words",
                "2. Analyze content gaps and user intent",
                "3. Create content expansion plan",
                "4. Add valuable, relevant content",
                "5. Maintain E-E-A-T principles"
            ]
        elif 'duplicate title' in description.lower():
            return [
                "1. Identify all duplicate title tags",
                "2. Create unique titles for each page",
                "3. Ensure titles reflect page content",
                "4. Include relevant keywords",
                "5. Test title uniqueness"
            ]
        elif 'faqpage' in description.lower():
            return [
                "1. Identify pages with duplicate FAQPage schemas",
                "2. Consolidate FAQ content into single schema",
                "3. Remove duplicate schema markup",
                "4. Validate with Google Rich Results Test",
                "5. Monitor Search Console for resolution"
            ]
        else:
            return [
                "1. Analyze the specific issue",
                "2. Create implementation plan",
                "3. Execute changes",
                "4. Test and validate",
                "5. Monitor results"
            ]
    
    def _estimate_effort(self, issue: Dict) -> str:
        """Estimate implementation effort"""
        category = issue['category']
        affected_count = len(issue.get('affected_pages', []))
        
        if category == 'technical':
            if affected_count > 20:
                return "High (2-3 days)"
            elif affected_count > 10:
                return "Medium (1-2 days)"
            else:
                return "Low (4-8 hours)"
        elif category == 'content':
            if affected_count > 20:
                return "High (3-5 days)"
            elif affected_count > 10:
                return "Medium (2-3 days)"
            else:
                return "Low (1-2 days)"
        else:
            return "Medium (1-2 days)"
    
    def _get_tools_needed(self, issue: Dict) -> List[str]:
        """Get tools needed for implementation"""
        category = issue['category']
        
        base_tools = ["Google Search Console", "Browser Developer Tools"]
        
        if category == 'technical':
            return base_tools + ["Schema Validator", "Rich Results Test"]
        elif category == 'content':
            return base_tools + ["Content Management System", "SEO Analysis Tools"]
        elif category == 'structured_data':
            return base_tools + ["Schema Validator", "Rich Results Test", "JSON-LD Validator"]
        else:
            return base_tools
    
    def _get_validation_method(self, issue: Dict) -> str:
        """Get validation method for an issue"""
        category = issue['category']
        
        if category == 'technical':
            return "Google Search Console monitoring and manual testing"
        elif category == 'content':
            return "Content audit and search result preview testing"
        elif category == 'structured_data':
            return "Google Rich Results Test and Search Console validation"
        else:
            return "Manual testing and monitoring"
    
    def _create_technical_requirements(self) -> Dict[str, Any]:
        """Create technical requirements section"""
        return {
            'server_requirements': [
                "HTTPS certificate validation",
                "Canonical URL configuration",
                "Meta robots tag implementation",
                "Structured data markup validation"
            ],
            'cms_requirements': [
                "Title tag optimization capabilities",
                "Meta description management",
                "Canonical URL configuration",
                "Schema markup implementation"
            ],
            'development_requirements': [
                "Access to site templates",
                "Content management system access",
                "Testing environment setup",
                "Deployment pipeline access"
            ]
        }
    
    def _create_content_requirements(self) -> Dict[str, Any]:
        """Create content requirements section"""
        return {
            'content_audit': [
                "Review all page titles for length and uniqueness",
                "Audit meta descriptions for length and quality",
                "Analyze content depth and value",
                "Check for duplicate content issues"
            ],
            'content_creation': [
                "Expand thin content pages",
                "Create unique, compelling titles",
                "Write engaging meta descriptions",
                "Ensure E-E-A-T compliance"
            ],
            'content_optimization': [
                "Front-load keywords in titles",
                "Include CTAs in meta descriptions",
                "Maintain consistent brand voice",
                "Optimize for featured snippets"
            ]
        }
    
    def _create_monitoring_plan(self) -> Dict[str, Any]:
        """Create monitoring plan"""
        return {
            'immediate_monitoring': [
                "Google Search Console error tracking",
                "Page speed and Core Web Vitals monitoring",
                "Indexing status verification",
                "Structured data validation"
            ],
            'weekly_monitoring': [
                "Keyword ranking tracking",
                "Organic traffic analysis",
                "Backlink profile monitoring",
                "Competitor analysis"
            ],
            'monthly_monitoring': [
                "Comprehensive SEO audit",
                "Content performance analysis",
                "Technical SEO assessment",
                "Local SEO metrics review"
            ],
            'tools_required': [
                "Google Search Console",
                "Google Analytics",
                "PageSpeed Insights",
                "Rich Results Test",
                "Schema Validator"
            ]
        }
    
    def _create_success_metrics(self) -> Dict[str, Any]:
        """Create success metrics"""
        return {
            'technical_metrics': [
                "SEO score improvement",
                "Page speed optimization",
                "Error rate reduction",
                "Indexing coverage increase"
            ],
            'content_metrics': [
                "Title tag optimization completion",
                "Meta description improvement",
                "Content depth enhancement",
                "Duplicate content elimination"
            ],
            'performance_metrics': [
                "Organic traffic growth",
                "Keyword ranking improvements",
                "Click-through rate enhancement",
                "Conversion rate optimization"
            ],
            'target_improvements': {
                'seo_score': f"Maintain {self.analysis_data.get('seo_score', 0)}/100 or improve",
                'page_speed': "Maintain <2s load time",
                'indexing': "100% of important pages indexed",
                'errors': "Zero critical SEO errors"
            }
        }

def main():
    """Main function to create implementation plan"""
    import glob
    
    # Find the most recent comprehensive analysis file
    analysis_files = glob.glob("/Users/dr.sayujkrishnan/Documents/openai-chatkit-advanced-samples/reports/seo/*/comprehensive_analysis.json")
    if not analysis_files:
        print("No comprehensive analysis data found. Please run comprehensive_analyzer.py first.")
        return
    
    latest_file = max(analysis_files, key=os.path.getctime)
    print(f"Creating implementation plan from: {latest_file}")
    
    # Load analysis data
    with open(latest_file, 'r') as f:
        analysis_data = json.load(f)
    
    # Create implementation plan
    planner = SEOImplementationPlanner(analysis_data)
    implementation_plan = planner.create_implementation_plan()
    
    # Save implementation plan
    output_dir = os.path.dirname(latest_file)
    plan_file = os.path.join(output_dir, f"implementation_plan_{datetime.now().strftime('%Y-%m-%d')}.json")
    
    with open(plan_file, 'w') as f:
        json.dump(implementation_plan, f, indent=2)
    
    print(f"Implementation plan saved to: {plan_file}")
    
    # Print summary
    print(f"\n=== IMPLEMENTATION PLAN SUMMARY ===")
    print(f"Total Issues: {implementation_plan['total_issues']}")
    print(f"Critical Issues: {len(implementation_plan['implementation_phases']['phase_1_critical']['issues'])}")
    print(f"High Priority Issues: {len(implementation_plan['implementation_phases']['phase_2_high']['issues'])}")
    print(f"Medium Priority Issues: {len(implementation_plan['implementation_phases']['phase_3_medium']['issues'])}")
    print(f"Low Priority Issues: {len(implementation_plan['implementation_phases']['phase_4_low']['issues'])}")
    
    # Print immediate actions
    critical_actions = implementation_plan['implementation_phases']['phase_1_critical']['actions']
    if critical_actions:
        print(f"\n=== IMMEDIATE ACTIONS (0-1 weeks) ===")
        for action in critical_actions:
            print(f"- {action['issue_description']} ({action['affected_pages_count']} pages)")
            print(f"  Effort: {action['estimated_effort']}")
    else:
        print(f"\n=== IMMEDIATE ACTIONS ===")
        print("No critical issues requiring immediate action! 🎉")

if __name__ == "__main__":
    main()
