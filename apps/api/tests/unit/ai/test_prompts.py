import pytest

from sentinel_api.ai.exceptions import PromptException
from sentinel_api.ai.prompts import PromptManager


def test_prompt_manager_rendering():
    pm = PromptManager()

    template_v1 = "Alert: Incident {{ id }} reported severity {{ severity }}."
    pm.register_template("incident_alert", "v1", template_v1)

    # Test standard hydration
    output = pm.render("incident_alert", "v1", id="INC-99", severity="CRITICAL")
    assert output == "Alert: Incident INC-99 reported severity CRITICAL."

    # Test version routing
    template_v2 = "[{{ severity }}] Incident ID: {{ id }}"
    pm.register_template("incident_alert", "v2", template_v2)

    output_v2 = pm.render("incident_alert", "v2", id="INC-100", severity="WARNING")
    assert output_v2 == "[WARNING] Incident ID: INC-100"

    # Assert unregistered key lookup error
    with pytest.raises(PromptException):
        pm.render("missing_key", "v1", id="INC-0")

    # Assert unregistered version lookup error
    with pytest.raises(PromptException):
        pm.render("incident_alert", "v32", id="INC-0")

    # Assert missing variables error
    with pytest.raises(PromptException):
        pm.render("incident_alert", "v1", id="INC-99")
