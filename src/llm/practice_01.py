import dotenv
from google import genai
from google.genai import types
from google.genai import Client

from src.logger import get_logger
logger = get_logger(
    "my_app",
    level="DEBUG",          # oder via Umgebungsvariable LOG_LEVEL=DEBUG
    log_file="../../logs/app.log",
    to_console=False,
    json_console=False,     # True = JSON in der Konsole
    json_file=False         # True = JSON in der Datei
)

logger.info("App startet…")
logger.debug("Konfiguration geladen", extra={})

api_key = dotenv.get_key("../../.env", "GEMINI_API_KEY")


with Client(api_key=api_key) as client:
    schema = {
        "type": "OBJECT",
        "required": ["kernfelder_beschreibungen"],
        "properties": {
            "kernfelder_beschreibungen": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "name": {"type": "STRING"},
                        "beschreibung": {"type": "STRING"}
                    },
                    "required": ["name", "beschreibung"]
                }
            }
        }
    }
    client_config = types.GenerateContentConfig(
        temperature=0.9,
        max_output_tokens=512,
        response_mime_type="application/json",
        response_schema=schema
    )

    prompt = """
    Erkläre die 5 Kernfelder der Fahrzeugbeherrschung eines Rennfahrers. Halte dich kurz und knapp und stichpunktartig.
    """
    response_1 = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=client_config
    )

    print(response_1.text)