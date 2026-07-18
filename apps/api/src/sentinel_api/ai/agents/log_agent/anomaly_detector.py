from typing import Any, Dict, List
import structlog

logger = structlog.get_logger("sentinel_api.ai.agents.log_agent.anomaly_detector")


class AnomalyDetector:
    """Detects statistical outliers, rare high-severity logs, and temporal spikes."""

    def detect_anomalies(
        self, parsed_logs: List[Dict[str, Any]], findings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identifies anomalies across parsed logs and finding clusters."""
        logger.info("Beginning anomaly detection scan")

        anomalies: List[Dict[str, Any]] = []
        total_logs = len(parsed_logs)
        if total_logs == 0:
            return anomalies

        # 1. Identify High Frequency Failures
        for f in findings:
            ratio = f["occurrences"] / total_logs
            if ratio > 0.3 and f["level"] in ["ERROR", "CRITICAL", "FATAL"]:
                anomalies.append(
                    {
                        "type": "HIGH_FREQUENCY_FAILURE",
                        "description": f"High-frequency error cluster detected: '{f['template']}' accounts for {ratio:.1%} of all log records.",
                        "severity": "High",
                        "finding_ref": f["template"],
                    }
                )

        # 2. Identify Rare Critical Events
        for f in findings:
            if f["occurrences"] == 1 and f["level"] in ["CRITICAL", "FATAL"]:
                anomalies.append(
                    {
                        "type": "RARE_CRITICAL_EVENT",
                        "description": f"Rare critical event detected: '{f['template']}' occurred only once but carries '{f['level']}' severity.",
                        "severity": "Critical",
                        "finding_ref": f["template"],
                    }
                )

        # 3. Identify Temporal Error Spikes (first half vs second half comparison)
        sorted_logs = sorted(parsed_logs, key=lambda x: x.get("timestamp", ""))
        half = len(sorted_logs) // 2
        if half > 0:
            first_half_errors = sum(
                1
                for x in sorted_logs[:half]
                if x.get("level") in ["ERROR", "CRITICAL", "FATAL"]
            )
            second_half_errors = sum(
                1
                for x in sorted_logs[half:]
                if x.get("level") in ["ERROR", "CRITICAL", "FATAL"]
            )

            if second_half_errors > first_half_errors * 2.5 and second_half_errors > 5:
                anomalies.append(
                    {
                        "type": "SUDDEN_ERROR_SPIKE",
                        "description": (
                            f"Sudden error volume spike detected: Errors increased from"
                            f" {first_half_errors} in the first half to"
                            f" {second_half_errors} in the second half."
                        ),
                        "severity": "High",
                        "finding_ref": "temporal_spike",
                    }
                )

        logger.info("Anomaly scan completed", anomalies_flagged=len(anomalies))
        return anomalies
