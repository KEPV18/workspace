#!/usr/bin/env python3
"""
تغيير هرم الموديلات لاستخدام الموديلات الرخيصة أولاً، ثم الانتقال للمجانية عند نفاد الرصيد.
الترتيب المطلوب:
1. Primary: openai/gpt-5-nano (أرخص)
2. Fallbacks: x-ai/grok-3-mini, google/gemini-2.5-flash-lite, perplexity/sonar, deepseek/deepseek-r1
3. إذا فشلوا كلهم: الموديلات المجانية
"""

import json
from pathlib import Path

OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"

# قائمة الموديلات الرخيصة بالترتيب المفضل (من أرخص إلى الأغلى قليلاً)
CHEAP_MODELS = [
    "openrouter/openai/gpt-5-nano",
    "openrouter/x-ai/grok-3-mini",
    "openrouter/google/gemini-2.5-flash-lite",
    "openrouter/perplexity/sonar",
    "openrouter/deepseek/deepseek-r1"
]

# أسماء الموديلات بدون البادئة (لإضافتها إلى providers.openrouter.models)
CHEAP_MODEL_IDS = [
    "openai/gpt-5-nano",
    "x-ai/grok-3-mini",
    "google/gemini-2.5-flash-lite",
    "perplexity/sonar",
    "deepseek/deepseek-r1"
]

# الموديلات المجانية (الترتيب الحالي)
FREE_MODELS = [
    "openrouter/free:free",
    "openrouter/hunter-alpha:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "healer-alpha:free",
    "nvidia/nemotron-3-nano-30b-a3b:free"
]

def load_config():
    with open(OPENCLAW_CONFIG, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open(OPENCLAW_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"✅ تم حفظ التحديثات في: {OPENCLAW_CONFIG}")

def ensure_provider_models(config):
    """إضافة الموديلات الرخيصة إلى قائمة providers.openrouter.models"""
    providers = config.setdefault("models", {}).setdefault("providers", {})
    openrouter = providers.setdefault("openrouter", {})
    models_list = openrouter.setdefault("models", [])

    added = []
    for model_id in CHEAP_MODEL_IDS:
        # تحقق من وجود الموديل مسبقاً
        if not any(m.get("id") == model_id for m in models_list):
            models_list.append({
                "id": model_id,
                "name": model_id.split("/")[-1].split(":")[0]
            })
            added.append(model_id)
    return added

def update_agents_model_config(config):
    """تحديث إعدادات الـ model في agents.defaults"""
    agents = config.setdefault("agents", {})
    defaults = agents.setdefault("defaults", {})
    model_cfg = defaults.setdefault("model", {})
    models_detail = defaults.setdefault("models", {})

    # Primary: أول موديل رخيص
    primary = CHEAP_MODELS[0]
    model_cfg["primary"] = primary

    # Fallbacks: كل الموديلات الرخيصة (بعد primary) ثم المجانية
    fallbacks = CHEAP_MODELS[1:] + FREE_MODELS
    model_cfg["fallbacks"] = fallbacks

    # إضافة تفاصيل الموديلات إلى agents.defaults.models
    all_models = CHEAP_MODELS + FREE_MODELS
    for m in all_models:
        if m not in models_detail:
            models_detail[m] = {}

    return primary, fallbacks

def main():
    print("🚀 بدء تحديث هرم الموديلات (رخيصة أولاً، مجانية كحل أخير)...")
    print("========================================")

    config = load_config()
    print("✅ تم قراءة التكوين الحالي")

    # إضافة الموديلات إلى providers
    added_provider = ensure_provider_models(config)
    if added_provider:
        print(f"📝 أضفت {len(added_provider)} موديل إلى providers.openrouter.models:")
        for m in added_provider:
            print(f"   • {m}")
    else:
        print("ℹ️  الموديلات الرخيصة موجودة مسبقاً في providers")

    # تحديد الـ Primary والـ Fallbacks
    primary, fallbacks = update_agents_model_config(config)
    print(f"\n🎯 Primary设置为: {primary}")
    print(f"📋 الترتيب الجديد لـ Fallbacks ({len(fallbacks)} موديل):")
    for i, m in enumerate(fallbacks, 1):
        marker = "🆓" if ":free" in m else "💰"
        print(f"   {i:2d}. {m:<50} {marker}")

    save_config(config)

    print("\n========================================")
    print("🎉 تم تحديث هرم الموديلات بنجاح!")
    print("\n⚡ كيف تعمل الآن:")
    print("1. Primary (أرخص موديل): openrouter/openai/gpt-5-nano")
    print("2. إذا فشل أو نفد الرصيد: ينتقل للموديل الرخيص التالي في القائمة")
    print("3. إذا نفد رصيد كل الموديلات الرخيصة: تلقائيًا ينتقل للمجانية")
    print("\n💡 ملاحظة: المجانية متاحة كخط احتياطي أخير فقط.")
    print("\n🔄 أعد تشغيل OpenClaw لتطبيق التغييرات!")
    print("========================================")

if __name__ == "__main__":
    main()