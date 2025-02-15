from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import PyPDF2
import io

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))

# Initialize model
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_prompt = request.json.get("prompt")
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    try:
        response = chat.send_message(user_prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/make-notes', methods=['POST'])
def make_notes():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        content = ""
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        # Handle PDF files
        if file_extension == '.pdf':
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
                
        # Handle text files
        elif file_extension in ['.txt', '.doc', '.docx']:
            content = file.read().decode('utf-8')
        else:
            return jsonify({"error": "Unsupported file format. Please upload PDF or text files."}), 400
        
        # Create prompt for summarization
        prompt = f"""Please create concise and structured notes from the following text. 
        Include:
        - Main points and key concepts
        - Important details and examples
        - Any significant conclusions
        
        Text to summarize:
        {content}"""
        
        # Generate notes using Gemini
        response = model.generate_content(prompt)
        
        return jsonify({
            "notes": response.text,
            "filename": file.filename
        })
    except PyPDF2.PdfReadError:
        return jsonify({"error": "Invalid or corrupted PDF file"}), 400
    except UnicodeDecodeError:
        return jsonify({"error": "Please upload a valid text file"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/embed-text', methods=['POST'])
def embed_text():
    return jsonify({"message": "Text embedding feature is coming soon!"})

@app.route('/ask-me-anything', methods=['POST'])
def ask_me_anything():
    return jsonify({"message": "Ask Me Anything feature is coming soon!"})

if __name__ == '__main__':
    app.run(debug=True)