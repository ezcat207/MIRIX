TEMPORARY_MESSAGE_LIMIT = 20  # 降低批处理大小，减少单次 LLM 调用阻塞时间
MAXIMUM_NUM_IMAGES_IN_CLOUD = 600

GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.5-flash-lite",
    "gemini-1.5-pro",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
]
OPENAI_MODELS = [
    "gpt-4.1-mini",
    "gpt-4.1",
    "gpt-4o-mini",
    "gpt-4o",
    "o4-mini",
    "gpt-5-mini",
    "gpt-5",
]

OLLAMA_MODELS = [
    "llama3.2",
    "mistral",
    "gemma2",
    "qwen2.5-coder-32b",
    "deepseek-r1-distill-llama-70b",
    "deepseek-v3.1:671b-cloud",
    "qwen3-vl:235b-cloud",
]

STUCK_TIMEOUT = 10
RUNNING_TIMEOUT = 30
TOTAL_TIMEOUT = 60

SKIP_META_MEMORY_MANAGER = False

# Whether to use the reflexion agent
WITH_REFLEXION_AGENT = False

# Whether to use the background agent

# Phase 2: Mech Pilot Constants
PROJECTS_MD_PATH = "/Volumes/Lexar/AISync90/MIRIX/mock/projects.json"
TOOLS_MD_PATH = "/Users/power/Documents/obsidian-out-of-the-box/tools.md"
