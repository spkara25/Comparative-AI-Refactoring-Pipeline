from dataclasses import dataclass 

@dataclass
class Researcher:
    researcher_id : int
    name : str
    email : str
    def manage_dataset(self):
        pass

    def configure_prompt(self):
        pass

    def submit_refactoring_request(self):
        pass

    def generate_comparison_report(self):
        pass
    