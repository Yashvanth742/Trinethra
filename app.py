import os
from flask import Flask, request, jsonify, send_from_directory
import json
import google.generativeai as genai
app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        transcript = data.get('transcript', '')

        prompt = f"""
You are an expert psychology analyst. Analyze this supervisor feedback transcript about a Fellow (employee).
IMPORTANT: Return ONLY the JSON array. No introduction, no explanation, no extra text. Start your response with [ and end with ].
Extract exactly 5 key behavioral findings. For each finding, provide:
1. A short title (5 words max)
2. A behavioral observation (what the supervisor actually said, in your own words)
3. A score from 1-10 (10 being excellent)
4. A gap or suggestion for improvement

Return ONLY a JSON array like this, nothing else:
[
  {{
    "title": "Communication Skills",
    "observation": "Fellow explains ideas clearly to the team",
    "score": 8,
    "gap": "Could improve written communication"
  }}
]

Transcript:
{transcript}
"""

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"error": "GEMINI_API_KEY environment variable is not set. Please set it in Cloud Run to use the AI features."}), 400

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.2, "max_output_tokens": 2048})
        
        response = model.generate_content(prompt)
        raw_text = response.text

        print("RAW RESPONSE:", raw_text)

        try:
            start = raw_text.index('[')
            end = raw_text.rindex(']') + 1
            json_text = raw_text[start:end]
            findings = json.loads(json_text)
        except ValueError:
            # Handle case where ']' might be missing because it got cut off
            try:
                start = raw_text.index('[')
                json_text = raw_text[start:].strip()
                if json_text.endswith(','):
                    json_text = json_text[:-1]
                if not json_text.endswith(']'):
                    json_text += ']'
                findings = json.loads(json_text)
            except Exception as e:
                print("PARSE ERROR (Truncated Fix Failed):", e)
                findings = [{"title": "Parse Error", "observation": raw_text[:300], "score": 0, "gap": "Could not parse response"}]
        except json.JSONDecodeError:
            # Try cleaning the text and parsing again
            try:
                import re
                json_text = re.sub(r'[\x00-\x1f\x7f]', '', json_text)
                findings = json.loads(json_text)
            except Exception as e:
                print("PARSE ERROR (Decode Error):", e)
                findings = [{"title": "Parse Error", "observation": raw_text[:300], "score": 0, "gap": "Could not parse response"}]
        except Exception as e:
            print("PARSE ERROR:", e)
            findings = [{"title": "Parse Error", "observation": raw_text[:300], "score": 0, "gap": "Could not parse response"}]
        return jsonify({"findings": findings})

    except Exception as e:
        print("FLASK ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)