#!/usr/bin/env python3
"""
SEO Issues Troubleshooting Script
Fixes all identified SEO issues from the audit
"""

import json
import os
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class SEOFix:
    issue_type: str
    description: str
    affected_urls: List[str]
    fix_action: str
    priority: str

class SEOTroubleshooter:
    def __init__(self, analysis_file: str):
        with open(analysis_file, 'r') as f:
            self.analysis_data = json.load(f)
        self.fixes = []
        
    def analyze_issues(self):
        """Analyze all issues and create fix recommendations"""
        
        # Critical Issue: Broken epilepsy surgery page
        epilepsy_404_url = "https://www.drsayuj.info/services/epilepsy-surgery"
        epilepsy_working_url = "https://www.drsayuj.info/services/epilepsy-surgery-hyderabad"
        
        self.fixes.append(SEOFix(
            issue_type="redirect",
            description="Broken epilepsy surgery page needs redirect",
            affected_urls=[epilepsy_404_url],
            fix_action=f"Create 301 redirect from {epilepsy_404_url} to {epilepsy_working_url}",
            priority="critical"
        ))
        
        # High Priority: Duplicate title tags
        duplicate_pages = self.analysis_data['issues'][3]['affected_pages']  # Duplicate title issue
        
        # Group pages by likely title patterns
        title_groups = self._group_duplicate_titles(duplicate_pages)
        
        for group_name, urls in title_groups.items():
            self.fixes.append(SEOFix(
                issue_type="title_optimization",
                description=f"Duplicate title tags in {group_name} group",
                affected_urls=urls,
                fix_action=f"Create unique, descriptive title tags for each page in {group_name}",
                priority="high"
            ))
        
        # Medium Priority: Thin content
        thin_content_pages = self.analysis_data['issues'][2]['affected_pages']  # Thin content issue
        
        self.fixes.append(SEOFix(
            issue_type="content_expansion",
            description="Pages with thin content (less than 300 words)",
            affected_urls=thin_content_pages,
            fix_action="Expand content to provide more value to users",
            priority="medium"
        ))
        
        # High Priority: Noindex directive (same as broken page)
        self.fixes.append(SEOFix(
            issue_type="noindex_removal",
            description="Page with noindex directive preventing indexing",
            affected_urls=[epilepsy_404_url],
            fix_action="Remove noindex directive (will be resolved by redirect)",
            priority="high"
        ))
    
    def _group_duplicate_titles(self, pages: List[str]) -> Dict[str, List[str]]:
        """Group pages by likely title patterns"""
        groups = {
            "homepage_duplicates": [],
            "appointments_duplicates": [],
            "services_duplicates": [],
            "conditions_duplicates": [],
            "trailing_slash_duplicates": []
        }
        
        for page in pages:
            if page in ["https://www.drsayuj.info", "https://www.drsayuj.info/"]:
                groups["homepage_duplicates"].append(page)
            elif "appointments" in page:
                groups["appointments_duplicates"].append(page)
            elif "services" in page:
                groups["services_duplicates"].append(page)
            elif "conditions" in page:
                groups["conditions_duplicates"].append(page)
            elif page.endswith("/"):
                groups["trailing_slash_duplicates"].append(page)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def generate_fix_recommendations(self) -> Dict[str, Any]:
        """Generate detailed fix recommendations"""
        recommendations = {
            "critical_fixes": [],
            "high_priority_fixes": [],
            "medium_priority_fixes": [],
            "implementation_plan": {
                "phase_1": [],
                "phase_2": [],
                "phase_3": []
            }
        }
        
        for fix in self.fixes:
            fix_dict = {
                "type": fix.issue_type,
                "description": fix.description,
                "affected_urls": fix.affected_urls,
                "action": fix.fix_action,
                "priority": fix.priority
            }
            
            if fix.priority == "critical":
                recommendations["critical_fixes"].append(fix_dict)
                recommendations["implementation_plan"]["phase_1"].append(fix_dict)
            elif fix.priority == "high":
                recommendations["high_priority_fixes"].append(fix_dict)
                recommendations["implementation_plan"]["phase_2"].append(fix_dict)
            elif fix.priority == "medium":
                recommendations["medium_priority_fixes"].append(fix_dict)
                recommendations["implementation_plan"]["phase_3"].append(fix_dict)
        
        return recommendations
    
    def create_redirect_rules(self) -> List[Dict[str, str]]:
        """Create redirect rules for broken pages"""
        redirects = [
            {
                "from": "https://www.drsayuj.info/services/epilepsy-surgery",
                "to": "https://www.drsayuj.info/services/epilepsy-surgery-hyderabad",
                "type": "301",
                "reason": "Fix broken epilepsy surgery page"
            }
        ]
        
        # Add trailing slash redirects
        trailing_slash_pages = [
            "https://www.drsayuj.info/appointments/",
            "https://www.drsayuj.info/services/minimally-invasive-spine-surgery/",
            "https://www.drsayuj.info/conditions/spinal-stenosis-treatment-hyderabad/",
            "https://www.drsayuj.info/conditions/slip-disc-treatment-hyderabad/",
            "https://www.drsayuj.info/services/endoscopic-discectomy-hyderabad/",
            "https://www.drsayuj.info/conditions/sciatica-treatment-hyderabad/"
        ]
        
        for page in trailing_slash_pages:
            redirects.append({
                "from": page,
                "to": page.rstrip("/"),
                "type": "301",
                "reason": "Remove trailing slash for consistency"
            })
        
        return redirects
    
    def create_title_suggestions(self) -> Dict[str, str]:
        """Create unique title suggestions for duplicate pages"""
        title_suggestions = {
            # Homepage variations
            "https://www.drsayuj.info": "Dr. Sayuj Krishnan | Best Neurosurgeon in Hyderabad | Brain & Spine Surgery",
            "https://www.drsayuj.info/": "Dr. Sayuj Krishnan | Best Neurosurgeon in Hyderabad | Brain & Spine Surgery",
            
            # Appointments
            "https://www.drsayuj.info/appointments": "Book Appointment | Dr. Sayuj Krishnan | Neurosurgeon Hyderabad",
            "https://www.drsayuj.info/appointments/": "Book Appointment | Dr. Sayuj Krishnan | Neurosurgeon Hyderabad",
            
            # Services
            "https://www.drsayuj.info/services/minimally-invasive-spine-surgery": "Minimally Invasive Spine Surgery | Dr. Sayuj Krishnan | Hyderabad",
            "https://www.drsayuj.info/services/minimally-invasive-spine-surgery/": "Minimally Invasive Spine Surgery | Dr. Sayuj Krishnan | Hyderabad",
            "https://www.drsayuj.info/services/endoscopic-discectomy-hyderabad": "Endoscopic Discectomy Surgery | Dr. Sayuj Krishnan | Hyderabad",
            "https://www.drsayuj.info/services/endoscopic-discectomy-hyderabad/": "Endoscopic Discectomy Surgery | Dr. Sayuj Krishnan | Hyderabad",
            "https://www.drsayuj.info/services/microvascular-decompression": "Microvascular Decompression Surgery | Dr. Sayuj Krishnan | Hyderabad",
            "https://www.drsayuj.info/services/radiosurgery-gamma-knife": "Gamma Knife Radiosurgery | Dr. Sayuj Krishnan | Hyderabad",
            
            # Conditions
            "https://www.drsayuj.info/conditions/slip-disc-treatment-hyderabad": "Slip Disc Treatment | Dr. Sayuj Krishnan | Neurosurgeon Hyderabad",
            "https://www.drsayuj.info/conditions/slip-disc-treatment-hyderabad/": "Slip Disc Treatment | Dr. Sayuj Krishnan | Neurosurgeon Hyderabad",
            "https://www.drsayuj.info/conditions/spinal-stenosis-treatment-hyderabad": "Spinal Stenosis Treatment | Dr. Sayuj Krishnan | Neurosurgeon Hyderabad",
            "https://www.drsayuj.info/conditions/spinal-stenosis-treatment-hyderabad/": "Spinal Stenosis Treatment | Dr. Sayuj Krishnan | Neurosurgeon Hyderabad",
            "https://www.drsayuj.info/conditions/sciatica-treatment-hyderabad": "Sciatica Treatment | Dr. Sayuj Krishnan | Neurosurgeon Hyderabad",
            "https://www.drsayuj.info/conditions/sciatica-treatment-hyderabad/": "Sciatica Treatment | Dr. Sayuj Krishnan | Neurosurgeon Hyderabad",
            "https://www.drsayuj.info/conditions/trigeminal-neuralgia-treatment-hyderabad": "Trigeminal Neuralgia Treatment | Dr. Sayuj Krishnan | Neurosurgeon Hyderabad",
            "https://www.drsayuj.info/conditions/trigeminal-neuralgia-treatment": "Trigeminal Neuralgia Treatment | Dr. Sayuj Krishnan | Neurosurgeon Hyderabad",
        }
        
        return title_suggestions
    
    def create_content_expansion_plan(self) -> Dict[str, Dict[str, Any]]:
        """Create content expansion plan for thin content pages"""
        expansion_plan = {
            "https://www.drsayuj.info/conditions": {
                "current_word_count": "~200",
                "target_word_count": "500+",
                "suggested_additions": [
                    "Detailed explanation of common neurological conditions",
                    "Symptoms and warning signs",
                    "Diagnostic procedures",
                    "Treatment options and approaches",
                    "Prevention strategies",
                    "When to seek medical help"
                ]
            },
            "https://www.drsayuj.info/conditions/spinal-stenosis-treatment-hyderabad": {
                "current_word_count": "~250",
                "target_word_count": "600+",
                "suggested_additions": [
                    "Detailed explanation of spinal stenosis",
                    "Causes and risk factors",
                    "Symptoms progression",
                    "Diagnostic imaging details",
                    "Conservative treatment options",
                    "Surgical treatment details",
                    "Recovery timeline",
                    "Prevention strategies"
                ]
            },
            "https://www.drsayuj.info/conditions/sciatica-treatment-hyderabad": {
                "current_word_count": "~250",
                "target_word_count": "600+",
                "suggested_additions": [
                    "Comprehensive sciatica overview",
                    "Anatomy of sciatic nerve",
                    "Common causes and triggers",
                    "Symptoms and pain patterns",
                    "Diagnostic procedures",
                    "Treatment options (conservative and surgical)",
                    "Physical therapy recommendations",
                    "Lifestyle modifications"
                ]
            },
            "https://www.drsayuj.info/contact": {
                "current_word_count": "~200",
                "target_word_count": "400+",
                "suggested_additions": [
                    "Detailed clinic information",
                    "Office hours and availability",
                    "Emergency contact procedures",
                    "Insurance and payment information",
                    "What to expect during consultation",
                    "Preparation for appointment",
                    "Location and parking details"
                ]
            },
            "https://www.drsayuj.info/patient-stories/minimal-invasive-meningioma-resection": {
                "current_word_count": "~250",
                "target_word_count": "800+",
                "suggested_additions": [
                    "Detailed patient background",
                    "Symptoms and diagnosis process",
                    "Treatment decision-making",
                    "Surgical procedure details",
                    "Recovery journey",
                    "Follow-up care",
                    "Patient testimonial",
                    "Lessons learned"
                ]
            }
        }
        
        return expansion_plan

def main():
    """Main function to run the troubleshooting analysis"""
    import glob
    
    # Find the most recent analysis file
    analysis_files = glob.glob("/Users/dr.sayujkrishnan/Documents/openai-chatkit-advanced-samples/reports/seo/*/analysis.json")
    if not analysis_files:
        print("No analysis data found. Please run analyze_crawl.py first.")
        return
    
    latest_analysis_file = max(analysis_files, key=os.path.getctime)
    print(f"Troubleshooting issues from: {latest_analysis_file}")
    
    # Create troubleshooter
    troubleshooter = SEOTroubleshooter(latest_analysis_file)
    troubleshooter.analyze_issues()
    
    # Generate recommendations
    recommendations = troubleshooter.generate_fix_recommendations()
    
    # Create output directory
    output_dir = os.path.dirname(latest_analysis_file)
    
    # Save troubleshooting results
    troubleshooting_file = os.path.join(output_dir, "troubleshooting_plan.json")
    with open(troubleshooting_file, 'w') as f:
        json.dump({
            "recommendations": recommendations,
            "redirect_rules": troubleshooter.create_redirect_rules(),
            "title_suggestions": troubleshooter.create_title_suggestions(),
            "content_expansion_plan": troubleshooter.create_content_expansion_plan()
        }, f, indent=2)
    
    print(f"Troubleshooting plan saved to: {troubleshooting_file}")
    
    # Print summary
    print(f"\n=== TROUBLESHOOTING SUMMARY ===")
    print(f"Critical fixes needed: {len(recommendations['critical_fixes'])}")
    print(f"High priority fixes needed: {len(recommendations['high_priority_fixes'])}")
    print(f"Medium priority fixes needed: {len(recommendations['medium_priority_fixes'])}")
    
    print(f"\n=== CRITICAL FIXES ===")
    for fix in recommendations['critical_fixes']:
        print(f"- {fix['description']}")
        print(f"  Action: {fix['action']}")
    
    print(f"\n=== HIGH PRIORITY FIXES ===")
    for fix in recommendations['high_priority_fixes']:
        print(f"- {fix['description']}")
        print(f"  Action: {fix['action']}")
    
    print(f"\n=== MEDIUM PRIORITY FIXES ===")
    for fix in recommendations['medium_priority_fixes']:
        print(f"- {fix['description']}")
        print(f"  Action: {fix['action']}")

if __name__ == "__main__":
    main()
