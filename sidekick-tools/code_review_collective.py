#!/usr/bin/env python3
"""
SIDEKICK Code Review Collective
Unified interface for distributed AI code review
Integrates Security Auditor (Claude B) and Architecture Reviewer (Claude A)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import our distributed AI components
try:
    from security_auditor import SecurityAuditor
    from architecture_reviewer import ArchitectureReviewer
except ImportError as e:
    print(f"Error importing components: {e}")
    print("Make sure security_auditor.py and architecture_reviewer.py are in the same directory")
    sys.exit(1)

class CodeReviewCollective:
    """Unified code review system using distributed AI components"""
    
    def __init__(self):
        self.security_auditor = SecurityAuditor()
        self.architecture_reviewer = ArchitectureReviewer()
        
    def review_file(self, file_path: str, options: Dict[str, bool] = None) -> Dict[str, Any]:
        """Perform comprehensive code review using both AI components"""
        if options is None:
            options = {"security": True, "architecture": True}
        
        results = {
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            "reviews": {},
            "combined_score": 0,
            "recommendations": [],
            "summary": ""
        }
        
        # Read the code file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception as e:
            return {
                "error": f"Failed to read file {file_path}: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        
        print(f"🔍 Analyzing {file_path}...")
        
        # Run Security Analysis (Claude B's component)
        if options.get("security", True):
            print("🔒 Running security analysis...")
            try:
                security_results = self.security_auditor.analyze_code(code_content, file_path)
                results["reviews"]["security"] = security_results
                print(f"   Security analysis complete - Risk: {security_results.get('risk_score', 'N/A')}")
            except Exception as e:
                results["reviews"]["security"] = {"error": str(e)}
                print(f"   Security analysis failed: {e}")
        
        # Run Architecture Analysis (Claude A's component)  
        if options.get("architecture", True):
            print("🏗️  Running architecture analysis...")
            try:
                architecture_results = self.architecture_reviewer.review_code(code_content, file_path)
                results["reviews"]["architecture"] = architecture_results
                print(f"   Architecture analysis complete - Score: {architecture_results.get('overall_score', 'N/A')}/10")
            except Exception as e:
                results["reviews"]["architecture"] = {"error": str(e)}
                print(f"   Architecture analysis failed: {e}")
        
        # Generate combined analysis
        results.update(self._combine_analyses(results["reviews"]))
        
        return results
    
    def _combine_analyses(self, reviews: Dict[str, Any]) -> Dict[str, Any]:
        """Combine security and architecture analyses into unified report"""
        combined_score = 0
        recommendations = []
        issues = []
        
        # Process Security Results
        security = reviews.get("security", {})
        if "error" not in security:
            # Convert risk score (0-100, lower is better) to quality score (0-10, higher is better)
            risk_score = security.get("risk_score", 50)
            security_quality_score = max(0, 10 - (risk_score / 10))
            
            combined_score += security_quality_score * 0.4  # 40% weight
            
            # Add security recommendations
            if "findings" in security:
                for finding in security["findings"]:
                    severity = finding.get("severity", "unknown")
                    recommendations.append(f"Security ({severity}): {finding.get('description', 'Unknown issue')}")
                    issues.append({
                        "type": "security",
                        "severity": severity,
                        "description": finding.get("description", ""),
                        "line": finding.get("line_number", 0)
                    })
        
        # Process Architecture Results
        architecture = reviews.get("architecture", {})
        if "error" not in architecture:
            arch_score = architecture.get("overall_score", 5)
            combined_score += arch_score * 0.6  # 60% weight
            
            # Add architecture recommendations
            arch_recommendations = architecture.get("recommendations", [])
            recommendations.extend([f"Architecture: {rec}" for rec in arch_recommendations[:3]])
            
            # Extract architecture issues
            for category in architecture.get("analysis", {}).values():
                if isinstance(category, dict) and "issues" in category:
                    for issue in category["issues"]:
                        issues.append({
                            "type": "architecture", 
                            "severity": issue.get("severity", "low"),
                            "description": issue.get("description", ""),
                            "line": issue.get("line", 0)
                        })
        
        # Generate summary
        summary = self._generate_summary(combined_score, len(issues), reviews)
        
        return {
            "combined_score": round(combined_score, 2),
            "recommendations": recommendations[:5],  # Top 5 recommendations
            "issues": issues,
            "summary": summary
        }
    
    def _generate_summary(self, score: float, issue_count: int, reviews: Dict[str, Any]) -> str:
        """Generate human-readable summary"""
        # Quality assessment
        if score >= 8.0:
            quality = "Excellent"
            emoji = "🟢"
        elif score >= 6.0:
            quality = "Good" 
            emoji = "🟡"
        elif score >= 4.0:
            quality = "Fair"
            emoji = "🟠"
        else:
            quality = "Needs Improvement"
            emoji = "🔴"
        
        # Component status
        security_status = "✅" if "security" in reviews and "error" not in reviews["security"] else "❌"
        architecture_status = "✅" if "architecture" in reviews and "error" not in reviews["architecture"] else "❌"
        
        summary = f"{emoji} Overall Quality: {quality} (Score: {score}/10)\n"
        summary += f"Security Analysis: {security_status} | Architecture Analysis: {architecture_status}\n"
        summary += f"Total Issues Found: {issue_count}"
        
        return summary
    
    def export_report(self, results: Dict[str, Any], output_path: str) -> bool:
        """Export review results to JSON file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Failed to export report: {e}")
            return False
    
    def print_report(self, results: Dict[str, Any], verbose: bool = False):
        """Print formatted review results to console"""
        print("\n" + "="*70)
        print(f"🎯 SIDEKICK CODE REVIEW COLLECTIVE REPORT")
        print("="*70)
        print(f"📁 File: {results['file_path']}")
        print(f"⏰ Timestamp: {results['timestamp']}")
        print()
        
        # Summary
        print("📊 SUMMARY:")
        print(results['summary'])
        print()
        
        # Recommendations
        if results.get('recommendations'):
            print("💡 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"   {i}. {rec}")
            print()
        
        # Detailed results (if verbose)
        if verbose:
            print("🔍 DETAILED ANALYSIS:")
            
            # Security details
            security = results['reviews'].get('security', {})
            if security and "error" not in security:
                print(f"   🔒 Security Risk Score: {security.get('risk_score', 'N/A')}/100")
                findings = security.get('findings', [])
                print(f"   🔒 Security Findings: {len(findings)}")
            
            # Architecture details
            architecture = results['reviews'].get('architecture', {})
            if architecture and "error" not in architecture:
                print(f"   🏗️  Architecture Score: {architecture.get('overall_score', 'N/A')}/10")
                arch_analysis = architecture.get('analysis', {})
                total_issues = sum(len(cat.get('issues', [])) for cat in arch_analysis.values() if isinstance(cat, dict))
                print(f"   🏗️  Architecture Issues: {total_issues}")
            print()
        
        print("✅ Review complete! Results stored in SIDEKICK memory.")
        print("="*70)

def main():
    """CLI entry point for Code Review Collective"""
    parser = argparse.ArgumentParser(
        description="SIDEKICK Code Review Collective - Distributed AI Code Analysis",
        epilog="Example: python code_review_collective.py myfile.py --verbose --save-report"
    )
    
    parser.add_argument("file", help="Python file to analyze")
    parser.add_argument("--security-only", action="store_true", help="Run only security analysis")
    parser.add_argument("--architecture-only", action="store_true", help="Run only architecture analysis")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--save-report", type=str, metavar="FILE", help="Save report to JSON file")
    parser.add_argument("--verbose", action="store_true", help="Show detailed analysis results")
    
    args = parser.parse_args()
    
    # Validate file exists
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    # Determine analysis options
    options = {
        "security": not args.architecture_only,
        "architecture": not args.security_only
    }
    
    # Run the analysis
    collective = CodeReviewCollective()
    
    print("🚀 SIDEKICK Code Review Collective")
    print(f"Distributed AI Analysis: Security Auditor (Claude B) + Architecture Reviewer (Claude A)")
    print()
    
    try:
        results = collective.review_file(args.file, options)
        
        if args.json:
            # JSON output
            print(json.dumps(results, indent=2, default=str))
        else:
            # Formatted output
            collective.print_report(results, args.verbose)
        
        # Save report if requested
        if args.save_report:
            if collective.export_report(results, args.save_report):
                print(f"📄 Report saved to {args.save_report}")
            else:
                print("❌ Failed to save report")
        
    except KeyboardInterrupt:
        print("\n❌ Analysis cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()