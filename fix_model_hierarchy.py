#!/usr/bin/env python3
"""
إصلاح هرم الموديلات ليعمل بشكل صحيح
"""

import json
import os
import sys
from pathlib import Path

CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"

def read_config():
    if not CONFIG_PATH.exists():
        print(f"❌ ملف التكوين غير موجود: {CONFIG_PATH}")
        sys.exit(1)
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ تم تحديث التكوين في: {CONFIG_PATH}")

def fix_model_hierarchy(config):
    """إصلاح هرم الموديلات للعمل الصحيح"""
    
    print("🔧 إصلاح هرم الموديلات...")
    
    # الحصول على قسم الموديلات
    model_config = config["agents"]["defaults"]["model"]
    
    # التكوين الصحيح:
    # 1. Primary: openrouter/free (الروتر الذكي الذي يختار أفضل مجاني)
    # 2. Fallbacks: الموديلات المدفوعة إذا فشلت كل المجانية
    
    correct_primary = "openrouter/free:free"
    correct_fallbacks = [
        # إذا فشل openrouter/free، نجرب مجاني آخر مباشرة
        "openrouter/hunter-alpha:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "healer-alpha:free",
        "nvidia/nemotron-3-nano-30b-a3b:free",
        # إذا فشلت كل المجانية، ننتقل للرخيص
        "openai/gpt-5-nano",
        "x-ai/grok-3-mini", 
        "google/gemini-2.5-flash-lite",
        "perplexity/sonar",
        "deepseek/deepseek-r1",
        # آخر حل: الموديل المتوسط
        "openrouter/deepseek/deepseek-v3.2"
    ]
    
    # تحديث الـ Primary
    old_primary = model_config.get("primary", "")
    model_config["primary"] = correct_primary
    
    # تحديث الـ Fallbacks
    old_fallbacks = model_config.get("fallbacks", [])
    model_config["fallbacks"] = correct_fallbacks
    
    print(f"   📊 Primary: {old_primary} → {correct_primary}")
    print(f"   📋 Fallbacks: {len(old_fallbacks)} → {len(correct_fallbacks)} موديل")
    
    # تحديث قسم models التفصيلي
    models_detail = config["agents"]["defaults"]["models"]
    
    # إضافة Primary الجديد إذا لم يكن موجوداً
    if correct_primary not in models_detail:
        models_detail[correct_primary] = {}
    
    return config

def main():
    print("🚀 بدء إصلاح هرم الموديلات...")
    print("========================================")
    
    # قراءة التكوين الحالي
    config = read_config()
    
    # إصلاح هرم الموديلات
    config = fix_model_hierarchy(config)
    
    # كتابة التكوين الجديد
    write_config(config)
    
    print("\n========================================")
    print("🎉 تم إصلاح هرم الموديلات بنجاح!")
    print("\n📊 التكوين الصحيح الآن:")
    print(f"   1. Primary: openrouter/free:free")
    print(f"     ⚡ (روتر ذكي يختار أفضل موديل مجاني تلقائياً)")
    print(f"   2. Fallback 1-4: موديلات مجانية احتياطية")
    print(f"   3. Fallback 5-9: موديلات رخيصة")
    print(f"   4. Fallback 10: موديل متوسط (آخر حل)")
    
    print("\n⚡ كيفية العمل:")
    print("1. openrouter/free يختار أفضل موديل مجاني تلقائياً")
    print("2. إذا فشل، ينتقل للمجاني الاحتياطي الأول")
    print("3. إذا فشلت كل المجانية، ينتقل للرخيص")
    print("4. إذا فشل كل شيء، ينتقل للمتوسط")
    print("\n💰 التوفير: 100% مجاني ما دامت الموديلات المجانية تعمل!")
    print("\n🔄 أعد تشغيل OpenClaw للتغييرات!")
    print("========================================")

if __name__ == "__main__":
    main()