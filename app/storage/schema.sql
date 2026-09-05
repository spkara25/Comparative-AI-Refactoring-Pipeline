-- Schema for Comparative AI Refactoring Pipeline

CREATE TABLE IF NOT EXISTS researchers (
    researcher_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS legacy_datasets (
    dataset_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    source VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS prompt_configurations (
    prompt_id INT AUTO_INCREMENT PRIMARY KEY,
    prompt_text TEXT NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    temperature FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS refactoring_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id INT,
    prompt_id INT,
    original_code MEDIUMTEXT NOT NULL,
    language VARCHAR(50) DEFAULT 'Python',
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (dataset_id) REFERENCES legacy_datasets(dataset_id) ON DELETE SET NULL,
    FOREIGN KEY (prompt_id) REFERENCES prompt_configurations(prompt_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS refactored_codes (
    code_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT,
    code_content MEDIUMTEXT NOT NULL,
    language VARCHAR(50) DEFAULT 'Python',
    FOREIGN KEY (request_id) REFERENCES refactoring_requests(request_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evaluation_metrics (
    metric_id INT AUTO_INCREMENT PRIMARY KEY,
    cyclomatic_complexity FLOAT NOT NULL,
    halstead_volume FLOAT NOT NULL,
    maintainability_index FLOAT NOT NULL,
    test_pass_rate FLOAT NOT NULL,
    coverage_percentage FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS experiment_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    experiment_date DATETIME NOT NULL,
    summary TEXT,
    researcher_id INT,
    request_id INT,
    refactored_code_id INT,
    original_metric_id INT,
    refactored_metric_id INT,
    FOREIGN KEY (researcher_id) REFERENCES researchers(researcher_id) ON DELETE SET NULL,
    FOREIGN KEY (request_id) REFERENCES refactoring_requests(request_id) ON DELETE CASCADE,
    FOREIGN KEY (refactored_code_id) REFERENCES refactored_codes(code_id) ON DELETE CASCADE,
    FOREIGN KEY (original_metric_id) REFERENCES evaluation_metrics(metric_id) ON DELETE SET NULL,
    FOREIGN KEY (refactored_metric_id) REFERENCES evaluation_metrics(metric_id) ON DELETE SET NULL
);