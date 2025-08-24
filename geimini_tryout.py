import dotenv
from google import genai
from google.genai import types
from setup_parser import ACCSetup
import json


from logger import get_logger

logger = get_logger(
    "my_app",
    level="DEBUG",          # oder via Umgebungsvariable LOG_LEVEL=DEBUG
    log_file="logs/app.log",
    to_console=False,
    json_console=False,     # True = JSON in der Konsole
    json_file=False         # True = JSON in der Datei
)

logger.info("App startet…")
logger.debug("Konfiguration geladen", extra={})


api_key = dotenv.get_key(".env", "GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def get_setup()-> str:
    """
    Gets the setup file and returns all necessary data.
    :return: complete Setup from a race car in Assetto Corsa Competizione
    """
    acc_setup = ACCSetup()

    return json.dumps(acc_setup.get_setup())

"""
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Tell me how the internet works, but pretend I'm a puppy who only understands squeaky toys. Keep it short.",
    config=types.GenerateContentConfig(
        temperature=0.4,
        top_p=0.95,
        top_k=20,
        candidate_count=1,
        seed=5,
        stop_sequences=["STOP!"],
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )
)

"""

system_instruction = """

    **Aufgabe**
    Du bist ein professioneller und methodischer Renningenieur für Assetto Corsa Competizione. 
    Deine Aufgabe ist es, das Problem des Fahrers zu analysieren und einzelne, präzise Setup-Änderung vorzuschlagen.
    
    **Hintergrundinformationen**
    Meta-Leitlinien (ACC GT3):
    Reifen: Optimum 26–27 PSI heiß (trocken), 30–31 PSI (nass). Drücke nach ein paar Runden ins Ziel bringen.
    Quali-Setups: Aggressiv → max Sturz, wenig Flügel, spitze Spurwerte, harte Stabis, niedriger Tank. Fokus: maximale Rotation & Grip auf 1 Runde.
    Race-Setups: Stabil & konstant → etwas mehr Flügel, moderater Sturz/Spur, weichere ARBs/Dämpfer, Fokus auf Reifenhaltbarkeit & leichter Untersteuer-Tendenz. Tankgewicht berücksichtigen.
    Regen-Setups: Max Flügel, Auto höher legen, weiches Fahrwerk, weniger Sturz/nahe 0 Spur, TC & ABS hoch, Bias leicht nach hinten. Ziel: Traktion & Sicherheit.
    
    **Vorgehenseweise**
    **WICHTIG!**
    Halte dich strikt an folgende Reihenfolge:
    1. Du analysierst immer zuerst das Setup und nutzt die 'get_setup' Function. Die Reifendrücke kommen aus der Setup-Date, rechne sie nicht um.
    2. Du nutzt die Werte im setup file so, wie sie dort stehen.
    3. Danach analysierst du die Anmerkungen des Fahrers auf das Setup und die Gesamtsituation
    und gibst eine Empfehlung an den Fahrer zurück.
    
    Du darfst maximal 5 Parameter (wie z.B. rearWing, rearArb...) um einen kleinen Wert ändern. Deine Änderungen müssen nachvollziehbar,
    für die ganze Strecke von Vorteil und passend zur Meta von ACC sein (siehe Meta-Leitfaden). 
    

    **Ausgabeformat**   
        **Change**: 
            {'Setup-Changes':{
                'Setup-Parameter 01': 'STRING'{
                    'Old Value': 'STRING',
                    'New Value': 'STRING',}
                'Setup-Parameter 02': 'STRING'{
                    'Old Value': 'STRING',
                    'New Value': 'STRING',}
                'Setup_Parameter 03...{...}
             }
        }
        **Explanation**
        Erkläre kurz in Worten, was du gemacht hast.
    
"""

tool_hashmap = {"get_setup": get_setup}


get_car_setup = types.FunctionDeclaration(
    name="get_setup",
    description="Use this function to get all necessary data from the ACC setup file.",
    parameters={
        "type": "OBJECT",
        "properties": {} },
)

get_setup_tool = types.Tool(
    function_declarations=[get_car_setup],
)

chat_config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    tools=[get_setup_tool],
    temperature=0.2
)

chat = client.chats.create(
    model="gemini-2.0-flash",
    config=chat_config,

)


# Ab hier beginnt der Chatverlauf.


response = chat.send_message(input("Hi, ich bin Speedy-Boy dein Renningenieur, was kann ich für dich tun?\n"))

parts = response.candidates[0].content.parts
logger.debug("Parts: %s", [p.__dict__.keys() for p in parts])

tool_call_part = next((p for p in parts if getattr(p, "function_call", None)), None)

if tool_call_part:
    # Wenn die AI also eine Funktion nutzen möchte, wird diese Kondition True und wir verarbeiten die Anfrage.
    # Die AI gibt uns nur einen Text aus, sie weiß auch, dass sie ein paar Parameter ggf. braucht. Mit einer If-Abfrage oder besser
    # einer HashMap können wir die Anfrage abfangen und den Code in unserem Backend ausführen.
    # Dann senden wir das Ergebnis des Codes wieder zurück an die AI und erhalten daraufhin unsere Antwort.
    # Wir bauen quasi die Schnittstelle zwischen AI und Funktion.


    print(f" -> Das war ein Function Call!\nlast_response: {tool_call_part}")
    tool_name = tool_call_part.function_call.name
    tool_args = tool_call_part.function_call.args

    try:
        tool_response_data = tool_hashmap[tool_name]()
        print(f"Setup-Daten erfolgreich geladen: {tool_response_data}")
        logger.info(f"Setup-Daten erfolgreich geladen: {tool_response_data}")

        final_response = chat.send_message(
            types.Part.from_function_response(
                name=tool_name,
                response={
                    "setup": tool_response_data
                }
            )
        )

        print("\n-------- Antwort des Renningenieurs -------------")
        print(final_response.text)
        logger.info(f"Final Response after the function Call:\n{final_response}")
    except Exception as e:
        print(f"{e}\n\nCould not find tool: '{tool_name}' in 'tool_hashmap'")

else:
    print(f"Das war kein Function-Call:\n{response.text}")

