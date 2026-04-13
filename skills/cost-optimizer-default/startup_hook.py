#!/usr/bin/env python3
"""
Startup Hook for Cost Optimizer Default
Runs automatically when OpenClaw starts
"""

import os
import json
import time
from pathlib import Path

def run_startup_hook():
    """Run when OpenClaw starts"""
    workspace_dir = Path.home() / ".openclaw" / "workspace"
    skill_dir = workspace_dir / "skills" / "cost-optimizer-default"
    
    # Create startup log
    startup_log = skill_dir / "startup_log.json"
    
    startup_data = {
        "last_startup": time.strftime("%Y-%m-%d %H:%M:%S"),
        "skill_version": "1.0.0",
        "default_model": "z-ai/glm-4.7-flash",
        "optimization_enabled": True,
        "auto_mode": True
    }
    
    with open(startup_log, 'w') as f:
        json.dump(startup_data, f, indent=2)
    
    # Create or update config file
    config_file = workspace_dir / "cost_optimizer_config.json"
    if not config_file.exists():
        config_data = {
            "optimizer_settings": {
                "default_model": "z-ai/glm-4.7-flash",
                "auto_select": True,
                "complexity_analysis": True,
                "cost_tracking": True,
                "budget_limit": 10.0,
                "warnings_enabled": True
            },
            "model_preferences": {
                "economy": ["z-ai/glm-4.7-flash", "google/gemini-2.5-flash-lite"],
                "balanced": ["openai/gpt-5-nano", "x-ai/grok-3-mini"],
                "power": ["deepseek/deepseek-v3.2", "perplexity/sonar"]
            },
            "cost_rates": {
                "z-ai/glm-4.7-flash": {"input": 0.00000006, "output": 0.0000004},
                "google/gemini-2.5-flash-lite": {"input": 0.000000075, "output": 0.0000003},
                "openai/gpt-5-nano": {"input": 0.0000001, "output": 0.0000004},
                "x-ai/grok-3-mini": {"input": 0.0000003, "output": 0.0000005},
                "deepseek/deepseek-v3.2": {"input": 0.00000032, "output": 0.00000089},
                "perplexity/sonar": {"input": 0.000001, "output": 0.000001}
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    # Print startup message
    print("=" * 60)
    print("💰 محسن التكلفة الافتراضي - جاهز للتشغيل")
    print("=" * 60)
    print("🎯 النموذج الافتراضي: z-ai/glm-4.7-flash")
    print("📊 التحكم التلقائي في التكلفة: مفعل")
    print("⚠️  تحذيرات الميزانية: مفعلة")
    print("=" * 60)
    
    # Check monthly budget
    cost_file = skill_dir / "cost_tracker.json"
    if cost_file.exists():
        with open(cost_file, 'r') as f:
            cost_data = json.load(f)
        
        current_month = time.strftime("%Y-%m")
        monthly_spent = cost_data.get("monthlySpent", {}).get(current_month, 0.0)
        budget_limit = 10.0
        
        if monthly_spent > 0:
            percentage = (monthly_spent / budget_limit) * 100
            print(f"📈 الإنفاق الشهري الحالي: ${monthly_spent:.2f} ({percentage:.1f}% من الميزانية)")
            
            if percentage > 90:
                print("🚨 تحذير: تجاوزت 90% من الميزانية الشهرية!")
            elif percentage > 70:
                print("⚠️  ملاحظة: تجاوزت 70% من الميزانية الشهرية")
            else:
                remaining = budget_limit - monthly_spent
                print(f"✅ الميزانية المتبقية: ${remaining:.2f}")
    
    print("\n✅ المحسن الافتراضي يعمل تلقائياً مع كل طلب")
    print("   - يحلل تعقيد المهمة")
    print("   - يختار النموذج الأمثل")
    print("   - يتحكم في التكلفة")
    print("   - يسجل الإحصائيات")
    print("\n🔧 للأوامر: 'أعرض إحصائيات التكلفة' أو 'تحقق من الميزانية'")
    print("=" * 60)
    
    return True

def check_dependencies():
    """Check if all dependencies are available"""
    required_files = [
        "optimizer.py",
        "model_rules.yaml",
        "SKILL.md"
    ]
    
    workspace_dir = Path.home() / ".openclaw" / "workspace"
    skill_dir = workspace_dir / "skills" / "cost-optimizer-default"
    
    missing_files = []
    for file in required_files:
        if not (skill_dir / file).exists():
            missing_files.append(file)
    
    return missing_files

if __name__ == "__main__":
    print("🔍 فحص تبعيات محسن التكلفة...")
    
    missing = check_dependencies()
    if missing:
        print(f"❌ ملفات مفقودة: {', '.join(missing)}")
        print("يرجى استكمال تثبيت المهارة.")
    else:
        print("✅ جميع الملفات متوفرة")
        print("\n🚀 تشغيل خطاف البداية...")
        success = run_startup_hook()
        
        if success:
            print("\n🎉 اكتمل التهيئة بنجاح!")
            print("محسن التكلفة الافتراضي جاهز للعمل.")
        else:
            print("\n❌ حدث خطأ أثناء التهيئة.")