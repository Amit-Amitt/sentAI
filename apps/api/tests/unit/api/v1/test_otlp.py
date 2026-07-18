import pytest
from sentinel_api.services.otlp_parser import OTLPParser

def test_parse_traces_basic():
    # Example raw OTLP ExportTraceServiceRequest JSON
    raw_payload = {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "payment-service"}},
                        {"key": "k8s.namespace", "value": {"stringValue": "prod"}}
                    ]
                },
                "scopeSpans": [
                    {
                        "spans": [
                            {
                                "traceId": "5b8aa5a2d2c872e8321cf37308d69df2",
                                "spanId": "051581bf3cb55c13",
                                "name": "POST /charge",
                                "kind": "SERVER",
                                "startTimeUnixNano": "1672531200000000000", # 2023-01-01 00:00:00 UTC
                                "endTimeUnixNano": "1672531200050000000",   # +50ms
                                "status": {"code": "ERROR", "message": "Payment declined"},
                                "attributes": [
                                    {"key": "http.method", "value": {"stringValue": "POST"}},
                                    {"key": "http.status_code", "value": {"intValue": 500}}
                                ],
                                "events": [
                                    {
                                        "name": "exception",
                                        "timeUnixNano": "1672531200025000000",
                                        "attributes": [
                                            {"key": "exception.type", "value": {"stringValue": "GatewayTimeout"}}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    spans = OTLPParser.parse_traces(raw_payload)
    
    assert len(spans) == 1
    span = spans[0]
    
    assert span["trace_id"] == "5b8aa5a2d2c872e8321cf37308d69df2"
    assert span["span_id"] == "051581bf3cb55c13"
    assert span["name"] == "POST /charge"
    assert span["kind"] == "SERVER"
    assert span["duration_ms"] == 50.0
    assert span["status_code"] == "ERROR"
    assert span["status_message"] == "Payment declined"
    
    # Check attributes mapping
    assert span["resource_attributes"]["service.name"] == "payment-service"
    assert span["resource_attributes"]["k8s.namespace"] == "prod"
    assert span["span_attributes"]["http.method"] == "POST"
    assert span["span_attributes"]["http.status_code"] == 500
    
    # Check events
    assert len(span["events"]) == 1
    assert span["events"][0]["name"] == "exception"
    assert span["events"][0]["attributes"]["exception.type"] == "GatewayTimeout"

def test_parse_logs_basic():
    raw_payload = {
        "resourceLogs": [
            {
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "auth-service"}}
                    ]
                },
                "scopeLogs": [
                    {
                        "logRecords": [
                            {
                                "timeUnixNano": "1672531200000000000",
                                "severityText": "WARN",
                                "body": {"stringValue": "Invalid credentials provided"},
                                "attributes": [
                                    {"key": "user_id", "value": {"stringValue": "usr_123"}}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    logs = OTLPParser.parse_logs(raw_payload)
    assert len(logs) == 1
    log = logs[0]
    
    assert log["level"] == "WARN"
    assert log["message"] == "Invalid credentials provided"
    assert log["metadata"]["service.name"] == "auth-service"
    assert log["metadata"]["user_id"] == "usr_123"

def test_parse_metrics_basic():
    raw_payload = {
        "resourceMetrics": [
            {
                "resource": {
                    "attributes": [
                        {"key": "host.name", "value": {"stringValue": "web-01"}}
                    ]
                },
                "scopeMetrics": [
                    {
                        "metrics": [
                            {
                                "name": "system.cpu.utilization",
                                "gauge": {
                                    "dataPoints": [
                                        {
                                            "timeUnixNano": "1672531200000000000",
                                            "asDouble": 85.5,
                                            "attributes": [
                                                {"key": "cpu", "value": {"stringValue": "0"}}
                                            ]
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    metrics = OTLPParser.parse_metrics(raw_payload)
    assert len(metrics) == 1
    metric = metrics[0]
    
    assert metric["name"] == "system.cpu.utilization"
    assert metric["value"] == 85.5
    assert metric["tags"]["cpu"] == "0"
    assert metric["resource_attributes"]["host.name"] == "web-01"
