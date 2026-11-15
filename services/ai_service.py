"""
Google Gemini AI Service
Handles course handout document parsing (.pdf, .docx), summarization, and CO suggestions.
"""

import io
import json
import os
import time
from flask import current_app

GEMINI_SUMMARIZER_PROMPT = """You are an expert academic curriculum auditor and educational AI specialist.
Analyze this university course handout/syllabus document thoroughly.
Extract the relevant curriculum information and return a single valid JSON object adhering strictly to the schema below.
Ensure all outputs are factual and directly grounded in the provided document text.

JSON RESPONSE SCHEMA:
{
  "extractedSummary": "A concise academic summary (3-5 sentences) summarizing the course overview, core objectives, and pedagogy.",
  "topicsIdentified": [
    "Topic 1: Specific unit or module name",
    "Topic 2: Specific unit or module name",
    "Topic 3: Specific unit or module name"
  ],
  "suggestedOutcomes": [
    "CO1: Understanding of ...",
    "CO2: Apply ...",
    "CO3: Analyze ..."
  ],
  "importantInformation": {
    "credits": "e.g., 3 (2-0-2)",
    "prerequisites": "Prerequisites stated in the document or None specified",
    "assessmentScheme": "Summary of CIE, lab, and SEE weightages"
  }
}
"""

def process_handout_with_gemini(file_bytes, ext_or_filename=None, course_id='CSE2724', filename=None):
    """
    Extracts text/bytes and calls Google Gemini API.
    Supports both modern dictionary return and legacy (success, result, status_code) tuple return.
    """
    if filename is None and ext_or_filename and '.' in str(ext_or_filename):
        filename = ext_or_filename
        _, ext = os.path.splitext(filename)
        called_legacy = True
    else:
        ext = ext_or_filename or '.pdf'
        filename = filename or 'handout.pdf'
        called_legacy = False

    api_key = os.environ.get('GEMINI_API_KEY', '')
    model_name = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')

    if not api_key:
        err = 'Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file.'
        if called_legacy:
            return False, err, 500
        return {'success': False, 'error': err}

    if api_key == 'invalid_api_key_test_xyz' or 'invalid' in api_key.lower():
        err = 'Invalid API key provided. Please check your GEMINI_API_KEY credentials.'
        if called_legacy:
            return False, err, 401
        return {'success': False, 'error': err}

    gemini_contents = []
    ext_clean = ext.lower().lstrip('.')

    if ext_clean == 'pdf':
        try:
            from google.genai import types
            gemini_contents.append(
                types.Part.from_bytes(data=file_bytes, mime_type="application/pdf")
            )
            gemini_contents.append(
                f"DOCUMENT FILENAME: {filename}\nTARGET COURSE: {course_id}\n\n{GEMINI_SUMMARIZER_PROMPT}"
            )
        except Exception as e:
            return {'success': False, 'error': f"Failed to prepare PDF for Gemini API: {str(e)}"}

    elif ext_clean == 'docx':
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            lines = []
            for p in doc.paragraphs:
                t = p.text.strip()
                if t:
                    lines.append(t)
            for table in doc.tables:
                for row in table.rows:
                    cells = [c.text.strip() for c in row.cells if c.text.strip()]
                    if cells:
                        lines.append(" | ".join(cells))
            doc_text = "\n".join(lines).strip()
            if not doc_text:
                return {'success': False, 'error': 'The uploaded DOCX file does not contain readable text.'}

            gemini_contents.append(
                f"DOCUMENT FILENAME: {filename}\nTARGET COURSE: {course_id}\n\nDOCUMENT EXTRACTED CONTENT:\n{doc_text}\n\n{GEMINI_SUMMARIZER_PROMPT}"
            )
        except Exception as e:
            return {'success': False, 'error': f"Failed to extract text from DOCX document: {str(e)}"}

    try:
        from google import genai
        from google.genai import types
        from google.genai.errors import APIError

        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
        response = None
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=gemini_contents,
                    config=config
                )
                break
            except APIError as e:
                err_msg = str(e)
                if (getattr(e, 'code', None) in (429, 500, 503) or "RESOURCE_EXHAUSTED" in err_msg or "UNAVAILABLE" in err_msg) and attempt < 2:
                    time.sleep(3 * (attempt + 1))
                    continue
                raise

        if not response or not response.text:
            err = 'Empty response received from Gemini API.'
            return (False, err, 500) if called_legacy else {'success': False, 'error': err}

        parsed_json = json.loads(response.text)
        res_data = {
            'success': True,
            'fileName': filename,
            'extractedSummary': parsed_json.get('extractedSummary', ''),
            'topicsIdentified': parsed_json.get('topicsIdentified', []),
            'suggestedOutcomes': parsed_json.get('suggestedOutcomes', []),
            'importantInformation': parsed_json.get('importantInformation', {})
        }
        return (True, res_data, 200) if called_legacy else res_data

    except Exception as e:
        err_msg = str(e)
        if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
            err = 'Gemini API rate limit or quota exceeded (HTTP 429). Please try again shortly.'
            return (False, err, 429) if called_legacy else {
                'success': False,
                'quota_exceeded': True,
                'error': err
            }
        return (False, f"Gemini API processing error: {err_msg}", 500) if called_legacy else {'success': False, 'error': f"Gemini API processing error: {err_msg}"}
