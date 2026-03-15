#!/usr/bin/env python3
import json, sys, os, subprocess, time
from datetime import datetime, UTC

OPENCLAW_CONFIG = os.path.expanduser("~/.openclaw/openclaw.json")
LOG_DIR = os.path.expanduser("~/.openclaw/workspace/logs")
MEMORY_FILE = os.path.expanduser("~/.openclaw/memory/MEMORY.md")

CHEAP_ORDER = [
    "openrouter/openai/gpt-5-nano",
    "openrouter/x-ai/grok-3-mini",
    "openrouter/google/gemini-2.5-flash-lite",
    "openrouter/perplexity/sonar",
    "openrouter/deepseek/deepseek-r1",
    "openrouter/deepseek/deepseek-v3.2"
]


def load_config():
    with open(OPENCLAW_CONFIG, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(cfg):
    with open(OPENCLAW_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def ensure_models_present(cfg):
    providers = cfg.setdefault("models", {}).setdefault("providers", {})
    openrouter = providers.setdefault("openrouter", {})
    models_list = openrouter.setdefault("models", [])
    added = []
    for mod in CHEAP_ORDER:
        if not any(m.get("id") == mod for m in models_list):
            models_list.append({"id": mod, "name": mod.split("/")[-1]})
            added.append(mod)
    return added


def update_agent_defaults(cfg):
    agents = cfg.setdefault("agents", {})
    defaults = agents.setdefault("defaults", {})
    model_cfg = defaults.setdefault("model", {})
    model_cfg["primary"] = CHEAP_ORDER[0]
    model_cfg["fallbacks"] = CHEAP_ORDER[1:]
    return CHEAP_ORDER[0], CHEAP_ORDER[1:]


def log_result(task_id, sub_id, model, duration, cost_estimate, summary):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, f"auto_task_{task_id}.log")
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now(UTC).isoformat()} | Subtask {sub_id} | Model: {model} | dur={duration:.2f}s | est_cost={cost_estimate:.6f}$ | summary={summary}\n")
    
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, 'a', encoding='utf-8') as mf:
        mf.write(f"- **[{datetime.now(UTC).strftime('%Y-%m-%d %H:%M')}]** Subtask {sub_id}: `{model}` · {duration:.1f}s · ~${cost_estimate:.6f} · {summary[:100]}\n")


def run_subtask(desc, model):
    cmd = f"openclaw run --model {model} --task \"{desc}\" --log-level info"
    t0 = time.time()
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    t1 = time.time()
    out = proc.stdout.strip() if proc.stdout else proc.stderr.strip()
    duration = t1 - t0
    summary = out[:1000] if out else "no-output"
    cost_estimate = 0.002 * duration  # simplified cost model
    return model, duration, cost_estimate, summary


def main():
    if len(sys.argv) < 2:
        print("Usage: auto_task_orchestrator.py \"<task description>\"")
        sys.exit(1)
    
    task_desc = sys.argv[1]
    subtasks = [s.strip() for s in task_desc.split(';') if s.strip()]

    cfg = load_config()
    ensure_models_present(cfg)
    primary, fallbacks = update_agent_defaults(cfg)
    save_config(cfg)

    task_id = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    
    for i, st in enumerate(subtasks, start=1):
        model_idx = (i-1) % len(CHEAP_ORDER)
        model = CHEAP_ORDER[model_idx]
        used_model, dur, cost, summary = run_subtask(st, model)
        log_result(task_id, i, used_model, dur, cost, summary)

    print(f"🚀 Automated orchestration completed for task {task_id}")
    print(f"📊 View logs: {LOG_DIR}/auto_task_{task_id}.log")
    print(f"📚 Memory updated: {MEMORY_FILE}")

if __name__ == '__main__':
    main()