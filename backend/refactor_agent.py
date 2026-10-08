import sys
with open('app/ai/agent_executor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_mode = False

for i, line in enumerate(lines):
    if line.startswith("def get_state_crop_recommendations("):
        skip_mode = True
    
    if skip_mode and line.startswith("class AgriGeniusLangChainAgent:"):
        skip_mode = False
        
    if not skip_mode:
        new_lines.append(line)

with open('app/ai/agent_executor.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully removed get_state_crop_recommendations")
