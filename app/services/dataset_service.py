import os
from app.models.legacy_dataset import LegacyDataset

class DatasetService:
    """
    Handles the discovery, loading, and reading of legacy source code files.
    """

    @staticmethod
    def load_from_directory(directory_path: str, dataset_id: int = 1, name: str = "Local Directory") -> LegacyDataset:
        """Scans a directory for .py files and creates a LegacyDataset."""
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"The directory '{directory_path}' does not exist.")

        dataset = LegacyDataset(
            dataset_id=dataset_id,
            name=name,
            source=directory_path,
            description="Auto-loaded local dataset",
            code_files=[]
        )

        # Walk through the directory to find Python files
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    dataset.add_code(full_path)

        return dataset

    @staticmethod
    def read_code_content(file_path: str) -> str:
        """Reads and returns the raw string content of a code file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
            
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()