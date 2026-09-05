from dataclasses import dataclass 

@dataclass
class PromptConfiguration:
    prompt_id : int
    prompt_text : str
    model_name : str
    temperature : float

    def configure_prompt(self, text: str, temp: float):
        self.prompt_text = text
        self.temperature = temp 

    def validate_prompt(self) -> bool:
        return len(self.prompt_text.strip()) >0