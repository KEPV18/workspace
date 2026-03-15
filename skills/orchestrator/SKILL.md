# OpenRouter Orchestrator Skill

## Description
Intelligent task splitting and model selection system for OpenClaw. Analyzes incoming messages, splits them into subtasks, selects the most appropriate free/cheap model for each subtask, learns from performance history, and optimizes for cost and quality.

## When to Use
Use this skill when you want to:
- Automatically split complex requests into subtasks
- Use the most cost-effective model for each subtask type
- Learn from past performance to improve future selections
- Reduce API costs while maintaining quality

## Architecture
```
orchestrator/
├── SKILL.md              # This file
├── orchestrator.py       # Main orchestration logic
├── task_db.json          # Performance database
├── config.yaml           # Model configurations and rules
└── references/          # Documentation and examples
```

## Setup
1. Ensure OpenRouter API key is configured
2. Ensure the cheap models list includes your preferred free/cheap models
3. Run the skill with a test message to verify splitting works

## Quick Start
```bash
# Test the orchestrator with a sample task
python ~/.openclaw/workspace/skills/orchestrator/orchestrator.py "Write Python code for Fibonacci; Analyze results; Summarize report"
```

## Models Supported
- Primary: openrouter/openai/gpt-5-nano (free/cheapest)
- Fallbacks: grok-3-mini, gemini-2.5-flash-lite, sonar, deepseek-r1, deepseek-v3.2

## Task Types Classification
The system classifies tasks into:
- `coding`: Programming tasks
- `analysis`: Data analysis, reasoning
- `summarization`: Text summarization
- `creative`: Creative writing, brainstorming
- `translation`: Language translation
- `qa`: Question answering

## Performance Tracking
Each task execution records:
- Model used
- Task type
- Duration (seconds)
- Cost estimate
- Success status
- Quality score (if available)

## Learning Algorithm
The system uses a simple reinforcement learning approach:
1. For each task type, track average performance per model
2. Prefer models with highest success rate for that task type
3. Balance exploration (trying new models) vs exploitation (using known good models)
4. Prioritize free models over paid ones when performance is similar

## Safety
- Never sends private data to external analytics
- All performance data stays locally in task_db.json
- Can be disabled at any time by removing the skill

## Related Skills
- `open-router`: OpenRouter configuration and routing
- `data-analysis`: For complex analysis tasks
- `memory`: For long-term learning improvements