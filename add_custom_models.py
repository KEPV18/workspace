#!/usr/bin/env python3
"""
إضافة الموديلات المخصصة لهرم التكلفة الذكي
للمدير أحمد خالد
"""

import json
import os
import sys
from pathlib import Path

# مسار ملف التكوين
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"

# هرم الموديلات المطلوبة
MODEL_HIERARCHY = {
    "المستوى 1 - مجاني": [
        "openrouter/hunter-alpha:free",
        "openrouter/free:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "healer-alpha:free",
        "nvidia/nemotron-3-nano-30b-a3b:free"
    ],
    "المستوى 2 - رخيص": [
        "openai/gpt-5-nano",
        "x-ai/grok-3-mini", 
        "google/gemini-2.5-flash-lite",
        "perplexity/sonar",
        "deepseek/deepseek-r1"
    ],
    "المستوى 3 - متوسط": [
        "openrouter/deepseek/deepseek-v3.2"
    ]
}

def read_config():
    """قراءة ملف التكوين"""
    if not CONFIG_PATH.exists():
        print(f"❌ ملف التكوين غير موجود: {CONFIG_PATH}")
        sys.exit(1)
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_config(config):
    """كتابة ملف التكوين"""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ تم تحديث التكوين في: {CONFIG_PATH}")

def update_model_config(config):
    """تحديث قسم الموديلات"""
    
    # التأكد من وجود قسم agents
    if "agents" not in config:
        config["agents"] = {}
    
    if "defaults" not in config["agents"]:
        config["agents"]["defaults"] = {}
    
    # قسم model الرئيسي
    if "model" not in config["agents"]["defaults"]:
        config["agents"]["defaults"]["model"] = {}
    
    model_config = config["agents"]["defaults"]["model"]
    
    # تحديث الـ fallbacks مع الهرم الكامل
    all_fallbacks = []
    
    # إضافة كل الموديلات بالترتيب
    for level_name, models in MODEL_HIERARCHY.items():
        print(f"📊 {level_name}:")
        for model in models:
            if model not in all_fallbacks:
                all_fallbacks.append(model)
                print(f"   ✅ {model}")
    
    # تحديث الـ fallbacks
    model_config["fallbacks"] = all_fallbacks
    
    # قسم models التفصيلي
    if "models" not in config["agents"]["defaults"]:
        config["agents"]["defaults"]["models"] = {}
    
    models_detail = config["agents"]["defaults"]["models"]
    
    # إضافة كل الموديلات إلى القسم التفصيلي
    for model in all_fallbacks:
        if model not in models_detail:
            models_detail[model] = {}
    
    return config

def update_providers_config(config):
    """تحديث قسم providers"""
    
    # التأكد من وجود قسم models
    if "models" not in config:
        config["models"] = {}
    
    if "providers" not in config["models"]:
        config["models"]["providers"] = {}
    
    providers = config["models"]["providers"]
    
    # التأكد من وجود openrouter
    if "openrouter" not in providers:
        providers["openrouter"] = {
            "baseUrl": "https://openrouter.ai/api/v1",
            "api": "openai-completions",
            "apiKey": "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"
        }
    
    # إضافة جميع الموديلات إلى قائمة openrouter
    if "models" not in providers["openrouter"]:
        providers["openrouter"]["models"] = []
    
    openrouter_models = providers["openrouter"]["models"]
    
    # جمع جميع الموديلات التي تبدأ بـ openrouter/
    all_models = []
    for level_name, models in MODEL_HIERARCHY.items():
        all_models.extend(models)
    
    for model in all_models:
        if model.startswith("openrouter/"):
            model_id = model.replace("openrouter/", "")
            model_entry = {
                "id": model_id,
                "name": model_id.split("/")[-1].split(":")[0]
            }
            
            # إضافة إذا لم تكن موجودة
            if not any(m["id"] == model_id for m in openrouter_models):
                openrouter_models.append(model_entry)
                print(f"   📝 أضفت {model_id} إلى providers")
    
    return config

def main():
    print("🚀 بدء إعداد هرم التكلفة الذكي...")
    print("========================================")
    
    # قراءة التكوين الحالي
    config = read_config()
    print("✅ قراءة التكوين الحالي")
    
    # تحديث قسم الموديلات
    print("\n📋 تحديث هرم الموديلات:")
    config = update_model_config(config)
    
    # تحديث قسم providers
    print("\n🔧 تحديث providers:")
    config = update_providers_config(config)
    
    # كتابة التكوين الجديد
    write_config(config)
    
    print("\n========================================")
    print("🎉 تم إعداد هرم التكلفة الذكي بنجاح!")
    print("\n📊 الهرم الجديد:")
    
    # عرض الهرم النهائي
    fallbacks = config["agents"]["defaults"]["model"].get("fallbacks", [])
    for i, model in enumerate(fallbacks, 1):
        level = "🆓 مجاني" if ":free" in model else "💰 مدفوع"
        print(f"{i:2d}. {model:<50} {level}")
    
    print("\n⚡ التعليمات:")
    print("1. سيعمل OpenClaw بالموديلات المجانية أولاً")
    print("2. إذا فشل مجاني، ينتقل للرخيص")
    print("3. إذا فشل رخيص، ينتقل للمتوسط")
    print("4. جميع الموديلات متاحة على OpenRouter")
    print("\n🔄 أعد تشغيل OpenClaw للتغييرات!")
    print("========================================")

if __name__ == "__main__":
    main()