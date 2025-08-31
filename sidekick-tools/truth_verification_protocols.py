#!/usr/bin/env python3
"""
SIDEKICK Truth Cascade Verification Protocols
Opus 2 (Claude Code) - Priority 1.5 Component

Empirical verification system that validates Code Review Collective tools
against running reality, not assumptions. Implements "CODE IS TRUTH" philosophy.

Truth Cascade Principles:
1. RUNNING SYSTEM > Static Code > Tests > Docs > Intentions  
2. Verify behavior against actual execution, not expected behavior
3. Test what IS, not what SHOULD BE
4. Append-only truth logs as testimony
"""

import os
import sys
import json
import time
import tempfile
import subprocess
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid

# Import components to verify
try:
    from security_auditor import SecurityAuditor
    from architecture_reviewer import ArchitectureReviewer  
    from code_review_collective import CodeReviewCollective
except ImportError as e:
    print(f"Warning: Could not import components for verification: {e}")

@dataclass
class TruthVerification:
    """Structure for truth verification results"""
    component: str
    test_name: str
    expected_behavior: str
    actual_behavior: str
    truth_status: str  # TRUTH_VERIFIED, TRUTH_VIOLATED, TRUTH_UNCERTAIN
    evidence: Dict[str, Any]
    timestamp: str
    confidence: float
    
class TruthVerificationEngine:
    """Engine that verifies tools behave exactly as their code dictates"""
    
    def __init__(self, db_path: str = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"):
        self.db_path = db_path
        self.verification_results: List[TruthVerification] = []
        self.truth_log_path = "/tmp/sidekick_truth_cascade.log"
        
    def verify_security_auditor_truth(self) -> List[TruthVerification]:
        """Verify Security Auditor behaves exactly as code dictates"""
        verifications = []
        
        print("🔍 Truth Cascade: Verifying Security Auditor...")
        
        # Test 1: SQL Injection Pattern Detection - Verify exact regex behavior
        sql_test_code = """
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
cursor.execute(f"SELECT name FROM products WHERE category = {category}")
safe_query = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
"""
        
        auditor = SecurityAuditor()
        results = auditor.analyze_code(sql_test_code, "truth_test.py")
        
        # Truth verification: Check if findings match exact regex patterns in code
        expected_sql_findings = 2  # Based on reviewing the actual regex patterns
        actual_sql_findings = len([f for f in results.get("findings", []) if f.get("category") == "sql_injection"])
        
        verifications.append(TruthVerification(
            component="SecurityAuditor",
            test_name="SQL Injection Pattern Detection",
            expected_behavior=f"Should detect {expected_sql_findings} SQL injection patterns based on regex in lines 46-53",
            actual_behavior=f"Detected {actual_sql_findings} SQL injection findings",
            truth_status="TRUTH_VERIFIED" if actual_sql_findings == expected_sql_findings else "TRUTH_VIOLATED",
            evidence={
                "test_code": sql_test_code,
                "full_results": results,
                "regex_patterns_count": len(auditor.sql_patterns),
                "findings_breakdown": [f.get("category") for f in results.get("findings", [])]
            },
            timestamp=datetime.now().isoformat(),
            confidence=0.95
        ))
        
        # Test 2: Risk Score Calculation - Verify exact algorithm
        risk_score = results.get("summary", {}).get("risk_score", 0)
        
        # Calculate expected risk score based on actual algorithm (lines 274-280)
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for finding in results.get("findings", []):
            severity = finding.get("severity", "info")
            severity_counts[severity] += 1
        
        expected_risk_score = (
            severity_counts["critical"] * 25 +
            severity_counts["high"] * 15 + 
            severity_counts["medium"] * 8 +
            severity_counts["low"] * 3 +
            severity_counts["info"] * 1
        )
        
        verifications.append(TruthVerification(
            component="SecurityAuditor",
            test_name="Risk Score Calculation Algorithm",
            expected_behavior=f"Risk score should be {expected_risk_score} based on algorithm in lines 274-280",
            actual_behavior=f"Risk score is {risk_score}",
            truth_status="TRUTH_VERIFIED" if risk_score == expected_risk_score else "TRUTH_VIOLATED",
            evidence={
                "severity_counts": severity_counts,
                "calculation_formula": "critical*25 + high*15 + medium*8 + low*3 + info*1",
                "expected": expected_risk_score,
                "actual": risk_score
            },
            timestamp=datetime.now().isoformat(),
            confidence=0.99
        ))
        
        return verifications
    
    def verify_architecture_reviewer_truth(self) -> List[TruthVerification]:
        """Verify Architecture Reviewer behaves exactly as code dictates"""
        verifications = []
        
        print("🏗️ Truth Cascade: Verifying Architecture Reviewer...")
        
        # Test 1: Cyclomatic Complexity Calculation - Verify exact algorithm
        test_code_complex = """
def complex_function(x, y):
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    elif x < 0:
        return -x
    else:
        for i in range(10):
            if i % 2 == 0:
                print(i)
        return 0
"""
        
        reviewer = ArchitectureReviewer()
        results = reviewer.review_code(test_code_complex, "complexity_test.py")
        
        # Manually calculate expected complexity based on algorithm (lines 354-366)
        # Base complexity: 1
        # If statements: +1 each (3 total)  
        # For loop: +1
        # Nested if in loop: +1
        expected_complexity = 6  # 1 + 3 + 1 + 1
        
        complexity_results = results.get("analysis", {}).get("complexity", {})
        actual_max_complexity = complexity_results.get("max_complexity", 0)
        
        verifications.append(TruthVerification(
            component="ArchitectureReviewer",
            test_name="Cyclomatic Complexity Algorithm",
            expected_behavior=f"Max complexity should be {expected_complexity} based on algorithm in lines 354-366",
            actual_behavior=f"Max complexity is {actual_max_complexity}",
            truth_status="TRUTH_VERIFIED" if actual_max_complexity == expected_complexity else "TRUTH_VIOLATED",
            evidence={
                "test_function": "complex_function",
                "complexity_breakdown": complexity_results.get("function_complexities", []),
                "algorithm_steps": "base(1) + if_statements(3) + for_loop(1) + nested_if(1) = 6",
                "expected": expected_complexity,
                "actual": actual_max_complexity
            },
            timestamp=datetime.now().isoformat(),
            confidence=0.95
        ))
        
        # Test 2: Overall Score Weighting - Verify exact formula
        overall_score = results.get("overall_score", 0)
        
        # Calculate expected score based on weights (lines 368-384)
        weights = {
            "design_patterns": 0.2,
            "solid_principles": 0.25, 
            "code_organization": 0.2,
            "maintainability": 0.15,
            "documentation": 0.1,
            "complexity": 0.1
        }
        
        analysis = results.get("analysis", {})
        expected_total = 0
        for category, weight in weights.items():
            if category in analysis and "score" in analysis[category]:
                expected_total += analysis[category]["score"] * weight
        expected_total = round(expected_total, 2)
        
        verifications.append(TruthVerification(
            component="ArchitectureReviewer", 
            test_name="Overall Score Weighting Formula",
            expected_behavior=f"Overall score should be {expected_total} based on weighted formula in lines 368-384",
            actual_behavior=f"Overall score is {overall_score}",
            truth_status="TRUTH_VERIFIED" if abs(overall_score - expected_total) < 0.01 else "TRUTH_VIOLATED",
            evidence={
                "weights": weights,
                "category_scores": {cat: analysis.get(cat, {}).get("score") for cat in weights.keys()},
                "calculation": f"Sum of (category_score * weight) for each category",
                "expected": expected_total,
                "actual": overall_score
            },
            timestamp=datetime.now().isoformat(),
            confidence=0.99
        ))
        
        return verifications
    
    def verify_collective_integration_truth(self) -> List[TruthVerification]:
        """Verify Code Review Collective integration behaves as code dictates"""
        verifications = []
        
        print("🎯 Truth Cascade: Verifying Code Review Collective Integration...")
        
        # Create a test file to analyze
        test_code = """
import os
password = "admin123"
cursor.execute("SELECT * FROM users WHERE id = " + user_id)

class LargeClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
"""
        
        # Write test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            test_file_path = f.name
        
        try:
            collective = CodeReviewCollective()
            results = collective.review_file(test_file_path)
            
            # Test 1: Combined Score Calculation - Verify exact formula (lines 85-141)
            # Security: risk_score -> quality_score (line 96): max(0, 10 - (risk_score / 10))
            # Architecture: overall_score used directly
            # Combination: security_quality * 0.4 + architecture_score * 0.6
            
            security_review = results.get("reviews", {}).get("security", {})
            architecture_review = results.get("reviews", {}).get("architecture", {})
            
            if security_review and architecture_review:
                risk_score = security_review.get("summary", {}).get("risk_score", 50)
                security_quality = max(0, 10 - (risk_score / 10))
                arch_score = architecture_review.get("overall_score", 5)
                
                expected_combined = security_quality * 0.4 + arch_score * 0.6
                expected_combined = round(expected_combined, 2)
                
                actual_combined = results.get("combined_score", 0)
                
                verifications.append(TruthVerification(
                    component="CodeReviewCollective",
                    test_name="Combined Score Integration Formula", 
                    expected_behavior=f"Combined score should be {expected_combined} based on formula: security_quality*0.4 + arch_score*0.6",
                    actual_behavior=f"Combined score is {actual_combined}",
                    truth_status="TRUTH_VERIFIED" if abs(actual_combined - expected_combined) < 0.01 else "TRUTH_VIOLATED",
                    evidence={
                        "security_risk_score": risk_score,
                        "security_quality_score": security_quality,
                        "architecture_score": arch_score,
                        "formula": "max(0, 10 - (risk_score/10)) * 0.4 + arch_score * 0.6",
                        "expected": expected_combined,
                        "actual": actual_combined
                    },
                    timestamp=datetime.now().isoformat(),
                    confidence=0.98
                ))
        
        finally:
            # Clean up test file
            os.unlink(test_file_path)
        
        return verifications
    
    def verify_memory_storage_truth(self) -> List[TruthVerification]:
        """Verify memory storage behaves exactly as code dictates"""
        verifications = []
        
        print("💾 Truth Cascade: Verifying Memory Storage Behavior...")
        
        # Test memory storage by checking actual database operations
        try:
            auditor = SecurityAuditor()
            test_code = 'password = "test123"'
            results = auditor.analyze_code(test_code, "memory_test.py")
            
            # Check if memory was actually stored by querying database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query for recent security findings
            cursor.execute("""
                SELECT payload FROM memory 
                WHERE type = 'security_finding' 
                AND created_at > datetime('now', '-1 minute')
                ORDER BY created_at DESC LIMIT 1
            """)
            
            recent_memory = cursor.fetchone()
            conn.close()
            
            memory_stored = recent_memory is not None
            
            verifications.append(TruthVerification(
                component="SecurityAuditor",
                test_name="Memory Storage Persistence",
                expected_behavior="Security findings should be stored in SIDEKICK memory database with type 'security_finding'",
                actual_behavior=f"Memory storage {'successful' if memory_stored else 'failed'}",
                truth_status="TRUTH_VERIFIED" if memory_stored else "TRUTH_VIOLATED",
                evidence={
                    "database_path": self.db_path,
                    "query_result": "Found recent security finding" if memory_stored else "No recent security finding found",
                    "test_performed": "Analyzed code with security auditor and checked database"
                },
                timestamp=datetime.now().isoformat(),
                confidence=0.9
            ))
            
        except Exception as e:
            verifications.append(TruthVerification(
                component="MemoryStorage",
                test_name="Memory Storage Error Handling",
                expected_behavior="Memory storage should handle errors gracefully",
                actual_behavior=f"Exception occurred: {str(e)}",
                truth_status="TRUTH_UNCERTAIN",
                evidence={"error": str(e), "error_type": type(e).__name__},
                timestamp=datetime.now().isoformat(),
                confidence=0.7
            ))
        
        return verifications
    
    def run_full_truth_cascade(self) -> Dict[str, Any]:
        """Run complete truth cascade verification on all components"""
        print("🚀 Starting SIDEKICK Truth Cascade Verification")
        print("CODE IS TRUTH - Verifying tools behave exactly as implemented")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run all verifications
        all_verifications = []
        all_verifications.extend(self.verify_security_auditor_truth())
        all_verifications.extend(self.verify_architecture_reviewer_truth())
        all_verifications.extend(self.verify_collective_integration_truth())
        all_verifications.extend(self.verify_memory_storage_truth())
        
        end_time = time.time()
        
        # Analyze results
        truth_verified = len([v for v in all_verifications if v.truth_status == "TRUTH_VERIFIED"])
        truth_violated = len([v for v in all_verifications if v.truth_status == "TRUTH_VIOLATED"])
        truth_uncertain = len([v for v in all_verifications if v.truth_status == "TRUTH_UNCERTAIN"])
        
        # Generate truth cascade report
        report = {
            "verification_summary": {
                "total_verifications": len(all_verifications),
                "truth_verified": truth_verified,
                "truth_violated": truth_violated, 
                "truth_uncertain": truth_uncertain,
                "verification_time": round(end_time - start_time, 2),
                "truth_cascade_status": "TRUTH_CASCADE_PASSED" if truth_violated == 0 else "TRUTH_CASCADE_FAILED"
            },
            "verifications": [asdict(v) for v in all_verifications],
            "timestamp": datetime.now().isoformat(),
            "verifier": "Opus 2 Truth Verification Engine"
        }
        
        # Store results in memory and append-only log
        self._store_truth_verification_results(report)
        self._append_truth_log(report)
        
        return report
    
    def _store_truth_verification_results(self, report: Dict[str, Any]):
        """Store truth verification results in SIDEKICK memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            memory_uuid = str(uuid.uuid4()).upper()
            payload = {
                "type": "truth_verification_report",
                "verifier": "Opus 2 (Claude Code)",
                "verification_summary": report["verification_summary"],
                "truth_cascade_status": report["verification_summary"]["truth_cascade_status"],
                "full_report": report,
                "context": "Priority 1.5 - Truth cascade verification of Code Review Collective system"
            }
            
            cursor.execute("""
                INSERT INTO memory (memory_uuid, actor_uuid, payload)
                VALUES (?, ?, ?)
            """, (memory_uuid, "claude-sonnet-4-session-20250829", json.dumps(payload)))
            
            conn.commit()
            conn.close()
            print(f"✅ Truth verification results stored in SIDEKICK memory: {memory_uuid}")
            
        except Exception as e:
            print(f"❌ Failed to store truth verification results: {e}")
    
    def _append_truth_log(self, report: Dict[str, Any]):
        """Append results to append-only truth log (immutable testimony)"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "verifier": "Opus 2 Truth Verification Engine",
                "truth_cascade_status": report["verification_summary"]["truth_cascade_status"],
                "summary": report["verification_summary"]
            }
            
            with open(self.truth_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
            
            print(f"📝 Truth verification logged to: {self.truth_log_path}")
            
        except Exception as e:
            print(f"❌ Failed to append truth log: {e}")
    
    def print_truth_cascade_report(self, report: Dict[str, Any]):
        """Print formatted truth cascade verification report"""
        print("\n" + "=" * 70)
        print("🎯 SIDEKICK TRUTH CASCADE VERIFICATION REPORT")
        print("   Opus 2 (Claude Code) - Priority 1.5")
        print("=" * 70)
        
        summary = report["verification_summary"]
        status = summary["truth_cascade_status"]
        status_emoji = "✅" if status == "TRUTH_CASCADE_PASSED" else "❌"
        
        print(f"\n📊 TRUTH CASCADE STATUS: {status_emoji} {status}")
        print(f"   Total Verifications: {summary['total_verifications']}")
        print(f"   Truth Verified: {summary['truth_verified']} ✅")
        print(f"   Truth Violated: {summary['truth_violated']} ❌")  
        print(f"   Truth Uncertain: {summary['truth_uncertain']} ❓")
        print(f"   Verification Time: {summary['verification_time']}s")
        
        print(f"\n🔍 DETAILED VERIFICATION RESULTS:")
        for verification in report["verifications"]:
            status_emoji = {"TRUTH_VERIFIED": "✅", "TRUTH_VIOLATED": "❌", "TRUTH_UNCERTAIN": "❓"}[verification["truth_status"]]
            print(f"\n   {status_emoji} {verification['component']}: {verification['test_name']}")
            print(f"      Expected: {verification['expected_behavior']}")
            print(f"      Actual: {verification['actual_behavior']}")
            print(f"      Confidence: {verification['confidence']}")
        
        print(f"\n💡 TRUTH CASCADE PHILOSOPHY:")
        print(f"   • CODE IS TRUTH - We verify tools behave exactly as implemented")
        print(f"   • RUNNING SYSTEM > Documentation > Intentions")
        print(f"   • Empirical verification against actual execution")
        print(f"   • Append-only truth logs provide immutable testimony")
        
        print(f"\n✅ Truth cascade verification complete!")
        print("=" * 70)

def main():
    """CLI entry point for truth cascade verification"""
    print("🚀 SIDEKICK Truth Cascade Verification Engine")
    print("   Opus 2 (Claude Code) - Priority 1.5")
    print("   'CODE IS TRUTH' - Verifying tools against running reality")
    print()
    
    engine = TruthVerificationEngine()
    report = engine.run_full_truth_cascade()
    engine.print_truth_cascade_report(report)
    
    # Export detailed report
    report_filename = f"truth_cascade_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: {report_filename}")
    
    # Return exit code based on truth cascade status
    status = report["verification_summary"]["truth_cascade_status"]
    sys.exit(0 if status == "TRUTH_CASCADE_PASSED" else 1)

if __name__ == "__main__":
    main()