from typing import List, Dict, Any, Tuple

class GithubRiskAnalyzer:
    """Analyzes the risk of a deployment or commit based on file changes."""
    
    HIGH_RISK_FILES = [
        "package.json", "yarn.lock", "package-lock.json", # Node Dependencies
        "requirements.txt", "Pipfile", "poetry.lock", # Python Dependencies
        "go.mod", "go.sum", # Go Dependencies
        "pom.xml", "build.gradle", # Java Dependencies
        "Dockerfile", "docker-compose.yml", ".dockerignore", # Container changes
        ".env", ".env.example", ".env.production", # Configuration
        "serverless.yml", "template.yaml", # Infrastructure as Code
    ]
    
    MIGRATION_DIRECTORIES = [
        "alembic/versions/",
        "migrations/",
        "prisma/migrations/",
        "db/migrate/"
    ]
    
    @classmethod
    def analyze_risk(cls, files_changed: List[str]) -> Tuple[float, List[str]]:
        """
        Calculates a risk score from 0.0 to 1.0.
        Returns the score and a list of identified risk factors.
        """
        if not files_changed:
            return 0.0, []
            
        risk_score = 0.0
        risk_factors = []
        
        # Base risk from volume of changes
        if len(files_changed) > 50:
            risk_score += 0.4
            risk_factors.append("High volume of changed files (>50)")
        elif len(files_changed) > 20:
            risk_score += 0.2
            risk_factors.append("Moderate volume of changed files (>20)")
            
        # Check for dependency / config / infra changes
        has_config_change = False
        has_migration = False
        
        for file_path in files_changed:
            filename = file_path.split("/")[-1]
            
            # Check high risk files
            if filename in cls.HIGH_RISK_FILES:
                if not has_config_change:
                    risk_score += 0.3
                    risk_factors.append(f"Critical configuration or dependency changes detected (e.g. {filename})")
                    has_config_change = True
                    
            # Check DB migrations
            for mig_dir in cls.MIGRATION_DIRECTORIES:
                if mig_dir in file_path:
                    if not has_migration:
                        risk_score += 0.4
                        risk_factors.append(f"Database migration detected ({filename})")
                        has_migration = True
                        break
        
        # Cap at 1.0
        risk_score = min(risk_score, 1.0)
        
        return risk_score, risk_factors
