import datetime
from typing import Dict, Any, List

class OTLPParser:
    """Parses OpenTelemetry (OTLP) JSON/Protobuf payloads into Sentinel internal formats."""

    @staticmethod
    def _parse_time_unix_nano(unix_nano: str) -> datetime.datetime:
        """Converts OTLP Unix Nano timestamp to datetime."""
        try:
            return datetime.datetime.utcfromtimestamp(int(unix_nano) / 1e9)
        except (ValueError, TypeError):
            return datetime.datetime.utcnow()

    @staticmethod
    def _extract_attributes(attributes_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Converts OTLP KeyValue list to a standard Python dictionary."""
        attrs = {}
        if not attributes_list:
            return attrs
        for attr in attributes_list:
            key = attr.get("key")
            value_dict = attr.get("value", {})
            
            # OTLP values can be stringValue, intValue, boolValue, doubleValue, etc.
            val = None
            if "stringValue" in value_dict:
                val = value_dict["stringValue"]
            elif "intValue" in value_dict:
                val = value_dict["intValue"]
            elif "boolValue" in value_dict:
                val = value_dict["boolValue"]
            elif "doubleValue" in value_dict:
                val = value_dict["doubleValue"]
            else:
                val = str(value_dict)
            
            if key:
                attrs[key] = val
        return attrs

    @classmethod
    def parse_traces(cls, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parses OTLP ExportTraceServiceRequest JSON payload into flat spans."""
        spans_out = []
        
        resource_spans = payload.get("resourceSpans", [])
        for rs in resource_spans:
            resource = rs.get("resource", {})
            resource_attrs = cls._extract_attributes(resource.get("attributes", []))
            
            scope_spans = rs.get("scopeSpans", [])
            for ss in scope_spans:
                spans = ss.get("spans", [])
                for span in spans:
                    
                    start_time = cls._parse_time_unix_nano(span.get("startTimeUnixNano", 0))
                    end_time = cls._parse_time_unix_nano(span.get("endTimeUnixNano", 0))
                    duration_ms = (end_time - start_time).total_seconds() * 1000
                    
                    # Parse Span Events
                    events_out = []
                    for event in span.get("events", []):
                        events_out.append({
                            "name": event.get("name"),
                            "timestamp": cls._parse_time_unix_nano(event.get("timeUnixNano", 0)).isoformat(),
                            "attributes": cls._extract_attributes(event.get("attributes", []))
                        })

                    # Parse Span Links
                    links_out = []
                    for link in span.get("links", []):
                        links_out.append({
                            "linked_trace_id": link.get("traceId"),
                            "linked_span_id": link.get("spanId"),
                            "attributes": cls._extract_attributes(link.get("attributes", []))
                        })
                    
                    status = span.get("status", {})

                    spans_out.append({
                        "trace_id": span.get("traceId"),
                        "span_id": span.get("spanId"),
                        "parent_span_id": span.get("parentSpanId"),
                        "name": span.get("name"),
                        "kind": str(span.get("kind", "UNSET")),
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "duration_ms": duration_ms,
                        "status_code": status.get("code", "UNSET"),
                        "status_message": status.get("message"),
                        "span_attributes": cls._extract_attributes(span.get("attributes", [])),
                        "resource_attributes": resource_attrs,
                        "events": events_out,
                        "links": links_out
                    })
        return spans_out

    @classmethod
    def parse_metrics(cls, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parses OTLP ExportMetricsServiceRequest JSON payload into flat metrics."""
        metrics_out = []
        resource_metrics = payload.get("resourceMetrics", [])
        for rm in resource_metrics:
            resource = rm.get("resource", {})
            resource_attrs = cls._extract_attributes(resource.get("attributes", []))
            
            scope_metrics = rm.get("scopeMetrics", [])
            for sm in scope_metrics:
                metrics = sm.get("metrics", [])
                for metric in metrics:
                    metric_name = metric.get("name")
                    
                    # Handle Gauge, Sum, Histogram, etc. 
                    # Assuming basic Gauge/Sum for simplicity in this implementation
                    data_points = []
                    if "gauge" in metric:
                        data_points = metric["gauge"].get("dataPoints", [])
                    elif "sum" in metric:
                        data_points = metric["sum"].get("dataPoints", [])
                    
                    for dp in data_points:
                        val = dp.get("asDouble", dp.get("asInt", 0.0))
                        ts = cls._parse_time_unix_nano(dp.get("timeUnixNano", 0)).isoformat()
                        attrs = cls._extract_attributes(dp.get("attributes", []))
                        
                        metrics_out.append({
                            "name": metric_name,
                            "value": val,
                            "timestamp": ts,
                            "tags": attrs,
                            "resource_attributes": resource_attrs
                        })
        return metrics_out

    @classmethod
    def parse_logs(cls, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parses OTLP ExportLogsServiceRequest JSON payload into flat logs."""
        logs_out = []
        resource_logs = payload.get("resourceLogs", [])
        for rl in resource_logs:
            resource = rl.get("resource", {})
            resource_attrs = cls._extract_attributes(resource.get("attributes", []))
            
            scope_logs = rl.get("scopeLogs", [])
            for sl in scope_logs:
                log_records = sl.get("logRecords", [])
                for log in log_records:
                    ts = cls._parse_time_unix_nano(log.get("timeUnixNano", 0)).isoformat()
                    
                    body = log.get("body", {})
                    message = body.get("stringValue", str(body))
                    
                    level = log.get("severityText", "INFO")
                    attrs = cls._extract_attributes(log.get("attributes", []))
                    
                    logs_out.append({
                        "level": level,
                        "message": message,
                        "timestamp": ts,
                        "metadata": {**attrs, **resource_attrs}
                    })
        return logs_out
