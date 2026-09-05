from dataclasses import dataclass

@dataclass
class AIServiceConfig:
    service_id : int 
    service_name : str
    model_version : str
    