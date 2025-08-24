import dotenv
import google.generativeai as genai
import json


from setup_parser import ACCSetup


API_KEY = dotenv.get_key(".env", "GEMINI_API_KEY")

genai.configure(api_key=API_KEY)


def ask_aero_specialist(problem: str, setup=None):
    """Konsultiert den Aerodynamik-Spezialisten bei Problemen mit der Aero-Balance eines Fahrzeugs."""
    _aero_prompt_path = "src/assets/prompts/aero_prompt.txt"
    with open(_aero_prompt_path, "r", encoding="utf-8") as _aero_prompt:
        aero_prompt = _aero_prompt.read()
        aero_prompt += "\n\n"
        aero_prompt += (f"Setup:\n"
                        f" {setup}")

    aero_model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=aero_prompt)

    aero_response = aero_model.generate_content(problem)
    return aero_response.text
def ask_mech_grip_specialist(problem: str, setup=None):
    """Konsultiert den Mechanischen-Grip-Spezialisten bei Problemen mit dem mechanischen Grip eines Fahrzeugs."""
    _mech_prompt_path = "src/assets/prompts/mechanical_grip.txt"
    with open(_mech_prompt_path, "r", encoding="utf-8") as _mechanical_prompt:
        mechanical_prompt = _mechanical_prompt.read()

    mech_model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=mechanical_prompt)

    mech_response = mech_model.generate_content(problem)
    return mech_response.text
def ask_tyre_specialist(problem: str, setup=None):
    """Konsultiert den Reifen-Spezialisten bei Problemen mit Reifen, Sturz, Spur, Nachlauf und so weiter eines Fahrzeugs."""
    _tyre_prompt_path = "src/assets/prompts/tyres_prompt.txt"
    with open(_tyre_prompt_path, "r", encoding="utf-8") as _tyre_prompt:
        tyre_prompt = _tyre_prompt.read()

    tyre_model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=tyre_prompt)

    tyre_response = tyre_model.generate_content(problem)
    return tyre_response.text
def ask_damper_specialist(problem: str, setup=None):
    """Konsultiert den Daempfer-Spezialisten bei Problemen mit den Daempfern eines Fahrzeugs."""
    _damper_prompt_path = "src/assets/prompts/dampers_prompt.txt"
    with open(_damper_prompt_path, "r", encoding="utf-8") as _damper_prompt:
        damper_prompt = _damper_prompt.read()

    damper_model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=damper_prompt)

    damper_response = damper_model.generate_content(problem)
    return damper_response.text
def ask_electronics_specialist(problem: str, setup=None):
    """Konsultiert den Daempfer-Spezialisten bei Problemen mit den Daempfern eines Fahrzeugs."""
    _electronics_prompt_path = "src/assets/prompts/electronics_prompt.txt"
    with open(_electronics_prompt_path, "r", encoding="utf-8") as _electronics_prompt:
        electronics_prompt = _electronics_prompt.read()

    electronics_model= genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=electronics_prompt)

    electronics_response = electronics_model.generate_content(problem)
    return electronics_response.text


class SetupManager:
    def __init__(self, setup_path=""):
        mp_file_path = "src/assets/prompts/manager_prompt.txt"
        with open(mp_file_path, "r", encoding="utf-8") as f:
            self.prompt = f.read()

        self.response = None
        self.acc_setup = None

        if setup_path:
            try:
                self.acc_setup = ACCSetup(setup_path)
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest'
                                              , system_instruction=self.prompt,
                                              tools=[ask_aero_specialist,
                                                     ask_tyre_specialist,
                                                     ask_damper_specialist,
                                                     ask_electronics_specialist,
                                                     ask_mech_grip_specialist,
                                                     self.acc_setup.get_setup,
                                                     self.acc_setup.get_mechanical_balance,
                                                     self.acc_setup.get_aero,
                                                     self.acc_setup.get_tyres_and_alignment,
                                                     self.acc_setup.get_dampers,
                                                     self.acc_setup.get_electronics
                                                     ]
                                              )

            except Exception as e:
                print(e)
                print("Es konnte kein Setup geladen werden!")

        else:
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest'
                                              , system_instruction=self.prompt,
                                              tools=[ask_aero_specialist,
                                                     ask_tyre_specialist,
                                                     ask_damper_specialist,
                                                     ask_electronics_specialist,
                                                     ask_mech_grip_specialist])

        self.chat = self.model.start_chat()

    def set_setup(self, setup:json):
        history = self.chat.history
        if not self.chat.history:
            history = self.prompt

        try:
            self.acc_setup = ACCSetup(setup)

            self.model = genai.GenerativeModel('gemini-1.5-flash-latest'
                                               , system_instruction=history,
                                               tools=[ask_aero_specialist,
                                                      ask_tyre_specialist,
                                                      ask_damper_specialist,
                                                      ask_electronics_specialist,
                                                      ask_mech_grip_specialist,
                                                      self.acc_setup.get_setup,
                                                      self.acc_setup.get_mechanical_balance,
                                                      self.acc_setup.get_aero,
                                                      self.acc_setup.get_tyres_and_alignment,
                                                      self.acc_setup.get_dampers,
                                                      self.acc_setup.get_electronics
                                                      ]
                                               )
            return True
        except Exception as e:
            print(e)
            print("Es konnte kein Setup geladen werden!")
        return False

    def send_function_response(self, chat, tool_name, payload_dict):
        pass

    def find_function_call(self, response):
        for part in response.candidates[0].content.parts:
            if part.function_call:
                return part.function_call

        return None

    def send_function_response(self, chat, tool_name, payload_dict):

        chat.send_message(
            content=[genai.protos.Part(
                function_response=genai.protos.FunctionResponse(
                    name=tool_name,
                    response={'result': tool_response}
                )
            )]
        )

    def ask(self, message:str):
        response = self.chat.send_message(message)
        found_tool_call = False
        final_response = ""
        max_func_calls = 2
        func_calls = 0

        while func_calls < max_func_calls:
            print(response.candidates[0].content.parts)
            last_parts = response.candidates[0].content.parts[0]

            # Falls die letzte Antwort der ai kein function call war, wird abgebrochen.
            if not last_parts.function_call:
                break

            # Instanzieren der temporären Variablen des Parts.
            function_call = last_parts.function_call
            tool_name = function_call.name
            tool_args = function_call.args
            print(f"-> Manager ruft auf: {tool_name}")
            tool_response = None

            if tool_name == "ask_aero_specialist":
                tool_response = ask_aero_specialist(**tool_args)
            elif tool_name == "ask_mech_grip_specialist":
                tool_response = ask_mech_grip_specialist(**tool_args)
            elif tool_name == "ask_tyre_specialist":
                tool_response = ask_tyre_specialist(**tool_args)
            elif tool_name == "ask_damper_specialist":
                tool_response = ask_damper_specialist(**tool_args)
            elif tool_name == "ask_electronics_specialist":
                tool_response = ask_electronics_specialist(**tool_args)

            elif tool_name == "get_tyres_and_alignment":
                tool_response = self.acc_setup.get_tyres_and_alignment()
                if isinstance(tool_response, dict):
                    tool_response = json.dumps(tool_response)
            elif tool_name == "get_setup":
                tool_response = self.acc_setup.get_setup()
                if isinstance(tool_response, dict):
                    tool_response = json.dumps(tool_response)
            elif tool_name == "get_mechanical_grip":
                tool_response = self.acc_setup.get_mechanical_balance()
                if isinstance(tool_response, dict):
                    tool_response = json.dumps(tool_response)
            elif tool_name == "get_aero":
                tool_response = self.acc_setup.get_aero()
                if isinstance(tool_response, dict):
                    tool_response = json.dumps(tool_response)
            elif tool_name == "get_dampers":
                tool_response = self.acc_setup.get_dampers()
                if isinstance(tool_response, dict):
                    tool_response = json.dumps(tool_response)
            elif tool_name == "get_electronics":
                tool_response = self.acc_setup.get_electronics()
                if isinstance(tool_response, dict):
                    tool_response = json.dumps(tool_response)

            if tool_response:
                final_response = self.chat.send_message(
                    content=[genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=tool_name,
                            response={'result': tool_response}
                        )
                    )]
                )
                response = final_response
                func_calls += 1

            else:
                print(f"Fehler: Werkzeug {tool_name} nicht gefunden")
                break

        return response.text



if __name__ == "__main__":


    setup_path = "src/assets/setups/SPA RACE BERNA 24 32.json"
    setup_manager = SetupManager(setup_path=setup_path)
    #setup_manager = SetupManager()
    while True:
        user_input = input("Beschreibe dein Problem:\n")
        if user_input == "e":
            break

        print(setup_manager.ask(user_input))
