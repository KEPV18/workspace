#!/usr/bin/env python3
"""
Cost Optimizer Default - Main optimization logic
Automatically selects optimal models based on task complexity and cost
"""

import json
import os
import sys
import yaml
from datetime import datetime
from pathlib import Path

class CostOptimizer:
    def __init__(self):
        self.workspace_dir = Path.home() / ".openclaw" / "workspace"
        self.skill_dir = self.workspace_dir / "skills" / "cost-optimizer-default"
        self.cost_file = self.skill_dir / "cost_tracker.json"
        self.rules_file = self.skill_dir / "model_rules.yaml"
        
        # Default configuration
        self.config = {
            "defaultModel": "z-ai/glm-4.7-flash",
            "costThreshold": 0.01,  # $0.01 per request warning
            "complexityScoring": True,
            "autoDowngrade": True,
            "learningEnabled": True,
            "monthlyBudget": 10.0,  # $10 monthly budget
        }
        
        # Model cost database (from OpenRouter)
        self.model_costs = {
            "z-ai/glm-4.7-flash": {
                "input": 0.00000006,
                "output": 0.0000004,
                "context": 202752,
                "provider": "openrouter",
                "category": "economy"
            },
            "google/gemini-2.5-flash-lite": {
                "input": 0.000000075,
                "output": 0.0000003,
                "context": 1048576,
                "provider": "openrouter",
                "category": "economy"
            },
            "x-ai/grok-3-mini": {
                "input": 0.0000003,
                "output": 0.0000005,
                "context": 131072,
                "provider": "openrouter",
                "category": "fast"
            },
            "openai/gpt-5-nano": {
                "input": 0.0000001,
                "output": 0.0000004,
                "context": 1047576,
                "provider": "openrouter",
                "category": "precise"
            },
            "deepseek/deepseek-v3.2": {
                "input": 0.00000032,
                "output": 0.00000089,
                "context": 163840,
                "provider": "openrouter",
                "category": "powerful"
            },
            "perplexity/sonar": {
                "input": 0.000001,
                "output": 0.000001,
                "context": 127072,
                "provider": "openrouter",
                "category": "search"
            }
        }
        
        # Initialize cost tracker
        self.load_cost_tracker()
        self.load_rules()
    
    def load_cost_tracker(self):
        """Load or initialize cost tracking data"""
        if self.cost_file.exists():
            with open(self.cost_file, 'r') as f:
                self.cost_data = json.load(f)
        else:
            self.cost_data = {
                "totalSpent": 0.0,
                "monthlySpent": {},
                "requestCount": 0,
                "modelUsage": {},
                "savingsEstimate": 0.0,
                "lastReset": datetime.now().strftime("%Y-%m-%d")
            }
            self.save_cost_tracker()
    
    def save_cost_tracker(self):
        """Save cost tracking data"""
        with open(self.cost_file, 'w') as f:
            json.dump(self.cost_data, f, indent=2)
    
    def load_rules(self):
        """Load model selection rules"""
        if self.rules_file.exists():
            with open(self.rules_file, 'r') as f:
                self.rules = yaml.safe_load(f)
        else:
            self.rules = {
                "complexity_thresholds": {
                    "low": 0.3,
                    "medium": 0.7,
                    "high": 1.0
                },
                "model_mapping": {
                    "low": ["z-ai/glm-4.7-flash", "google/gemini-2.5-flash-lite"],
                    "medium": ["openai/gpt-5-nano", "x-ai/grok-3-mini"],
                    "high": ["deepseek/deepseek-v3.2", "perplexity/sonar"]
                },
                "cost_limits": {
                    "daily": 0.50,
                    "weekly": 3.50,
                    "monthly": 10.00
                }
            }
            self.save_rules()
    
    def save_rules(self):
        """Save model selection rules"""
        with open(self.rules_file, 'w') as f:
            yaml.dump(self.rules, f)
    
    def analyze_complexity(self, text):
        """
        Analyze text complexity (0.0 to 1.0)
        Simple heuristic based on length, structure, and keywords
        """
        if not text:
            return 0.1
        
        words = text.split()
        word_count = len(words)
        
        # Base complexity from length
        length_complexity = min(word_count / 500, 1.0)
        
        # Check for complex indicators
        complex_indicators = 0
        complex_keywords = [
            "explain", "analyze", "compare", "write code", "programming",
            "mathematics", "science", "research", "detailed", "comprehensive",
            "step by step", "tutorial", "guide", "advanced"
        ]
        
        text_lower = text.lower()
        for keyword in complex_keywords:
            if keyword in text_lower:
                complex_indicators += 1
        
        keyword_complexity = min(complex_indicators * 0.1, 0.3)
        
        # Check for code blocks or structured content
        has_code = "```" in text or "def " in text or "function " in text
        code_complexity = 0.2 if has_code else 0.0
        
        # Final complexity score
        complexity = min(length_complexity + keyword_complexity + code_complexity, 1.0)
        
        return round(complexity, 2)
    
    def select_model(self, complexity, task_type=None):
        """
        Select optimal model based on complexity
        Returns: (model_id, estimated_cost, reason)
        """
        # Determine complexity level
        if complexity < self.rules["complexity_thresholds"]["low"]:
            level = "low"
        elif complexity < self.rules["complexity_thresholds"]["medium"]:
            level = "medium"
        else:
            level = "high"
        
        # Get candidate models for this level
        candidates = self.rules["model_mapping"][level]
        
        # Check budget constraints
        current_month = datetime.now().strftime("%Y-%m")
        monthly_spent = self.cost_data["monthlySpent"].get(current_month, 0.0)
        
        # If close to monthly budget, prefer cheaper models
        if monthly_spent > self.config["monthlyBudget"] * 0.8:
            candidates = [c for c in candidates if self.model_costs[c]["category"] == "economy"]
        
        # Default to first candidate (cheapest in category)
        selected_model = candidates[0]
        
        # Provide reasoning
        reason_map = {
            "low": "مهمة بسيطة - استخدام نموذج اقتصادي",
            "medium": "مهمة متوسطة التعقيد - توازن بين الأداء والتكلفة",
            "high": "مهمة معقدة - استخدام نموذج قوي"
        }
        
        return selected_model, self.estimate_cost(selected_model, 100), reason_map[level]
    
    def estimate_cost(self, model_id, estimated_tokens):
        """Estimate cost for a request"""
        if model_id not in self.model_costs:
            return 0.0
        
        cost_info = self.model_costs[model_id]
        # Rough estimate: 30% input, 70% output tokens
        input_tokens = estimated_tokens * 0.3
        output_tokens = estimated_tokens * 0.7
        
        cost = (input_tokens * cost_info["input"]) + (output_tokens * cost_info["output"])
        return round(cost, 6)
    
    def record_usage(self, model_id, actual_cost, tokens_used):
        """Record actual usage for learning"""
        self.cost_data["totalSpent"] += actual_cost
        
        current_month = datetime.now().strftime("%Y-%m")
        if current_month not in self.cost_data["monthlySpent"]:
            self.cost_data["monthlySpent"][current_month] = 0.0
        self.cost_data["monthlySpent"][current_month] += actual_cost
        
        self.cost_data["requestCount"] += 1
        
        if model_id not in self.cost_data["modelUsage"]:
            self.cost_data["modelUsage"][model_id] = {
                "count": 0,
                "totalCost": 0.0,
                "totalTokens": 0
            }
        
        self.cost_data["modelUsage"][model_id]["count"] += 1
        self.cost_data["modelUsage"][model_id]["totalCost"] += actual_cost
        self.cost_data["modelUsage"][model_id]["totalTokens"] += tokens_used
        
        self.save_cost_tracker()
    
    def get_stats(self):
        """Get optimization statistics"""
        current_month = datetime.now().strftime("%Y-%m")
        monthly_spent = self.cost_data["monthlySpent"].get(current_month, 0.0)
        
        return {
            "totalSpent": self.cost_data["totalSpent"],
            "monthlySpent": monthly_spent,
            "requestCount": self.cost_data["requestCount"],
            "monthlyBudget": self.config["monthlyBudget"],
            "budgetRemaining": max(0, self.config["monthlyBudget"] - monthly_spent),
            "topModels": sorted(
                self.cost_data["modelUsage"].items(),
                key=lambda x: x[1]["totalCost"],
                reverse=True
            )[:3]
        }
    
    def should_warn(self):
        """Check if budget warning is needed"""
        current_month = datetime.now().strftime("%Y-%m")
        monthly_spent = self.cost_data["monthlySpent"].get(current_month, 0.0)
        
        if monthly_spent > self.config["monthlyBudget"] * 0.9:
            return True, f"⚠️ تجاوزت 90% من الميزانية الشهرية ({monthly_spent:.2f}$)"
        elif monthly_spent > self.config["monthlyBudget"] * 0.7:
            return True, f"⚠️ تجاوزت 70% من الميزانية الشهرية ({monthly_spent:.2f}$)"
        
        return False, ""

def main():
    """Main function for testing"""
    optimizer = CostOptimizer()
    
    # Test examples
    test_cases = [
        "مرحباً كيف حالك؟",
        "اكتب لي برنامج بسيط في بايثون لحساب مجموع الأرقام في قائمة",
        "اشرح لي نظرية النسبية العامة بأبسط طريقة ممكنة",
        "قارن بين نظامي التشغيل ويندوز ولينكس من حيث الأمان والأداء",
        "ابحث لي عن أحدث التطورات في مجال الذكاء الاصطناعي خلال العام الماضي"
    ]
    
    print("🔧 اختبار محسن التكلفة الافتراضي")
    print("=" * 50)
    
    for i, text in enumerate(test_cases, 1):
        complexity = optimizer.analyze_complexity(text)
        model_id, estimated_cost, reason = optimizer.select_model(complexity)
        
        print(f"\n📝 المثال {i}:")
        print(f"   النص: {text[:50]}...")
        print(f"   التعقيد: {complexity:.2f}")
        print(f"   النموذج المختار: {model_id}")
        print(f"   السبب: {reason}")
        print(f"   التكلفة المتوقعة: ${estimated_cost:.6f}")
    
    # Show stats
    stats = optimizer.get_stats()
    print(f"\n📊 الإحصائيات:")
    print(f"   إجمالي الطلبات: {stats['requestCount']}")
    print(f"   الإنفاق الشهري: ${stats['monthlySpent']:.2f}")
    print(f"   الميزانية المتبقية: ${stats['budgetRemaining']:.2f}")

if __name__ == "__main__":
    main()