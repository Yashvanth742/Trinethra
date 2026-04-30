trinethra/
├── app.py         # Flask backend — handles transcript analysis via Ollama
├── index.html     # Frontend — transcript input and intern review UI
└── README.md      # Project documentation


Why Ollama (Local LLM)?
Supervisor transcripts contain sensitive employee performance data. Sending this data to cloud AI services like ChatGPT or Claude would be a privacy risk. Ollama runs the AI model entirely on your local machine — nothing leaves your computer.

Tech Stack
LayerTechnologyFrontendHTML, CSS, JavaScriptBackendPython, FlaskAI EngineOllama (LLaMA 3)
Features

Paste any supervisor transcript and get structured findings in seconds
Each finding includes a title, behavioral observation, score out of 10, and improvement gap
Intern can Accept, Edit, or Reject each AI-generated finding
Export final report as a .txt file
