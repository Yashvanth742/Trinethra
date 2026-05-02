🧠 Problem Statement

Traditionally, psychology interns manually analyze 10–15 minute supervisor calls by reading transcripts, extracting behavioral evidence, mapping observations to a rubric, identifying gaps, and writing assessments. This process typically takes 45–60 minutes per transcript and is prone to inconsistencies.

💡 Solution

Trinethra leverages the Gemini API to generate a draft behavioral assessment from supervisor transcripts.

Instead of replacing human decision-making, the system acts as an assistant—providing structured suggestions that interns can review, edit, accept, or reject.

⚙️ Key Features

📥 Transcript Input
Paste supervisor feedback directly into the application

🤖 AI-Powered Analysis
Uses Gemini (via API key) to extract observations, assign scores, and identify behavioral gaps

📊 Structured Output
Generates rubric-based insights such as:

Behavior observed
Score (1–10 scale)
Improvement suggestions

✏️ Human-in-the-Loop Editing
Each AI-generated finding can be accepted, edited, or rejected

⚠️ Hallucination Control
Prompt guardrails ensure outputs remain grounded strictly in the transcript

📤 Export Functionality
Generate final reports after review

🧠 Design Philosophy

Trinethra follows an “AI suggests, human decides” approach.

The system is intentionally built to augment—not replace—human judgment, ensuring:

Reliability
Transparency
Accountability
🔧 Tech Stack
Frontend: HTML/CSS/JavaScript (or React)
Backend: Flask / Python
AI: Gemini API
📈 Impact

By reducing analysis time from ~60 minutes to under 10 minutes, Trinethra:

Improves efficiency
Maintains high-quality evaluations
Standardizes assessment workflows
Minimizes subjective inconsistencies
