from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.engine import Engine

class DatabaseRepository:
    """
    Handles persistence of experiment artifacts and evaluation metrics.
    """

    def __init__(self, engine: Engine):
        self.engine = engine

    def init_schema(self):
        """Initializes tables for SQLite or MySQL."""
        with self.engine.begin() as conn:
            # Dialect-agnostic baseline setup
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS researchers (
                    researcher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL
                );
            """ if self.engine.dialect.name == "sqlite" else """
                CREATE TABLE IF NOT EXISTS researchers (
                    researcher_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS evaluation_metrics (
                    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cyclomatic_complexity REAL NOT NULL,
                    halstead_volume REAL NOT NULL,
                    maintainability_index REAL NOT NULL,
                    test_pass_rate REAL NOT NULL,
                    coverage_percentage REAL NOT NULL
                );
            """ if self.engine.dialect.name == "sqlite" else """
                CREATE TABLE IF NOT EXISTS evaluation_metrics (
                    metric_id INT AUTO_INCREMENT PRIMARY KEY,
                    cyclomatic_complexity FLOAT NOT NULL,
                    halstead_volume FLOAT NOT NULL,
                    maintainability_index FLOAT NOT NULL,
                    test_pass_rate FLOAT NOT NULL,
                    coverage_percentage FLOAT NOT NULL
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS experiment_results (
                    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_date TEXT NOT NULL,
                    summary TEXT,
                    researcher_id INTEGER,
                    model_name TEXT,
                    original_metric_id INTEGER,
                    refactored_metric_id INTEGER
                );
            """ if self.engine.dialect.name == "sqlite" else """
                CREATE TABLE IF NOT EXISTS experiment_results (
                    result_id INT AUTO_INCREMENT PRIMARY KEY,
                    experiment_date DATETIME NOT NULL,
                    summary TEXT,
                    researcher_id INT,
                    model_name VARCHAR(255),
                    original_metric_id INT,
                    refactored_metric_id INT
                );
            """))

    def save_researcher(self, name: str, email: str) -> int:
        with self.engine.begin() as conn:
            # Check if researcher already exists
            check_stmt = text("SELECT researcher_id FROM researchers WHERE email = :email")
            existing = conn.execute(check_stmt, {"email": email}).first()
            if existing:
                return existing[0]

            stmt = text("INSERT INTO researchers (name, email) VALUES (:name, :email)")
            result = conn.execute(stmt, {"name": name, "email": email})
            return result.lastrowid
        
    def save_evaluation_metrics(
        self,
        cyclomatic_complexity: float,
        halstead_volume: float,
        maintainability_index: float,
        test_pass_rate: float,
        coverage_percentage: float
    ) -> int:
        with self.engine.begin() as conn:
            stmt = text("""
                INSERT INTO evaluation_metrics (
                    cyclomatic_complexity, halstead_volume, maintainability_index,
                    test_pass_rate, coverage_percentage
                ) VALUES (
                    :cc, :hv, :mi, :pass_rate, :cov
                )
            """)
            result = conn.execute(stmt, {
                "cc": cyclomatic_complexity,
                "hv": halstead_volume,
                "mi": maintainability_index,
                "pass_rate": test_pass_rate,
                "cov": coverage_percentage
            })
            return result.lastrowid

    def save_experiment_result(
        self,
        summary: str,
        researcher_id: int,
        model_name: str,
        original_metric_id: int,
        refactored_metric_id: int,
        experiment_date: Optional[datetime] = None
    ) -> int:
        date_val = (experiment_date or datetime.now()).isoformat()
        with self.engine.begin() as conn:
            stmt = text("""
                INSERT INTO experiment_results (
                    experiment_date, summary, researcher_id, model_name,
                    original_metric_id, refactored_metric_id
                ) VALUES (
                    :exp_date, :summary, :res_id, :model, :orig_id, :refact_id
                )
            """)
            result = conn.execute(stmt, {
                "exp_date": date_val,
                "summary": summary,
                "res_id": researcher_id,
                "model": model_name,
                "orig_id": original_metric_id,
                "refact_id": refactored_metric_id
            })
            return result.lastrowid

    def get_experiment_result(self, result_id: int) -> Optional[Dict[str, Any]]:
        with self.engine.connect() as conn:
            stmt = text("SELECT * FROM experiment_results WHERE result_id = :result_id")
            row = conn.execute(stmt, {"result_id": result_id}).mappings().first()
            return dict(row) if row else None