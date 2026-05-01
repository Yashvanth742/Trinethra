import os
import json
import re
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100))
    transcript = db.Column(db.Text)
    sentiment_score = db.Column(db.Integer)
    sentiment_label = db.Column(db.String(50))
    findings_json = db.Column(db.Text)
    action_plan_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

def get_gemini_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.2, "max_output_tokens": 2048})

def extract_json(raw_text, is_array=False):
    start_char = '[' if is_array else '{'
    end_char = ']' if is_array else '}'
    try:
        start = raw_text.index(start_char)
        end = raw_text.rindex(end_char) + 1
        json_text = raw_text[start:end]
        # Clean control characters
        json_text = re.sub(r'[\x00-\x1f\x7f]', '', json_text)
        return json.loads(json_text)
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        return None

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        transcript = data.get('transcript', '')
        role = data.get('role', 'Employee')

        prompt = f"""
You are an expert psychology analyst. Analyze this supervisor feedback transcript about a {role}.
Return ONLY a valid JSON object. No introduction, no explanation, no markdown formatting outside the JSON.

Extract:
1. An overall sentiment_score (0 to 100, 100 being perfectly positive)
2. A sentiment_label (e.g., "Highly Encouraging", "Constructive", "Critical", etc. max 3 words)
3. Exactly 5 key behavioral findings tailored to their role as a {role}.

For each finding, provide:
- title: A short title (5 words max)
- observation: A behavioral observation (what the supervisor actually said, in your own words)
- score: A score from 1-10 (10 being excellent)
- gap: A gap or suggestion for improvement

Return exactly this JSON format:
{{
  "sentiment_score": 85,
  "sentiment_label": "Highly Encouraging",
  "findings": [
    {{
      "title": "Communication Skills",
      "observation": "Explains ideas clearly to the team",
      "score": 8,
      "gap": "Could improve written communication"
    }}
  ]
}}

Transcript:
{transcript}
"""
        
        try:
            model = get_gemini_model()
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        response = model.generate_content(prompt)
        raw_text = response.text
        print("RAW RESPONSE:", raw_text)

        parsed_data = extract_json(raw_text, is_array=False)
        if not parsed_data:
            # Fallback
            parsed_data = {
                "sentiment_score": 0,
                "sentiment_label": "Error Parse",
                "findings": [{"title": "Parse Error", "observation": raw_text[:300], "score": 0, "gap": "Could not parse response"}]
            }

        # Save to DB
        report = Report(
            role=role,
            transcript=transcript,
            sentiment_score=parsed_data.get('sentiment_score', 0),
            sentiment_label=parsed_data.get('sentiment_label', 'Unknown'),
            findings_json=json.dumps(parsed_data.get('findings', []))
        )
        db.session.add(report)
        db.session.commit()

        # Return the report ID too
        parsed_data['report_id'] = report.id
        return jsonify(parsed_data)

    except Exception as e:
        print("FLASK ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    history = []
    for r in reports:
        history.append({
            "id": r.id,
            "role": r.role,
            "sentiment_score": r.sentiment_score,
            "sentiment_label": r.sentiment_label,
            "created_at": r.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify({"history": history})

@app.route('/report/<int:report_id>', methods=['GET'])
def get_report(report_id):
    report = db.session.get(Report, report_id)
    if not report:
        return jsonify({"error": "Report not found"}), 404
    return jsonify({
        "id": report.id,
        "role": report.role,
        "transcript": report.transcript,
        "sentiment_score": report.sentiment_score,
        "sentiment_label": report.sentiment_label,
        "findings": json.loads(report.findings_json),
        "action_plan": json.loads(report.action_plan_json) if report.action_plan_json else None,
        "created_at": report.created_at.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    try:
        data = request.json
        report_id = data.get('report_id')
        findings = data.get('findings', [])

        if not report_id:
            return jsonify({"error": "report_id is required"}), 400

        report = db.session.get(Report, report_id)
        if not report:
            return jsonify({"error": "Report not found"}), 404

        prompt = f"""
You are an expert HR coach. Based on these finalized feedback findings for a {report.role}, generate two things:
1. "email": A professional, encouraging email draft to send to the employee summarizing the feedback and setting a positive tone.
2. "checklist": An array of 3 to 5 actionable 30-day next steps (strings) to help them improve the identified gaps.

Return ONLY a valid JSON object in this exact format:
{{
  "email": "Subject: ...\\n\\nHi [Name],\\n\\n...",
  "checklist": [
    "Step 1...",
    "Step 2..."
  ]
}}

Findings:
{json.dumps(findings)}
"""
        try:
            model = get_gemini_model()
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        response = model.generate_content(prompt)
        raw_text = response.text
        
        parsed_data = extract_json(raw_text, is_array=False)
        if not parsed_data:
            return jsonify({"error": "Failed to parse Action Plan from AI."}), 500

        # Save action plan to DB
        report.action_plan_json = json.dumps(parsed_data)
        
        # We might also want to update the findings_json in case the user edited them!
        report.findings_json = json.dumps(findings)
        db.session.commit()

        return jsonify(parsed_data)

    except Exception as e:
        print("FLASK ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)