#!/usr/bin/env python3
"""
OpenRouter Task Orchestrator
Intelligent task splitting and model selection system
"""

import json
import yaml
import sys
import os
import re
import time
import random
import subprocess
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Paths
CONFIG_PATH = Path.home() / ".openclaw" / "workspace" / "skills" / "orchestrator" / "config.yaml"
DB_PATH = Path.home() / ".openclaw" / "workspace" / "skills" / "orchestrator" / "task_db.json"
LOG_DIR = Path.home() / ".openclaw" / "workspace" / "logs"
MEMORY_FILE = Path.home() / ".openclaw" / "memory" / "MEMORY.md"

class TaskOrchestrator:
    def __init__(self):
        self.config = self.load_config()
        self.db = self.load_db()
        self.models = self.config["models"]["fallbacks"] + [self.config["models"]["primary"]]
        
    def load_config(self) -> Dict:
        """Load configuration from YAML file"""
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_db(self) -> Dict:
        """Load performance database"""
        if DB_PATH.exists():
            with open(DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "performance": {},
            "task_history": [],
            "model_stats": {},
            "learning_config": self.config.get("learning_config", {})
        }
    
    def save_db(self):
        """Save performance database"""
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent=2, ensure_ascii=False)
    
    def classify_task(self, task: str) -> str:
        """Classify task type based on keywords"""
        task_lower = task.lower()
        task_patterns = self.config["task_patterns"]
        
        scores = {}
        for task_type, keywords in task_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in task_lower:
                    score += 1
            if score > 0:
                scores[task_type] = score
        
        if not scores:
            return "general"
        
        # Return task type with highest score
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def select_model(self, task_type: str) -> str:
        """Select the best model for a task type using learning"""
        if not self.config["orchestrator"]["use_learning"]:
            # Use initial biases
            biases = self.config["model_biases"].get(task_type, [self.config["models"]["primary"]])
            return biases[0]
        
        # Check if we have enough data for this task type
        task_perf = self.db["performance"].get(task_type, {})
        
        if len(task_perf) < self.db["learning_config"]["min_tasks_for_confident"]:
            # Not enough data, use exploration
            if random.random() < self.db["learning_config"]["exploration_rate"]:
                # Explore: try a random model
                return random.choice(self.models)
            else:
                # Use initial bias
                biases = self.config["model_biases"].get(task_type, [self.config["models"]["primary"]])
                return biases[0]
        
        # We have data, select based on performance
        best_model = None
        best_score = -1
        
        for model, stats in task_perf.items():
            if model not in self.models:
                continue
                
            # Calculate weighted score
            success_rate = stats.get("success_rate", 0.5)
            avg_duration = stats.get("avg_duration", 10)
            avg_cost = stats.get("avg_cost", 0.001)
            
            # Normalize and weight
            duration_score = 1.0 / (avg_duration + 0.1)  # Higher is better (faster)
            cost_score = 1.0 / (avg_cost + 0.0001)  # Higher is better (cheaper)
            
            weights = self.db["learning_config"]
            score = (
                success_rate * 0.4 +
                duration_score * weights["speed_weight"] +
                cost_score * weights["cost_weight"]
            )
            
            # Boost free models
            if model == self.config["models"]["primary"]:
                score *= weights["free_model_priority"]
            
            if score > best_score:
                best_score = score
                best_model = model
        
        return best_model or self.config["models"]["primary"]

    def enforce_token_budget(self, task_type: str, model: str, est_tokens: int) -> str:
        """Enforce token budget per task type using a simple day-based counter."""
        budget = self.config.get("token_budget", {})
        daily = budget.get("daily_tokens", None)
        today = datetime.utcnow().strftime("%Y-%m-%d")
        tb = self.db.get("token_budget", {})
        if tb.get("date") != today:
            tb = {"date": today, "used": 0}
        used = tb.get("used", 0)
        chosen_model = model
        if daily is not None and used + est_tokens > daily:
            biases = self.config.get("model_biases", {}).get(task_type, [self.config["models"]["primary"]])
            chosen_model = biases[-1] if biases else self.config["models"]["primary"]
            tb["used"] = used  # do not increment on override
        else:
            tb["used"] = used + est_tokens
        self.db["token_budget"] = tb
        self.save_db()
        return chosen_model
    
    def split_task(self, task: str) -> List[str]:
        """Split a complex task into subtasks"""
        delimiter = self.config["orchestrator"]["subtask_delimiter"]
        max_subtasks = self.config["orchestrator"]["max_subtasks"]
        min_len = self.config["orchestrator"]["min_subtask_length"]
        max_len = self.config["orchestrator"]["max_subtask_length"]
        
        # Split by delimiter
        raw_subtasks = [s.strip() for s in task.split(delimiter) if s.strip()]
        
        # Filter by length
        subtasks = []
        for st in raw_subtasks[:max_subtasks]:
            if min_len <= len(st) <= max_len:
                subtasks.append(st)
            elif len(st) > max_len:
                # Try to split further by sentences
                sentences = re.split(r'[.!?]+', st)
                for sent in sentences:
                    sent = sent.strip()
                    if min_len <= len(sent) <= max_len:
                        subtasks.append(sent)
                        if len(subtasks) >= max_subtasks:
                            break
        
        return subtasks[:max_subtasks]
    
    def execute_subtask(self, subtask: str, model: str) -> Dict[str, Any]:
        """Execute a subtask using the specified model"""
        # Escape quotes for shell command
        escaped_subtask = subtask.replace('"', '\\"')
        # Build dynamic --to based on numeric token or 6+ digit IDs
        to_param = self.config.get("orchestrator", {}).get("default_to", "5670001305")
        to_arg = ""
        if isinstance(to_param, str) and __import__('re').match(r'^\+?\d{6,}$', to_param):
            to_arg = f" --to {to_param}"
        elif isinstance(to_param, int) or (isinstance(to_param, str) and to_param.isdigit()):
            to_arg = f" --to {to_param}"
        cmd = f'openclaw agent --local{to_arg} --message "{escaped_subtask}"'
        
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            duration = time.time() - start_time
            
            # Estimate cost
            cost_per_sec = self.config["cost_per_second"].get(model, 0.0001)
            cost_estimate = duration * cost_per_sec
            
            output = result.stdout.strip() if result.stdout else result.stderr.strip()
            
            # Check if command succeeded (return code 0) and has meaningful output
            success = result.returncode == 0 and len(output) > 10
            
            return {
                "model": model,
                "duration": duration,
                "cost": cost_estimate,
                "success": success,
                "output": output[:1000],  # Limit output length
                "error": None if success else result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "model": model,
                "duration": 30,
                "cost": 30 * self.config["cost_per_second"].get(model, 0.0001),
                "success": False,
                "output": "",
                "error": "Timeout after 30 seconds"
            }
        except Exception as e:
            return {
                "model": model,
                "duration": time.time() - start_time,
                "cost": 0,
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    def update_performance(self, task_type: str, model: str, result: Dict):
        """Update performance database with execution results"""
        # Initialize structures if needed
        if task_type not in self.db["performance"]:
            self.db["performance"][task_type] = {}
        
        if model not in self.db["performance"][task_type]:
            self.db["performance"][task_type][model] = {
                "total_tasks": 0,
                "successful_tasks": 0,
                "durations": [],
                "costs": [],
                "avg_duration": 0,
                "avg_cost": 0,
                "success_rate": 0
            }
        
        stats = self.db["performance"][task_type][model]
        stats["total_tasks"] += 1
        stats["successful_tasks"] += 1 if result["success"] else 0
        stats["durations"].append(result["duration"])
        stats["costs"].append(result["cost"])
        
        # Update averages
        stats["avg_duration"] = sum(stats["durations"]) / len(stats["durations"])
        stats["avg_cost"] = sum(stats["costs"]) / len(stats["costs"])
        stats["success_rate"] = stats["successful_tasks"] / stats["total_tasks"]
        
        # Add to task history
        self.db["task_history"].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "task_type": task_type,
            "model": model,
            "duration": result["duration"],
            "cost": result["cost"],
            "success": result["success"],
            "subtask_preview": result["output"][:100] if result["output"] else ""
        })
        
        # Keep history manageable
        if len(self.db["task_history"]) > 1000:
            self.db["task_history"] = self.db["task_history"][-1000:]
        
        self.save_db()
    
    def log_execution(self, task_id: str, subtask_idx: int, result: Dict):
        """Log execution results to file"""
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / f"orchestrator_{task_id}.log"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(
                f"{datetime.now(UTC).isoformat()} | "
                f"Subtask {subtask_idx} | "
                f"Model: {result['model']} | "
                f"Duration: {result['duration']:.2f}s | "
                f"Cost: ${result['cost']:.6f} | "
                f"Success: {result['success']} | "
                f"Output: {result['output'][:200]}\n"
            )
        
        # Also update memory file
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MEMORY_FILE, 'a', encoding='utf-8') as mf:
            status = "✅" if result["success"] else "❌"
            mf.write(
                f"- **[{datetime.now(UTC).strftime('%Y-%m-%d %H:%M')}]** "
                f"{status} Subtask {subtask_idx}: `{result['model']}` · "
                f"{result['duration']:.1f}s · ~${result['cost']:.6f} · "
                f"{result['output'][:80] if result['output'] else 'no output'}\n"
            )
    
    def orchestrate(self, main_task: str) -> Dict[str, Any]:
        """Main orchestration function"""
        task_id = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        subtasks = self.split_task(main_task)
        
        if not subtasks:
            return {
                "task_id": task_id,
                "error": "No valid subtasks found",
                "results": []
            }
        
        results = []
        for i, subtask in enumerate(subtasks, 1):
            # Classify subtask
            task_type = self.classify_task(subtask)
            
            # Select model
            model = self.select_model(task_type)
            
            print(f"\n🔍 Subtask {i}/{len(subtasks)}: {subtask[:50]}...")
            print(f"   Type: {task_type}")
            print(f"   Selected model: {model}")
            
            # Execute
            est_tokens = max(1, len(subtask) // 4)
            model = self.enforce_token_budget(task_type, model, est_tokens)
            result = self.execute_subtask(subtask, model)
            results.append(result)
            
            # Update performance
            self.update_performance(task_type, model, result)
            
            # Log
            self.log_execution(task_id, i, result)
            
            print(f"   Duration: {result['duration']:.2f}s")
            print(f"   Cost: ${result['cost']:.6f}")
            print(f"   Success: {result['success']}")
            if result["error"]:
                print(f"   Error: {result['error']}")
        
        # Summary
        total_duration = sum(r["duration"] for r in results)
        total_cost = sum(r["cost"] for r in results)
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        
        summary = {
            "task_id": task_id,
            "total_subtasks": len(subtasks),
            "total_duration": total_duration,
            "total_cost": total_cost,
            "success_rate": success_rate,
            "results": results
        }
        
        print(f"\n🎉 Orchestration complete!")
        print(f"   Task ID: {task_id}")
        print(f"   Subtasks: {len(subtasks)}")
        print(f"   Total duration: {total_duration:.2f}s")
        print(f"   Total cost: ${total_cost:.6f}")
        print(f"   Success rate: {success_rate:.1%}")
        print(f"   Log: {LOG_DIR}/orchestrator_{task_id}.log")
        
        return summary

def main():
    if len(sys.argv) < 2:
        print("Usage: orchestrator.py \"<task description>\"")
        print("Example: orchestrator.py \"Write Python code for Fibonacci; Analyze results; Summarize report\"")
        sys.exit(1)
    
    task = sys.argv[1]
    orchestrator = TaskOrchestrator()
    
    try:
        result = orchestrator.orchestrate(task)
        
        # Print final results
        print("\n" + "="*50)
        print("FINAL RESULTS")
        print("="*50)
        for i, r in enumerate(result["results"], 1):
            print(f"\nSubtask {i}:")
            print(f"  Model: {r['model']}")
            print(f"  Duration: {r['duration']:.2f}s")
            print(f"  Cost: ${r['cost']:.6f}")
            print(f"  Success: {r['success']}")
            if r['output']:
                print(f"  Output: {r['output'][:200]}...")
        
    except Exception as e:
        print(f"❌ Error during orchestration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
