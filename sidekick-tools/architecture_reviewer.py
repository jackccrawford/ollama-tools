#!/usr/bin/env python3
"""
SIDEKICK Architecture Reviewer
Part of the Code Review Collective system
Analyzes code architecture, design patterns, and maintainability
Claude A component - coordinates with Claude B's Security Auditor
"""

import os
import ast
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class ArchitectureReviewer:
    """Architecture and design pattern analysis component"""
    
    def __init__(self, db_path: str = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"):
        self.db_path = db_path
        self.analysis_patterns = {
            "design_patterns": self._analyze_design_patterns,
            "solid_principles": self._analyze_solid_principles,
            "code_organization": self._analyze_code_organization,
            "maintainability": self._analyze_maintainability,
            "documentation": self._analyze_documentation,
            "complexity": self._analyze_complexity
        }
    
    def review_code(self, code_content: str, file_path: str = "unknown") -> Dict[str, Any]:
        """Main entry point for architecture review"""
        try:
            tree = ast.parse(code_content)
            
            analysis_results = {}
            for pattern_name, analyzer in self.analysis_patterns.items():
                analysis_results[pattern_name] = analyzer(tree, code_content, file_path)
            
            # Generate overall architecture score
            overall_score = self._calculate_overall_score(analysis_results)
            
            # Create comprehensive report
            report = {
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                "analyzer": "Architecture Reviewer (Claude A)",
                "overall_score": overall_score,
                "analysis": analysis_results,
                "recommendations": self._generate_recommendations(analysis_results),
                "summary": self._generate_summary(analysis_results, overall_score)
            }
            
            # Store in SIDEKICK memory
            self._store_findings(report)
            
            return report
            
        except SyntaxError as e:
            return {
                "file_path": file_path,
                "error": f"Syntax error in code: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "analyzer": "Architecture Reviewer (Claude A)"
            }
    
    def _analyze_design_patterns(self, tree: ast.AST, code: str, file_path: str) -> Dict[str, Any]:
        """Detect and analyze design patterns"""
        patterns_found = []
        issues = []
        
        # Analyze class structure for common patterns
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        # Singleton pattern detection
        for cls in classes:
            methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)]
            method_names = [m.name for m in methods]
            
            if '__new__' in method_names or 'getInstance' in method_names:
                patterns_found.append({
                    "pattern": "Singleton",
                    "class": cls.name,
                    "confidence": 0.7,
                    "line": cls.lineno
                })
        
        # Factory pattern detection
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and 'create' in node.name.lower():
                patterns_found.append({
                    "pattern": "Factory",
                    "function": node.name,
                    "confidence": 0.6,
                    "line": node.lineno
                })
        
        # Observer pattern detection (event handlers, callbacks)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if any(keyword in node.name.lower() for keyword in ['notify', 'observe', 'listen', 'callback']):
                    patterns_found.append({
                        "pattern": "Observer",
                        "function": node.name,
                        "confidence": 0.5,
                        "line": node.lineno
                    })
        
        # Anti-pattern detection
        if len(classes) == 1 and len(classes[0].body) > 20:
            issues.append({
                "issue": "God Object",
                "description": f"Class {classes[0].name} has too many responsibilities",
                "severity": "medium",
                "line": classes[0].lineno
            })
        
        return {
            "patterns_found": patterns_found,
            "issues": issues,
            "score": max(0, 10 - len(issues) * 2)  # Start at 10, deduct for issues
        }
    
    def _analyze_solid_principles(self, tree: ast.AST, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze adherence to SOLID principles"""
        violations = []
        score = 10
        
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        for cls in classes:
            methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)]
            
            # Single Responsibility Principle
            if len(methods) > 15:
                violations.append({
                    "principle": "Single Responsibility",
                    "violation": f"Class {cls.name} has {len(methods)} methods - too many responsibilities",
                    "severity": "medium",
                    "line": cls.lineno
                })
                score -= 2
            
            # Open/Closed Principle - check for excessive inheritance
            if len(cls.bases) > 2:
                violations.append({
                    "principle": "Open/Closed",
                    "violation": f"Class {cls.name} inherits from multiple classes",
                    "severity": "low",
                    "line": cls.lineno
                })
                score -= 1
            
            # Interface Segregation - check for large interfaces
            abstract_methods = 0
            for method in methods:
                if any(decorator.id == 'abstractmethod' for decorator in method.decorator_list if isinstance(decorator, ast.Name)):
                    abstract_methods += 1
            
            if abstract_methods > 10:
                violations.append({
                    "principle": "Interface Segregation",
                    "violation": f"Interface {cls.name} has {abstract_methods} abstract methods - too broad",
                    "severity": "medium",
                    "line": cls.lineno
                })
                score -= 2
        
        return {
            "violations": violations,
            "score": max(0, score),
            "principles_analyzed": ["Single Responsibility", "Open/Closed", "Interface Segregation"]
        }
    
    def _analyze_code_organization(self, tree: ast.AST, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze code organization and structure"""
        issues = []
        score = 10
        
        # Function length analysis
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        for func in functions:
            func_lines = len([node for node in ast.walk(func)])
            if func_lines > 50:
                issues.append({
                    "issue": "Long Function",
                    "description": f"Function {func.name} has {func_lines} statements - consider splitting",
                    "severity": "medium",
                    "line": func.lineno
                })
                score -= 1
        
        # Cyclomatic complexity (simplified)
        for func in functions:
            complexity = self._calculate_cyclomatic_complexity(func)
            if complexity > 10:
                issues.append({
                    "issue": "High Complexity",
                    "description": f"Function {func.name} has complexity {complexity} - consider simplifying",
                    "severity": "high",
                    "line": func.lineno
                })
                score -= 2
        
        # Import organization
        imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
        if len(imports) > 20:
            issues.append({
                "issue": "Too Many Imports",
                "description": f"File has {len(imports)} import statements - consider refactoring",
                "severity": "low",
                "line": 1
            })
            score -= 1
        
        return {
            "issues": issues,
            "score": max(0, score),
            "metrics": {
                "function_count": len(functions),
                "class_count": len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
                "import_count": len(imports)
            }
        }
    
    def _analyze_maintainability(self, tree: ast.AST, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze code maintainability factors"""
        issues = []
        score = 10
        
        # Magic numbers detection
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in [0, 1, -1] and node.value > 10:
                    issues.append({
                        "issue": "Magic Number",
                        "description": f"Magic number {node.value} found - consider using named constant",
                        "severity": "low",
                        "line": node.lineno
                    })
                    score -= 0.5
        
        # Hardcoded strings detection
        string_constants = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) > 10:
                string_constants.append(node.value)
        
        if len(string_constants) > 5:
            issues.append({
                "issue": "Hardcoded Strings",
                "description": f"Found {len(string_constants)} hardcoded strings - consider configuration",
                "severity": "medium",
                "line": 1
            })
            score -= 1
        
        # Exception handling analysis
        try_blocks = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        if len(functions) > 5 and len(try_blocks) == 0:
            issues.append({
                "issue": "No Exception Handling",
                "description": "Code lacks exception handling - consider adding try/catch blocks",
                "severity": "medium",
                "line": 1
            })
            score -= 2
        
        return {
            "issues": issues,
            "score": max(0, score),
            "maintainability_factors": {
                "exception_handling": len(try_blocks) > 0,
                "hardcoded_values": len(string_constants),
                "code_reuse": len(functions) / max(1, len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]))
            }
        }
    
    def _analyze_documentation(self, tree: ast.AST, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze code documentation quality"""
        issues = []
        score = 10
        
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        # Function documentation
        undocumented_functions = 0
        for func in functions:
            if not func.name.startswith('_'):  # Skip private methods
                docstring = ast.get_docstring(func)
                if not docstring:
                    undocumented_functions += 1
        
        if undocumented_functions > 0:
            issues.append({
                "issue": "Missing Docstrings",
                "description": f"{undocumented_functions} public functions lack documentation",
                "severity": "medium",
                "line": 1
            })
            score -= min(3, undocumented_functions)
        
        # Class documentation
        undocumented_classes = 0
        for cls in classes:
            docstring = ast.get_docstring(cls)
            if not docstring:
                undocumented_classes += 1
        
        if undocumented_classes > 0:
            issues.append({
                "issue": "Missing Class Documentation",
                "description": f"{undocumented_classes} classes lack documentation",
                "severity": "medium",
                "line": 1
            })
            score -= min(2, undocumented_classes)
        
        return {
            "issues": issues,
            "score": max(0, score),
            "documentation_coverage": {
                "functions": (len(functions) - undocumented_functions) / max(1, len(functions)),
                "classes": (len(classes) - undocumented_classes) / max(1, len(classes))
            }
        }
    
    def _analyze_complexity(self, tree: ast.AST, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze code complexity metrics"""
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        complexity_scores = []
        for func in functions:
            complexity = self._calculate_cyclomatic_complexity(func)
            complexity_scores.append({
                "function": func.name,
                "complexity": complexity,
                "line": func.lineno
            })
        
        avg_complexity = sum(s["complexity"] for s in complexity_scores) / max(1, len(complexity_scores))
        max_complexity = max((s["complexity"] for s in complexity_scores), default=0)
        
        return {
            "average_complexity": round(avg_complexity, 2),
            "max_complexity": max_complexity,
            "function_complexities": complexity_scores,
            "score": max(0, 10 - int(avg_complexity))
        }
    
    def _calculate_cyclomatic_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_overall_score(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate weighted overall architecture score"""
        weights = {
            "design_patterns": 0.2,
            "solid_principles": 0.25,
            "code_organization": 0.2,
            "maintainability": 0.15,
            "documentation": 0.1,
            "complexity": 0.1
        }
        
        total_score = 0
        for category, weight in weights.items():
            if category in analysis_results and "score" in analysis_results[category]:
                total_score += analysis_results[category]["score"] * weight
        
        return round(total_score, 2)
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Design patterns recommendations
        if "design_patterns" in analysis_results:
            issues = analysis_results["design_patterns"].get("issues", [])
            for issue in issues:
                if issue["issue"] == "God Object":
                    recommendations.append("Consider splitting large classes using Single Responsibility Principle")
        
        # SOLID principles recommendations
        if "solid_principles" in analysis_results:
            violations = analysis_results["solid_principles"].get("violations", [])
            for violation in violations[:3]:  # Top 3 violations
                recommendations.append(f"SOLID: {violation['violation']}")
        
        # Code organization recommendations
        if "code_organization" in analysis_results:
            issues = analysis_results["code_organization"].get("issues", [])
            for issue in issues[:2]:  # Top 2 issues
                recommendations.append(f"Organization: {issue['description']}")
        
        # Maintainability recommendations
        if "maintainability" in analysis_results:
            issues = analysis_results["maintainability"].get("issues", [])
            for issue in issues[:2]:  # Top 2 issues
                recommendations.append(f"Maintainability: {issue['description']}")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _generate_summary(self, analysis_results: Dict[str, Any], overall_score: float) -> str:
        """Generate human-readable summary"""
        if overall_score >= 8.0:
            quality = "Excellent"
        elif overall_score >= 6.0:
            quality = "Good"
        elif overall_score >= 4.0:
            quality = "Fair"
        else:
            quality = "Needs Improvement"
        
        total_issues = sum(
            len(analysis_results.get(category, {}).get("issues", []))
            for category in analysis_results
        )
        
        return f"Architecture Quality: {quality} (Score: {overall_score}/10). Found {total_issues} total issues across all categories."
    
    def _store_findings(self, report: Dict[str, Any]):
        """Store architecture findings in SIDEKICK memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create memory entry
            import uuid
            memory_uuid = str(uuid.uuid4()).upper()
            actor_uuid = "claude-sonnet-4-session-20250829"  # Claude A
            
            payload = {
                "type": "architecture_finding",
                "file_path": report["file_path"],
                "overall_score": report["overall_score"],
                "summary": report["summary"],
                "recommendations": report["recommendations"],
                "full_report": report,
                "analyzer": "Architecture Reviewer (Claude A)",
                "context": "Code Review Collective System"
            }
            
            cursor.execute("""
                INSERT INTO memory (memory_uuid, actor_uuid, payload)
                VALUES (?, ?, ?)
            """, (memory_uuid, actor_uuid, json.dumps(payload)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Failed to store findings: {e}")

def main():
    """Demo the Architecture Reviewer"""
    reviewer = ArchitectureReviewer()
    
    print("🏗️  SIDEKICK Architecture Reviewer")
    print("=" * 50)
    
    # Test with sample code
    sample_code = '''
import os
import sys

class DataProcessor:
    def __init__(self):
        self.data = []
        self.processed = False
        
    def load_data(self, filename):
        """Load data from file"""
        with open(filename, 'r') as f:
            self.data = f.readlines()
    
    def process_data(self):
        """Process the loaded data"""
        if not self.data:
            return
            
        processed_data = []
        for line in self.data:
            if len(line) > 10:
                processed_data.append(line.strip().upper())
        
        self.data = processed_data
        self.processed = True
    
    def save_data(self, filename):
        if not self.processed:
            print("Data not processed yet!")
            return
            
        with open(filename, 'w') as f:
            for line in self.data:
                f.write(line + "\\n")
'''
    
    report = reviewer.review_code(sample_code, "sample_code.py")
    
    print(f"\n📊 Analysis Results:")
    print(f"Overall Score: {report['overall_score']}/10")
    print(f"Summary: {report['summary']}")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print(f"\n✅ Architecture review complete!")
    print(f"Results stored in SIDEKICK memory with type 'architecture_finding'")

if __name__ == "__main__":
    main()