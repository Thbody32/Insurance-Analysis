import fitz  # PyMuPDF
from google import genai
from google.genai import types

class PolicyProcessor:
    def __init__(self, api_key: str, model_name: str = 'gemini-2.5-flash'):
        """Initializes the Gemini client and sets configuration."""
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def extract_text_from_pdf(self, uploaded_file) -> str:
        """Extracts all sequential text from an uploaded PDF stream."""
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        full_text = ""
        for page_num, page in enumerate(doc):
            full_text += f"\n--- START OF PAGE {page_num + 1} ---\n{page.get_text('text')}\n"
        return full_text.strip()

    def parse_policy(self, raw_text: str) -> str:


        prompt = f"""
        You are an expert actuarial data extraction engine. Analyze the following insurance policy text.
        Identify the insurance carrier and extract EVERY single coverage limit and deductible. Group them logically by their respective 'Coverage Part' or line of business.
        
        You must output strictly in JSON format with this exact structural schema:
        {{
            "carrier": "Name of Carrier",
            "coverage_parts": {{
                "Commercial Property": [
                    {{
                        "name": "Building",
                        "limit": 1500000,
                        "deductible": 5000
                    }}
                ]
            }}
        }}
        
        Do not add any conversational markdown formatting wrapper outside of the raw JSON block.
        
        Full Document Text:
        \"\"\"{raw_text}\"\"\"
        """

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            ),
        )
        return response.text

    @staticmethod
    def format_currency(val) -> str:
        """Utility to sanitize and format numeric values for display."""
        if val is None: return "N/A"
        if isinstance(val, (int, float)): return f"${val:,.0f}"
        if isinstance(val, list): return " / ".join([PolicyProcessor.format_currency(x) for x in val])

        val_str = str(val).strip()
        try:
            clean_str = val_str.replace('$', '').replace(',', '').strip()
            num = float(clean_str)
            return f"${int(num):,}" if num.is_integer() else f"${num:,.2f}"
        except ValueError:
            return val_str

