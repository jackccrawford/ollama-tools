#!/usr/bin/env python3
"""
SIDEKICK Security Auditor Component
AI-powered security vulnerability detection and analysis
Part of the Code Review Collective system

Analyzes code for:
- SQL injection vulnerabilities
- XSS (Cross-Site Scripting) risks
- Authentication/authorization flaws
- Secret exposure (API keys, passwords, tokens)
- Input validation issues
- Path traversal vulnerabilities
"""

import os
import re
import json
import ast
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict

@dataclass
class SecurityFinding:
    """Structure for security vulnerability findings"""
    severity: str  # critical, high, medium, low, info
    category: str  # sql_injection, xss, auth, secrets, input_validation, path_traversal
    title: str
    description: str
    line_number: int
    code_snippet: str
    recommendation: str
    confidence: float  # 0.0 to 1.0

class SecurityAuditor:
    """AI-powered security auditor for code analysis"""
    
    def __init__(self, db_path: str = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"):
        self.db_path = db_path
        self.findings: List[SecurityFinding] = []
        
        # Security pattern definitions
        self.sql_patterns = [
            r'\.execute\s*\(\s*["\'].*?%s.*?["\']',  # String formatting in SQL
            r'\.execute\s*\(\s*f["\'].*?\{.*?\}.*?["\']',  # F-string in SQL
            r'SELECT.*?\+.*?["\']',  # String concatenation in SELECT
            r'INSERT.*?\+.*?["\']',  # String concatenation in INSERT
            r'UPDATE.*?\+.*?["\']',  # String concatenation in UPDATE
            r'DELETE.*?\+.*?["\']',  # String concatenation in DELETE
        ]
        
        self.xss_patterns = [
            r'innerHTML\s*=.*?[+].*?["\']',  # innerHTML with concatenation
            r'document\.write\s*\(.*?[+].*?\)',  # document.write with concat
            r'\.html\s*\(.*?[+].*?\)',  # jQuery .html() with concat
            r'eval\s*\(.*?[+].*?\)',  # eval with user input
            r'dangerouslySetInnerHTML',  # React dangerous HTML
        ]
        
        self.secret_patterns = [
            r'["\'](?:api_key|apikey|api-key)\s*[=:]\s*["\'][^"\']{8,}["\']',
            r'["\'](?:password|pwd|pass)\s*[=:]\s*["\'][^"\']{4,}["\']',
            r'["\'](?:token|access_token|auth_token)\s*[=:]\s*["\'][^"\']{10,}["\']',
            r'["\'](?:secret|private_key|priv_key)\s*[=:]\s*["\'][^"\']{8,}["\']',
            r'[A-Za-z0-9]{32,}',  # Long hex strings (potential keys)
            r'sk_[a-zA-Z0-9]{24,}',  # Stripe secret keys
            r'ghp_[a-zA-Z0-9]{36}',  # GitHub personal access tokens
        ]
        
        self.auth_patterns = [
            r'if.*?password\s*==\s*["\'].*?["\']',  # Hardcoded password check
            r'admin.*?==.*?True',  # Simple admin checks
            r'user\.is_admin\s*=\s*True',  # Direct admin assignment
            r'session\[["\'].*?["\']\]\s*=.*?without.*?validation',  # Session without validation
        ]
        
        self.input_validation_patterns = [
            r'request\.(GET|POST|args|form)\[.*?\].*?without.*?validation',
            r'input\s*\(.*?\).*?without.*?sanitization',
            r'os\.system\s*\(.*?user.*?input',  # OS command with user input
            r'subprocess\..*?\(.*?user.*?input',  # Subprocess with user input
            r'open\s*\(.*?user.*?input',  # File operations with user input
        ]
    
    def analyze_file(self, file_path: str) -> List[SecurityFinding]:
        """Analyze a code file for security vulnerabilities"""
        self.findings = []
        
        if not os.path.exists(file_path):
            return self.findings
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Perform various security analyses
            self._check_sql_injection(content, lines)
            self._check_xss_vulnerabilities(content, lines)
            self._check_secret_exposure(content, lines)
            self._check_auth_issues(content, lines)
            self._check_input_validation(content, lines)
            self._check_path_traversal(content, lines)
            
            return self.findings
            
        except Exception as e:
            # Create finding for analysis error
            finding = SecurityFinding(
                severity="info",
                category="analysis_error",
                title="Security Analysis Error",
                description=f"Could not analyze file: {str(e)}",
                line_number=0,
                code_snippet="",
                recommendation="Ensure file is readable and contains valid code",
                confidence=1.0
            )
            self.findings.append(finding)
            return self.findings
    
    def _check_sql_injection(self, content: str, lines: List[str]):
        """Check for SQL injection vulnerabilities"""
        for pattern in self.sql_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                
                finding = SecurityFinding(
                    severity="high",
                    category="sql_injection",
                    title="Potential SQL Injection",
                    description="SQL query appears to use string concatenation or formatting which could lead to SQL injection",
                    line_number=line_num,
                    code_snippet=code_snippet.strip(),
                    recommendation="Use parameterized queries or prepared statements instead of string concatenation",
                    confidence=0.8
                )
                self.findings.append(finding)
    
    def _check_xss_vulnerabilities(self, content: str, lines: List[str]):
        """Check for XSS vulnerabilities"""
        for pattern in self.xss_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                
                finding = SecurityFinding(
                    severity="high",
                    category="xss",
                    title="Potential XSS Vulnerability",
                    description="Code appears to inject user data into HTML without proper escaping",
                    line_number=line_num,
                    code_snippet=code_snippet.strip(),
                    recommendation="Sanitize and escape all user input before inserting into HTML",
                    confidence=0.75
                )
                self.findings.append(finding)
    
    def _check_secret_exposure(self, content: str, lines: List[str]):
        """Check for exposed secrets and credentials"""
        for pattern in self.secret_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                
                # Skip common false positives
                if any(fp in code_snippet.lower() for fp in ['example', 'test', 'demo', 'placeholder', 'xxx']):
                    continue
                
                finding = SecurityFinding(
                    severity="critical",
                    category="secrets",
                    title="Potential Secret Exposure",
                    description="Code appears to contain hardcoded secrets, API keys, or credentials",
                    line_number=line_num,
                    code_snippet="[REDACTED FOR SECURITY]",
                    recommendation="Move secrets to environment variables or secure configuration files",
                    confidence=0.7
                )
                self.findings.append(finding)
    
    def _check_auth_issues(self, content: str, lines: List[str]):
        """Check for authentication and authorization issues"""
        for pattern in self.auth_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                
                finding = SecurityFinding(
                    severity="medium",
                    category="auth",
                    title="Potential Authentication Issue",
                    description="Code contains weak authentication or authorization patterns",
                    line_number=line_num,
                    code_snippet=code_snippet.strip(),
                    recommendation="Implement proper authentication mechanisms and avoid hardcoded credentials",
                    confidence=0.6
                )
                self.findings.append(finding)
    
    def _check_input_validation(self, content: str, lines: List[str]):
        """Check for input validation issues"""
        # Look for dangerous functions with user input
        dangerous_patterns = [
            r'os\.system\s*\([^)]*(?:input|request|argv)',
            r'subprocess\.(?:call|run|Popen)\s*\([^)]*(?:input|request|argv)',
            r'eval\s*\([^)]*(?:input|request|argv)',
            r'exec\s*\([^)]*(?:input|request|argv)',
            r'open\s*\([^)]*(?:input|request|argv)',
        ]
        
        for pattern in dangerous_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                
                finding = SecurityFinding(
                    severity="high",
                    category="input_validation",
                    title="Dangerous Function with User Input",
                    description="Code uses potentially dangerous functions with user-controlled input",
                    line_number=line_num,
                    code_snippet=code_snippet.strip(),
                    recommendation="Validate and sanitize all user input before using in system functions",
                    confidence=0.8
                )
                self.findings.append(finding)
    
    def _check_path_traversal(self, content: str, lines: List[str]):
        """Check for path traversal vulnerabilities"""
        path_patterns = [
            r'open\s*\([^)]*\.\./.*["\']',
            r'file_path.*?=.*?request',
            r'os\.path\.join.*?request',
        ]
        
        for pattern in path_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                
                finding = SecurityFinding(
                    severity="medium",
                    category="path_traversal",
                    title="Potential Path Traversal",
                    description="Code may be vulnerable to path traversal attacks",
                    line_number=line_num,
                    code_snippet=code_snippet.strip(),
                    recommendation="Validate file paths and use os.path.abspath() with proper restrictions",
                    confidence=0.6
                )
                self.findings.append(finding)
    
    def generate_report(self, findings: List[SecurityFinding]) -> Dict[str, Any]:
        """Generate a comprehensive security report"""
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        category_counts = {}
        
        for finding in findings:
            severity_counts[finding.severity] += 1
            category_counts[finding.category] = category_counts.get(finding.category, 0) + 1
        
        # Calculate overall risk score (0-100)
        risk_score = (
            severity_counts["critical"] * 25 +
            severity_counts["high"] * 15 +
            severity_counts["medium"] * 8 +
            severity_counts["low"] * 3 +
            severity_counts["info"] * 1
        )
        
        risk_level = "LOW"
        if risk_score >= 50:
            risk_level = "CRITICAL"
        elif risk_score >= 30:
            risk_level = "HIGH"
        elif risk_score >= 15:
            risk_level = "MEDIUM"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_findings": len(findings),
                "risk_score": risk_score,
                "risk_level": risk_level,
                "severity_breakdown": severity_counts,
                "category_breakdown": category_counts
            },
            "findings": [asdict(finding) for finding in findings]
        }
    
    def save_to_memory(self, report: Dict[str, Any], file_path: str):
        """Save security findings to SIDEKICK memory system"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create memory entry
            memory_data = {
                "type": "security_finding",
                "file_path": file_path,
                "risk_score": report["summary"]["risk_score"],
                "risk_level": report["summary"]["risk_level"],
                "total_findings": report["summary"]["total_findings"],
                "report": report
            }
            
            cursor.execute("""
                INSERT INTO memory (actor_uuid, memory_uuid, type, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "claude-sonnet-4-session-20250829",
                f"security-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "security_finding",
                json.dumps(memory_data),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving to memory: {e}")
            return False

def main():
    """Command-line interface for security auditor"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python security_auditor.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    auditor = SecurityAuditor()
    
    print(f"🔒 SIDEKICK Security Auditor")
    print(f"📁 Analyzing: {file_path}")
    print("=" * 50)
    
    # Analyze the file
    findings = auditor.analyze_file(file_path)
    report = auditor.generate_report(findings)
    
    # Display summary
    summary = report["summary"]
    print(f"\n📊 SECURITY ANALYSIS SUMMARY")
    print(f"Risk Level: {summary['risk_level']} (Score: {summary['risk_score']})")
    print(f"Total Findings: {summary['total_findings']}")
    
    if summary['total_findings'] > 0:
        print(f"\nSeverity Breakdown:")
        for severity, count in summary['severity_breakdown'].items():
            if count > 0:
                print(f"  {severity.upper()}: {count}")
        
        print(f"\nDetailed Findings:")
        for i, finding in enumerate(findings, 1):
            print(f"\n{i}. [{finding.severity.upper()}] {finding.title}")
            print(f"   Line {finding.line_number}: {finding.description}")
            print(f"   Code: {finding.code_snippet}")
            print(f"   Fix: {finding.recommendation}")
    
    # Save to memory
    if auditor.save_to_memory(report, file_path):
        print(f"\n✅ Security findings saved to SIDEKICK memory system")
    else:
        print(f"\n❌ Failed to save to memory system")
    
    # Export JSON report
    report_path = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Full report saved to: {report_path}")

if __name__ == "__main__":
    main()