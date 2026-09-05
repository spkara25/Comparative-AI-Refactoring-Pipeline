import os
import pytest
from app.services.dataset_service import DatasetService
from app.models.legacy_dataset import LegacyDataset

def test_dataset_service_loads_files():
    # 1. Define the path we are targeting
    target_dir = "datasets/legacy"
    
    # 2. Use the service to load the directory
    dataset = DatasetService.load_from_directory(target_dir, dataset_id=10, name="Test Legacy")
    
    # 3. Assertions about the dataset object
    assert isinstance(dataset, LegacyDataset)
    assert dataset.dataset_id == 10
    assert len(dataset.get_code()) >= 1 # We should find at least example_01.py
    
    # 4. Find our specific example file in the loaded list
    example_file_path = None
    for file_path in dataset.get_code():
        if "example_01.py" in file_path:
            example_file_path = file_path
            break
            
    assert example_file_path is not None, "example_01.py was not found in the directory!"
    
    # 5. Test reading the actual content
    content = DatasetService.read_code_content(example_file_path)
    assert "def calculate_things" in content
    
    print("\n[SUCCESS] Dataset ingestion works perfectly!")

def test_dataset_service_handles_missing_dir():
    # Verify that pointing to a fake directory raises the correct error
    with pytest.raises(FileNotFoundError):
        DatasetService.load_from_directory("datasets/fake_directory_that_does_not_exist")