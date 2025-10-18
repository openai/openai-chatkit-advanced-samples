#!/usr/bin/env python3
"""
FAQ Structured Data Fix Script
Fixes duplicate FAQPage schemas on drsayuj.info homepage
"""

import json
from typing import Dict, List, Any

class FAQStructuredDataFixer:
    def __init__(self):
        self.fixed_schema = None
        
    def create_consolidated_faq_schema(self) -> Dict[str, Any]:
        """Create a single, consolidated FAQPage schema"""
        
        # Consolidated FAQ content from both schemas
        faq_items = [
            {
                "@type": "Question",
                "name": "How do I know if I'm a candidate for endoscopic spine surgery?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "You may be a candidate for endoscopic spine surgery if you have conditions like herniated discs, spinal stenosis, or sciatica that haven't responded to conservative treatments. Dr. Sayuj Krishnan will evaluate your specific condition, medical history, and imaging studies to determine if you're a good candidate for this minimally invasive procedure."
                }
            },
            {
                "@type": "Question", 
                "name": "What are the benefits of endoscopic spine surgery?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Endoscopic spine surgery offers several benefits including smaller incisions, less tissue damage, reduced blood loss, faster recovery times, lower risk of infection, and minimal scarring. Most patients can return to normal activities much sooner compared to traditional open surgery."
                }
            },
            {
                "@type": "Question",
                "name": "How long is the recovery time for endoscopic spine surgery?",
                "acceptedAnswer": {
                    "@type": "Answer", 
                    "text": "Recovery time varies depending on the specific procedure and individual patient factors. Generally, patients can return to light activities within 1-2 weeks and resume normal activities within 4-6 weeks. Dr. Sayuj Krishnan provides personalized recovery plans for each patient."
                }
            },
            {
                "@type": "Question",
                "name": "Is endoscopic spine surgery safe?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes, endoscopic spine surgery is considered safe when performed by experienced surgeons like Dr. Sayuj Krishnan. The procedure uses advanced technology and techniques to minimize risks. Dr. Sayuj has extensive experience in minimally invasive spine surgery and follows strict safety protocols."
                }
            },
            {
                "@type": "Question",
                "name": "What conditions can be treated with endoscopic spine surgery?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Endoscopic spine surgery can treat various conditions including herniated discs, spinal stenosis, sciatica, degenerative disc disease, and certain types of spinal tumors. Dr. Sayuj Krishnan specializes in treating these conditions using the latest endoscopic techniques."
                }
            },
            {
                "@type": "Question",
                "name": "How much does endoscopic spine surgery cost in Hyderabad?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "The cost of endoscopic spine surgery varies depending on the specific procedure, complexity, and hospital stay. Dr. Sayuj Krishnan's team provides transparent pricing information during consultation. Many insurance plans cover these procedures, and financing options are available."
                }
            }
        ]
        
        # Create the consolidated FAQPage schema
        consolidated_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "@id": "https://www.drsayuj.info#faq",
            "mainEntity": faq_items
        }
        
        return consolidated_schema
    
    def generate_fix_instructions(self) -> Dict[str, Any]:
        """Generate detailed fix instructions"""
        
        return {
            "issue_description": "Duplicate FAQPage schemas on homepage",
            "problem": "Two separate FAQPage schemas exist on https://www.drsayuj.info/",
            "impact": "Critical - prevents optimal appearance in Google Search results",
            "solution": {
                "action": "Remove duplicate FAQPage schemas and consolidate into one",
                "steps": [
                    "1. Remove the first FAQPage schema (without @id)",
                    "2. Keep the second FAQPage schema (with @id: 'https://www.drsayuj.info#faq')",
                    "3. Update the kept schema with consolidated FAQ content",
                    "4. Ensure only one FAQPage schema exists on the homepage"
                ],
                "consolidated_schema": self.create_consolidated_faq_schema()
            },
            "implementation_notes": {
                "priority": "Critical - affects search visibility",
                "timeline": "Immediate implementation recommended",
                "testing": "Validate with Google Rich Results Test after implementation",
                "monitoring": "Check Google Search Console for issue resolution"
            },
            "validation": {
                "google_rich_results_test": "https://search.google.com/test/rich-results",
                "schema_validator": "https://validator.schema.org/",
                "search_console": "Monitor for 'FAQ structured data issue' resolution"
            }
        }
    
    def create_implementation_guide(self) -> str:
        """Create step-by-step implementation guide"""
        
        guide = """
# FAQ Structured Data Fix Implementation Guide

## Issue Summary
- **URL**: https://www.drsayuj.info/
- **Problem**: Duplicate FAQPage schemas (2 found)
- **Severity**: Critical
- **Impact**: Prevents optimal appearance in Google Search results

## Current State
The homepage contains TWO separate FAQPage schemas:
1. First schema: Standalone FAQPage without @id
2. Second schema: FAQPage with @id "https://www.drsayuj.info#faq"

Both schemas contain similar FAQ content about endoscopic spine surgery.

## Solution
Consolidate both schemas into a single, comprehensive FAQPage schema.

## Implementation Steps

### Step 1: Locate the Duplicate Schemas
Find the following in the homepage HTML:
- First FAQPage schema (around line 250-318 in analysis)
- Second FAQPage schema (around line 324-394 in analysis)

### Step 2: Remove the First Schema
Delete the first FAQPage schema (the one without @id).

### Step 3: Update the Second Schema
Replace the second FAQPage schema with the consolidated version:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "@id": "https://www.drsayuj.info#faq",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How do I know if I'm a candidate for endoscopic spine surgery?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "You may be a candidate for endoscopic spine surgery if you have conditions like herniated discs, spinal stenosis, or sciatica that haven't responded to conservative treatments. Dr. Sayuj Krishnan will evaluate your specific condition, medical history, and imaging studies to determine if you're a good candidate for this minimally invasive procedure."
      }
    },
    {
      "@type": "Question", 
      "name": "What are the benefits of endoscopic spine surgery?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Endoscopic spine surgery offers several benefits including smaller incisions, less tissue damage, reduced blood loss, faster recovery times, lower risk of infection, and minimal scarring. Most patients can return to normal activities much sooner compared to traditional open surgery."
      }
    },
    {
      "@type": "Question",
      "name": "How long is the recovery time for endoscopic spine surgery?",
      "acceptedAnswer": {
        "@type": "Answer", 
        "text": "Recovery time varies depending on the specific procedure and individual patient factors. Generally, patients can return to light activities within 1-2 weeks and resume normal activities within 4-6 weeks. Dr. Sayuj Krishnan provides personalized recovery plans for each patient."
      }
    },
    {
      "@type": "Question",
      "name": "Is endoscopic spine surgery safe?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, endoscopic spine surgery is considered safe when performed by experienced surgeons like Dr. Sayuj Krishnan. The procedure uses advanced technology and techniques to minimize risks. Dr. Sayuj has extensive experience in minimally invasive spine surgery and follows strict safety protocols."
      }
    },
    {
      "@type": "Question",
      "name": "What conditions can be treated with endoscopic spine surgery?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Endoscopic spine surgery can treat various conditions including herniated discs, spinal stenosis, sciatica, degenerative disc disease, and certain types of spinal tumors. Dr. Sayuj Krishnan specializes in treating these conditions using the latest endoscopic techniques."
      }
    },
    {
      "@type": "Question",
      "name": "How much does endoscopic spine surgery cost in Hyderabad?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The cost of endoscopic spine surgery varies depending on the specific procedure, complexity, and hospital stay. Dr. Sayuj Krishnan's team provides transparent pricing information during consultation. Many insurance plans cover these procedures, and financing options are available."
      }
    }
  ]
}
```

### Step 4: Validation
After implementation:
1. Test with Google Rich Results Test: https://search.google.com/test/rich-results
2. Validate with Schema.org validator: https://validator.schema.org/
3. Check Google Search Console for issue resolution

### Step 5: Monitoring
- Monitor Google Search Console for "FAQ structured data issue" resolution
- Check that only one FAQPage schema appears in search results
- Verify FAQ rich snippets are displaying correctly

## Expected Results
- ✅ Single FAQPage schema on homepage
- ✅ No duplicate structured data errors
- ✅ Improved search result appearance
- ✅ Better FAQ rich snippet display

## Timeline
- **Implementation**: Immediate (within 24 hours)
- **Validation**: Within 48 hours
- **Search Console Update**: 1-2 weeks
- **Full Resolution**: 2-4 weeks

## Risk Assessment
- **Risk Level**: Low
- **Impact**: High positive impact on search visibility
- **Rollback**: Easy to revert if needed
"""
        
        return guide

def main():
    """Main function to generate FAQ fix"""
    fixer = FAQStructuredDataFixer()
    
    # Generate fix instructions
    fix_instructions = fixer.generate_fix_instructions()
    
    # Save fix instructions
    output_file = "/Users/dr.sayujkrishnan/Documents/openai-chatkit-advanced-samples/reports/seo/2025-10-15_11-01-00/faq_structured_data_fix.json"
    with open(output_file, 'w') as f:
        json.dump(fix_instructions, f, indent=2)
    
    print(f"FAQ structured data fix instructions saved to: {output_file}")
    
    # Generate implementation guide
    implementation_guide = fixer.create_implementation_guide()
    guide_file = "/Users/dr.sayujkrishnan/Documents/openai-chatkit-advanced-samples/reports/seo/2025-10-15_11-01-00/faq_implementation_guide.md"
    with open(guide_file, 'w') as f:
        f.write(implementation_guide)
    
    print(f"FAQ implementation guide saved to: {guide_file}")
    
    # Print summary
    print(f"\n=== FAQ STRUCTURED DATA FIX SUMMARY ===")
    print(f"Issue: Duplicate FAQPage schemas on homepage")
    print(f"Severity: Critical")
    print(f"Solution: Consolidate into single FAQPage schema")
    print(f"Timeline: Immediate implementation recommended")
    print(f"Expected Result: Resolution of Google Search Console error")

if __name__ == "__main__":
    main()
