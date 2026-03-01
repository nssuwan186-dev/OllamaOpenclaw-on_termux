import pdfplumber
import sys
import json

def extract_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "
"
            return {"status": "success", "content": text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No file path provided"}))
    else:
        print(json.dumps(extract_pdf(sys.argv[1])))
