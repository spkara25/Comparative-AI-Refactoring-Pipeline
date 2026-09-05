from dataclasses import dataclass
from typing import List
@dataclass

class LegacyDataset: 
    dataset_id : int
    name : str
    source : str
    description : str
    code_files: List[str]

    def add_code(self, file_path: str):
        self.code_files.append(file_path)

    def remove_code(self, file_path: str):
        if file_path in self.code_files:
            self.code_files.remove(file_path)

    def get_code(self) -> List[str]:
        return self.code_files
    