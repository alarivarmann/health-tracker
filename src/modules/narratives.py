"""
Narratives module - builds stories using OFFICIAL instructions from YAML
"""
import json
from datetime import datetime
from .config import NARRATIVES_FILE

OFFICIAL_INSTRUCTIONS = """
You are analyzing work and individual metrics to build a coherent data-driven STORY about patterns and relationships.

## YOUR TASK: BUILD A NARRATIVE

Construct a story based on the data patterns that:

1. **Identifies the Main Theme**
   - What's the central pattern observable in the data? (e.g., "A week of recovery", "Mounting pressure", "Breaking through")
   - One sentence that captures the essence

2. **Connect the Dots** 
   - How do the metrics relate to each other?
   - What causal relationships are suggested? (e.g., "High project chaos → Poor sleep → Increased anxiety")
   - Look for chains of influence, not just correlations

3. **Provide Context**
   - Consider work-life dynamics visible in the data
   - Examine energy levels and autonomy patterns
   - Note environmental factors that might explain the patterns

4. **Offer Specific, Actionable Insights**
   - Not generic advice ("try to relax")
   - Tailored to THIS specific data pattern
   - Concrete next steps based on the metrics

## OUTPUT FORMAT

Structure your response as:

### 📖 The Story in Your Data
[Opening: What's the main theme observable in the metrics? 1-2 sentences]

[Deep dive: Connect the metrics into a narrative. 2-3 paragraphs explaining the causal relationships and patterns visible in the data]

### 🔍 What the Patterns Suggest
[Root causes: What underlying factors might explain these data patterns? 1 paragraph]

### 🎯 Specific Actions Based on These Patterns

Based on the data patterns, here are concrete next steps:

1. **[Action Name]** (Priority: High/Medium/Low)
   - Why: [Brief rationale based on the data story]
   - How: [Specific steps]

2. **[Action Name]**
   - Why: [...]
   - How: [...]

## REFLEX ACTION RULES (APPLY WHEN TRIGGERED)

Incorporate these into your specific actions when thresholds are met:

**Requests ≥ 8** → TERP Escalation
- Template: "Hi [Name], Could you provide the TERP/reference code before I schedule time? Otherwise I'll defer it to stay aligned with current priorities."
- Only show if "saying no" ≤ 5

**Sleep ≤ 4** → Sleep Recovery Plan
- Check environment (temp, window, noise)
- Evening routine discussion
- No screens ≥ 1h before bed
- If persistent ≥ 2 sessions → consider quetiapine per plan

**Anxiety ≥ 8 or Irritability ≥ 8** → Calm Reset
- nVNS + 10 min walk
- Postpone non-critical meetings
- Resume once calm

**Project chaos ≥ 7** → Anti-Chaos Routine
- Diagnostic: Lack of PM? Meeting sprawl? Shifting criteria?
- **Pull-Request Chaos Protocol:**
  1. Before starting: post intent note ("Implementing X for criteria Y. Proceeding unless objections today.")
  2. Work autonomously
  3. At PR: link intent + state "Implementation matches documented agreement from [date]"
  4. If scope changes after: "Happy to adjust in next iteration; merging this to avoid stagnation"
- **Skip-Meeting Template:** "Hi all, I'll skip this call to keep focus on the feature. Please share key notes async."
- Mindset: Delivery first, no defensive apologies. Chaos belongs to system, not you.

**Jira autonomy ≤ 4** → Self-Authorization Rule
- Choose one task you can complete solo this week
- Announce ownership: "Taking X independently to reduce overhead"
- Remember: Value > permission

**Stress outside work ≥ 8** → Therapy & Source Check
- Assess if more sessions needed
- Describe main stress source
- One small next step (schedule/message therapist)

**Quiet work blocks ≤ 3** → Daily Deep-Work Anchor
- Reserve same 2-hour block daily (e.g., 09:00-11:00)
- Treat as non-negotiable
- Apply Chaos Protocol at PR time if challenged
- Log protection success rate

**General Principles (Slow Productivity & Deep Work):**
- Fewer things, better
- Depth > responsiveness
- Batch communication; avoid "constant sync" trap
- Protect solitude daily
- End with deliberate shutdown ritual

**Delivery Log Recommendation:**
- Trigger if ANY ≥ 6: deadline pressure, unmet requests, project chaos, unwanted meetings, anxiety, irritability
- Recommend: "Consider using delivery_log.md to document scope and manage expectations"

## CRITICAL: DO NOT
- List thresholds generically ("X is below Y threshold")
- Repeat protocol names without context
- State what's "within range" repetitively
- Generate comparison tables or metric change lists (the UI handles this with mechanical rules)
- Enumerate individual metrics or their values (focus on patterns only)

## FOCUS ON
- Storytelling and causality between metrics
- Personalized insights based on the specific pattern
- Making connections between metrics (what influences what)
- Actionable, concrete guidance based on observable patterns
- Root causes and systemic issues, not individual metric values

## NOTE
The UI will automatically display:
- Top priority issues (severity increases, continuous problems)
- Mechanical classification of safe vs problem metrics
- Statistical trend analysis

Your role is to tell the STORY behind the data, not list the data itself.

"""

def load_narratives():
    if not NARRATIVES_FILE.exists():
        return []
    with open(NARRATIVES_FILE, 'r') as f:
        return json.load(f)

def save_narrative(date, narrative, feedback=None):
    narratives = load_narratives()
    existing = next((n for n in narratives if n['date'] == date), None)
    if existing:
        if feedback:
            existing['feedback'] = feedback
            existing['updated_at'] = datetime.now().isoformat()
    else:
        narratives.append({
            'date': date,
            'narrative': narrative,
            'feedback': feedback,
            'created_at': datetime.now().isoformat()
        })
    with open(NARRATIVES_FILE, 'w') as f:
        json.dump(narratives, f, indent=2)

def get_recent_narratives(n=3):
    narratives = load_narratives()
    return narratives[-n:] if len(narratives) >= n else narratives

def build_context_prompt(metrics, previous, changes):
    """Build prompt using OFFICIAL YAML instructions"""
    recent_narratives = get_recent_narratives(3)

    # Locate the most recent piece of user feedback (if any)
    latest_feedback_entry = next(
        (narr for narr in reversed(recent_narratives) if narr.get('feedback')),
        None
    )

    # Extract free-form context if provided
    user_context = metrics.get('context', None)

    prompt = "# Work & Individual Metrics Analysis\n\n"

    # Surface the latest feedback as an overriding directive
    if latest_feedback_entry and latest_feedback_entry.get('feedback'):
        prompt += "## Immediate User Directive (Overrides Template)\n"
        prompt += "**You must answer this directive directly before following any other instructions.**\n\n"
        prompt += f"> {latest_feedback_entry['feedback']}\n\n"

    # Add user's free-form context prominently just below the directive if provided
    if user_context:
        prompt += "## User's Additional Context\n"
        prompt += "**Use this situational context to interpret the metrics and frame your story.**\n\n"
        prompt += f"> {user_context}\n\n"
    
    prompt += "## Current Metrics\n"
    for key, value in metrics.items():
        if key != 'date' and key != 'context' and key != 'recommendation' and value is not None:
            prompt += f"- {key.replace('_', ' ').title()}: {value}\n"
    
    # Add previous recommendation effectiveness analysis
    if previous and 'recommendation' in previous and previous['recommendation']:
        prompt += "\n## Previous Recommendation Effectiveness Analysis\n"
        prompt += "**Previous Entry Date:** " + str(previous.get('date', 'Unknown')) + "\n\n"
        prompt += "**Previous Metrics:**\n"
        for key, value in previous.items():
            if key != 'date' and key != 'context' and key != 'recommendation' and value is not None:
                prompt += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        prompt += "\n**Previous Recommendation:**\n"
        prompt += f"{previous['recommendation']}\n\n"
        prompt += "**Your Task:** Compare the previous metrics with current metrics to assess:\n"
        prompt += "1. Did following the previous recommendations appear to help? (Look at metric changes)\n"
        prompt += "2. Which specific recommendations seem to have been effective?\n"
        prompt += "3. Which areas still need attention or different approaches?\n"
        prompt += "4. Incorporate this effectiveness assessment into your new narrative and recommendations.\n\n"
    
    if changes:
        prompt += "\n## Changes from Previous Entry (for your reference)\n"
        
        rising = []
        declining = []
        stable = []
        
        for key, change in changes.items():
            delta = change['delta']
            if delta > 0.5:
                rising.append(f"{change['label']}: {change['previous']:.1f} → {change['current']:.1f} (+{delta:.1f})")
            elif delta < -0.5:
                declining.append(f"{change['label']}: {change['previous']:.1f} → {change['current']:.1f} ({delta:.1f})")
            else:
                stable.append(f"{change['label']}: Stable at {change['current']:.1f}")
        
        if rising:
            prompt += "**Rising:**\n"
            for item in rising:
                prompt += f"- {item}\n"
        if declining:
            prompt += "**Declining:**\n"
            for item in declining:
                prompt += f"- {item}\n"
        if stable:
            prompt += "**Stable:**\n"
            for item in stable:
                prompt += f"- {item}\n"
    
    historical_feedback = [
        narr for narr in recent_narratives
        if narr.get('feedback') and narr != latest_feedback_entry
    ]

    if historical_feedback:
        prompt += "\n## Earlier User Feedback (Reference Only)\n"
        prompt += "Use these prior comments for background context after you fully satisfy the immediate directive.\n"
        for narr in historical_feedback:
            prompt += f"{narr['date']}: {narr['feedback']}\n"
    
    prompt += "\n## Priority Rules You Must Follow\n"
    prompt += "1. If an \"Immediate User Directive\" appears above, answer it explicitly and confirm how your story addresses it before doing anything else.\n"
    prompt += "2. Incorporate any \"User's Additional Context\" into your reasoning and recommendations.\n"
    prompt += "3. Only after completing steps 1 and 2 should you follow the OFFICIAL narrative instructions that follow.\n"

    prompt += "\n" + OFFICIAL_INSTRUCTIONS
    
    return prompt
