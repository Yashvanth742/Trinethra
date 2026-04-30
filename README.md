🚀 Trinethra – AI-Assisted Supervisor Feedback Analyzer

Trinethra is a web-based AI-assisted analysis tool designed to streamline the evaluation of supervisor feedback within DeepThought’s PDGMS ecosystem. It transforms unstructured supervisor transcripts into structured, actionable insights, significantly reducing manual analysis time while preserving human judgment.

🧠 Problem

Traditionally, psychology interns manually analyze 10–15 minute supervisor calls by reading transcripts, extracting behavioral evidence, mapping observations to a rubric, identifying gaps, and writing assessments. This process typically takes 45–60 minutes per transcript and is prone to inconsistencies.

💡 Solution

Trinethra leverages a local LLM (via Ollama) to generate a draft behavioral assessment from supervisor transcripts. Instead of replacing human decision-making, the system acts as an assistant—providing structured suggestions that interns can review, edit, accept, or reject.

⚙️ Key Features
📥 Transcript Input: Paste supervisor feedback directly into the application
🤖 AI-Powered Analysis: Uses a local LLM to extract observations, assign scores, and identify gaps
📊 Structured Output: Generates rubric-based insights such as behavior, score, and improvement suggestions
✏️ Human-in-the-Loop Editing: Each AI-generated finding can be accepted, edited, or rejected
⚠️ Hallucination Control: Prompt guardrails ensure outputs are grounded strictly in the transcript
📤 Export Functionality: Generate final reports after review
🧠 Design Philosophy

Trinethra follows a “AI suggests, human decides” approach. The system is intentionally built to augment—not replace—human judgment, ensuring reliability, transparency, and accountability in behavioral assessments.

🔧 Tech Stack
Frontend: HTML/CSS/JavaScript (or React)
Backend: Flask / Python
AI: Ollama (Local LLM)
📈 Impact

By reducing analysis time from ~60 minutes to under 10 minutes, Trinethra improves efficiency while maintaining high-quality evaluations. It also standardizes assessment workflows and minimizes subjective inconsistencies.
