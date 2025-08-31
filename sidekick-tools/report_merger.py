#!/usr/bin/env python3
"""
SIDEKICK Report Merger System
Combines Security Auditor and Architecture Reviewer reports into unified analysis
Part of the Code Review Collective integration system
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class UnifiedFinding:
    """Unified finding structure combining security and architecture insights"""
    category: str  # security, architecture, or combined
    type: str  # specific finding type
    severity: str  # critical, high, medium, low, info
    title: str
    description: str
    line_number: int
    code_snippet: str
    recommendation: str
    confidence: float
    source: str  # security_auditor, architecture_reviewer, or merged

@dataclass
class CodeQualityScore:
    """Overall code quality scoring system"""
    security_score: float  # 0-100 (100 = most secure)
    architecture_score: float  # 0-100 (100 = best architecture)
    overall_score: float  # 0-100 weighted combination
    grade: str  # A, B, C, D, F
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL

class ReportMerger:
    """Merges security and architecture analysis reports"""
    
    def __init__(self):
        self.security_weight = 0.6  # Security weighted higher
        self.architecture_weight = 0.4
    
    def merge_reports(self, security_report: Dict[str, Any], architecture_report: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Merge security and architecture reports into unified analysis"""
        
        # Extract findings from both reports
        security_findings = self._convert_security_findings(security_report.get("findings", []))
        architecture_findings = self._convert_architecture_findings(architecture_report.get("findings", []))
        
        # Combine all findings
        all_findings = security_findings + architecture_findings
        
        # Identify overlapping issues and merge them
        merged_findings = self._merge_overlapping_findings(all_findings)
        
        # Calculate unified quality score
        quality_score = self._calculate_quality_score(security_report, architecture_report)
        
        # Generate recommendations prioritized by impact
        recommendations = self._generate_prioritized_recommendations(merged_findings)
        
        # Create unified report structure
        unified_report = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "analysis_type": "comprehensive_code_review",
            "quality_score": asdict(quality_score),
            "summary": {
                "total_findings": len(merged_findings),
                "security_findings": len(security_findings),
                "architecture_findings": len(architecture_findings),
                "merged_findings": len(merged_findings) - len(security_findings) - len(architecture_findings),
                "severity_breakdown": self._calculate_severity_breakdown(merged_findings),
                "category_breakdown": self._calculate_category_breakdown(merged_findings)
            },
            "findings": [asdict(finding) for finding in merged_findings],
            "recommendations": recommendations,
            "raw_reports": {
                "security": security_report,
                "architecture": architecture_report
            }
        }
        
        return unified_report
    
    def _convert_security_findings(self, security_findings: List[Dict]) -> List[UnifiedFinding]:
        """Convert security findings to unified format"""
        unified = []
        for finding in security_findings:
            unified_finding = UnifiedFinding(
                category="security",
                type=finding.get("category", "unknown"),
                severity=finding.get("severity", "info"),
                title=finding.get("title", "Security Issue"),
                description=finding.get("description", ""),
                line_number=finding.get("line_number", 0),
                code_snippet=finding.get("code_snippet", ""),
                recommendation=finding.get("recommendation", ""),
                confidence=finding.get("confidence", 0.5),
                source="security_auditor"
            )
            unified.append(unified_finding)
        return unified
    
    def _convert_architecture_findings(self, architecture_findings: List[Dict]) -> List[UnifiedFinding]:
        """Convert architecture findings to unified format"""
        unified = []
        for finding in architecture_findings:
            # Map architecture severity to unified scale
            arch_severity = finding.get("severity", "info")
            unified_severity = self._map_architecture_severity(arch_severity)
            
            unified_finding = UnifiedFinding(
                category="architecture",
                type=finding.get("category", "design"),
                severity=unified_severity,
                title=finding.get("title", "Architecture Issue"),
                description=finding.get("description", ""),
                line_number=finding.get("line_number", 0),
                code_snippet=finding.get("code_snippet", ""),
                recommendation=finding.get("recommendation", ""),
                confidence=finding.get("confidence", 0.7),
                source="architecture_reviewer"
            )
            unified.append(unified_finding)
        return unified
    
    def _map_architecture_severity(self, arch_severity: str) -> str:
        """Map architecture-specific severity to unified security scale"""
        severity_mapping = {
            "major": "high",
            "minor": "medium", 
            "suggestion": "low",
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "info": "info"
        }
        return severity_mapping.get(arch_severity.lower(), "medium")
    
    def _merge_overlapping_findings(self, findings: List[UnifiedFinding]) -> List[UnifiedFinding]:
        """Identify and merge overlapping issues between security and architecture"""
        merged = []
        processed = set()
        
        for i, finding in enumerate(findings):
            if i in processed:
                continue
                
            # Look for related findings (same line, similar issue)
            related_findings = []
            for j, other_finding in enumerate(findings[i+1:], i+1):
                if j in processed:
                    continue
                    
                if self._are_findings_related(finding, other_finding):
                    related_findings.append(other_finding)
                    processed.add(j)
            
            if related_findings:
                # Merge the findings
                merged_finding = self._create_merged_finding(finding, related_findings)
                merged.append(merged_finding)
            else:
                merged.append(finding)
            
            processed.add(i)
        
        return merged
    
    def _are_findings_related(self, finding1: UnifiedFinding, finding2: UnifiedFinding) -> bool:
        """Determine if two findings are related and should be merged"""
        # Same line number (within 2 lines)
        line_diff = abs(finding1.line_number - finding2.line_number)
        if line_diff <= 2:
            return True
        
        # Similar code snippets
        if finding1.code_snippet and finding2.code_snippet:
            snippet_similarity = self._calculate_snippet_similarity(finding1.code_snippet, finding2.code_snippet)
            if snippet_similarity > 0.7:
                return True
        
        # Related issue types
        related_types = {
            ("sql_injection", "input_validation"),
            ("xss", "input_validation"),
            ("auth", "design_pattern"),
            ("secrets", "hardcoded_values")
        }
        
        type_pair = (finding1.type, finding2.type)
        if type_pair in related_types or tuple(reversed(type_pair)) in related_types:
            return True
        
        return False
    
    def _calculate_snippet_similarity(self, snippet1: str, snippet2: str) -> float:
        """Calculate similarity between code snippets (simple implementation)"""
        if not snippet1 or not snippet2:
            return 0.0
        
        # Simple token-based similarity
        tokens1 = set(snippet1.lower().split())
        tokens2 = set(snippet2.lower().split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union)
    
    def _create_merged_finding(self, primary: UnifiedFinding, related: List[UnifiedFinding]) -> UnifiedFinding:
        """Create a merged finding from primary and related findings"""
        # Use highest severity
        all_findings = [primary] + related
        severities = ["critical", "high", "medium", "low", "info"]
        highest_severity = "info"
        
        for severity in severities:
            if any(f.severity == severity for f in all_findings):
                highest_severity = severity
                break
        
        # Combine descriptions and recommendations
        descriptions = [f.description for f in all_findings if f.description]
        recommendations = [f.recommendation for f in all_findings if f.recommendation]
        
        merged_description = " Additionally: ".join(descriptions)
        merged_recommendation = " Also: ".join(recommendations)
        
        # Average confidence scores
        confidences = [f.confidence for f in all_findings]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Create merged finding
        merged = UnifiedFinding(
            category="combined",
            type=f"{primary.type}_combined",
            severity=highest_severity,
            title=f"Combined Issue: {primary.title}",
            description=merged_description,
            line_number=primary.line_number,
            code_snippet=primary.code_snippet,
            recommendation=merged_recommendation,
            confidence=avg_confidence,
            source="merged"
        )
        
        return merged
    
    def _calculate_quality_score(self, security_report: Dict, architecture_report: Dict) -> CodeQualityScore:
        """Calculate overall code quality score"""
        # Extract scores from reports
        security_risk_score = security_report.get("summary", {}).get("risk_score", 0)
        architecture_score = architecture_report.get("summary", {}).get("overall_score", 8.0)  # Assuming 0-10 scale
        
        # Convert to 0-100 scale (100 = best)
        security_score = max(0, 100 - security_risk_score)  # Invert risk score
        arch_score = architecture_score * 10  # Convert 0-10 to 0-100
        
        # Calculate weighted overall score
        overall_score = (security_score * self.security_weight + 
                        arch_score * self.architecture_weight)
        
        # Determine grade and risk level
        if overall_score >= 90:
            grade = "A"
            risk_level = "LOW"
        elif overall_score >= 80:
            grade = "B"
            risk_level = "LOW"
        elif overall_score >= 70:
            grade = "C"
            risk_level = "MEDIUM"
        elif overall_score >= 60:
            grade = "D"
            risk_level = "HIGH"
        else:
            grade = "F"
            risk_level = "CRITICAL"
        
        return CodeQualityScore(
            security_score=round(security_score, 1),
            architecture_score=round(arch_score, 1),
            overall_score=round(overall_score, 1),
            grade=grade,
            risk_level=risk_level
        )
    
    def _calculate_severity_breakdown(self, findings: List[UnifiedFinding]) -> Dict[str, int]:
        """Calculate severity breakdown for merged findings"""
        breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for finding in findings:
            breakdown[finding.severity] += 1
        return breakdown
    
    def _calculate_category_breakdown(self, findings: List[UnifiedFinding]) -> Dict[str, int]:
        """Calculate category breakdown for merged findings"""
        breakdown = {}
        for finding in findings:
            breakdown[finding.category] = breakdown.get(finding.category, 0) + 1
        return breakdown
    
    def _generate_prioritized_recommendations(self, findings: List[UnifiedFinding]) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations based on findings"""
        recommendations = []
        
        # Group findings by severity and type
        critical_security = [f for f in findings if f.severity == "critical" and f.category == "security"]
        high_severity = [f for f in findings if f.severity == "high"]
        architecture_major = [f for f in findings if f.category == "architecture" and f.severity in ["high", "critical"]]
        
        # Priority 1: Critical Security Issues
        if critical_security:
            recommendations.append({
                "priority": 1,
                "title": "URGENT: Critical Security Vulnerabilities",
                "description": f"Address {len(critical_security)} critical security issues immediately",
                "action": "Review and fix all critical security vulnerabilities before deployment",
                "estimated_effort": "High",
                "impact": "Critical"
            })
        
        # Priority 2: High Severity Issues
        if high_severity:
            recommendations.append({
                "priority": 2,
                "title": "High Priority Issues",
                "description": f"Resolve {len(high_severity)} high-severity findings",
                "action": "Address high-severity security and architecture issues",
                "estimated_effort": "Medium-High",
                "impact": "High"
            })
        
        # Priority 3: Architecture Improvements
        if architecture_major:
            recommendations.append({
                "priority": 3,
                "title": "Architecture Improvements",
                "description": f"Improve code architecture in {len(architecture_major)} areas",
                "action": "Refactor code to follow better design patterns and principles",
                "estimated_effort": "Medium",
                "impact": "Medium"
            })
        
        return recommendations

def main():
    """Test the report merger with sample data"""
    print("🔄 SIDEKICK Report Merger System")
    print("=" * 50)
    
    # Sample security report
    security_report = {
        "summary": {"risk_score": 45, "total_findings": 3},
        "findings": [
            {
                "category": "sql_injection",
                "severity": "high",
                "title": "SQL Injection Risk",
                "description": "Potential SQL injection vulnerability",
                "line_number": 15,
                "code_snippet": "query = f'SELECT * FROM users WHERE id = {user_id}'",
                "recommendation": "Use parameterized queries",
                "confidence": 0.8
            }
        ]
    }
    
    # Sample architecture report
    architecture_report = {
        "summary": {"overall_score": 7.2, "total_findings": 2},
        "findings": [
            {
                "category": "design_pattern",
                "severity": "medium",
                "title": "Missing Design Pattern",
                "description": "Could benefit from Factory pattern",
                "line_number": 25,
                "code_snippet": "obj = SomeClass(param1, param2)",
                "recommendation": "Consider using Factory pattern",
                "confidence": 0.6
            }
        ]
    }
    
    merger = ReportMerger()
    unified_report = merger.merge_reports(security_report, architecture_report, "sample.py")
    
    print(f"📊 Unified Quality Score: {unified_report['quality_score']['overall_score']:.1f}/100")
    print(f"🎯 Grade: {unified_report['quality_score']['grade']}")
    print(f"⚠️ Risk Level: {unified_report['quality_score']['risk_level']}")
    print(f"🔍 Total Findings: {unified_report['summary']['total_findings']}")
    
    # Save sample report
    with open("sample_unified_report.json", "w") as f:
        json.dump(unified_report, f, indent=2)
    
    print("✅ Sample unified report generated: sample_unified_report.json")

if __name__ == "__main__":
    main()