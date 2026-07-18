from sentinel_api.app.reporting.schemas import IncidentReport


class JsonExporter:
    """Exports the unified Incident Report to JSON format."""

    def export(self, report: IncidentReport) -> str:
        """Serializes the IncidentReport model to a pretty JSON string."""
        return report.model_dump_json(indent=2)
