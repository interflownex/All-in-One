from scripts.google_cloud_control import load_profile


def test_google_cloud_profile_is_active_and_non_destructive() -> None:
    profile = load_profile()
    assert profile["enabled"] is True
    assert "alloydb.googleapis.com" in profile["required_apis"]
    assert "aiplatform.googleapis.com" in profile["required_apis"]
    assert profile["safety"]["requires_explicit_project"] is True
    assert profile["safety"]["allow_delete"] is False
    assert profile["safety"]["allow_billing_change"] is False
    assert profile["safety"]["allow_policy_bypass"] is False
    assert profile["authoritative_project"] == "all-in-one-498012"
    assert profile["authority_mode"] == "remote_state_is_authoritative"
    assert profile["default_region"] == "southamerica-east1"
    assert profile["default_zone"] == "southamerica-east1-a"
    assert profile["safety"]["requires_import_before_change"] is True
    assert profile["safety"]["preserve_existing_remote_resources"] is True
