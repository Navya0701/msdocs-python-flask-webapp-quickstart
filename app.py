import os
import traceback
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS to allow frontend access (adjust this if needed)
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://black-cliff-051a7af1e.4.azurestaticapps.net"
).split(",")
CORS(
    app,
    resources={r"/chat": {"origins": allowed_origins}},
    supports_credentials=True
)

# Path to vector store (kept for reference)
vecstore_path = '/home/filesharemount'


@app.route('/')
def main_page():
    """Basic welcome route"""
    return 'Hello there! Welcome to MedCopilot — your medical guidelines assistant!'


@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Main API endpoint to handle chat messages"""
    if request.method == 'OPTIONS':
        return ('', 204)

    if not request.is_json:
        return jsonify({"error": "Invalid request. Expected JSON body."}), 400

    body = request.get_json(silent=True) or {}
    message = body.get('message')

    if not message:
        return jsonify({"error": "Missing 'message' in JSON body."}), 400

    print(f"📩 Received message: {message}")

    try:
        # ✅ Updated: Use new Azure API endpoint
        api_url = f"https://dmiqcoresvc.azurewebsites.net/api/v1/testq?question={message}"
        print(f"🌐 Calling external API: {api_url}")

        external_response = requests.get(api_url)

        if external_response.status_code != 200:
            print(f"⚠️ External API returned {external_response.status_code}")
            return jsonify({
                "error": f"External API returned status {external_response.status_code}",
                "details": external_response.text
            }), 500

        # ✅ Safe JSON parsing (in case Azure returns plain text)
        try:
            api_data = external_response.json()
        except Exception:
            api_data = {"answer": external_response.text}

        print("✅ Azure API Response:", api_data)
        return jsonify(api_data)

    except Exception as e:
        print("❌ ERROR in /chat handler:")
        print(traceback.format_exc())
        return jsonify({
            "error": "An error occurred while processing your request.",
            "details": str(e)
        }), 500


def serialize(result):
    """
    Safely convert inference output into a JSON serializable dict.
    (Kept for potential future local inference use)
    """
    try:
        if isinstance(result, dict):
            input_text = result.get('input', "")
            answer = result.get('answer', str(result))
            context_items = result.get('context', [])

            context_list = []
            for item in context_items:
                context_dict = {
                    "metadata": getattr(item, "metadata", {}),
                    "page_content": getattr(item, "page_content", str(item))
                }
                context_list.append(context_dict)

            return {
                "input": input_text,
                "answer": answer,
                "context": context_list
            }

        elif isinstance(result, str):
            return {"input": "", "answer": result, "context": []}

        else:
            return {
                "input": "",
                "answer": str(result),
                "context": []
            }

    except Exception as e:
        print("⚠️ Error during serialization:", e)
        return {
            "input": "",
            "answer": "An internal error occurred during serialization.",
            "context": []
        }


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
