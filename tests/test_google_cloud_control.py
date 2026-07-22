import subprocess

from scripts import google_cloud_control
from scripts.google_cloud_control import auth_status, load_profile


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


def test_google_cloud_auth_status_reports_adc_without_printing_token(
    monkeypatch,
) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_result(*args: str):
        calls.append(args)
        if args == ("--version",):
            return subprocess.CompletedProcess(
                ["gcloud", *args], 0, stdout="Google Cloud SDK 999\n", stderr=""
            )
        if args[:2] == ("auth", "list"):
            return subprocess.CompletedProcess(
                ["gcloud", *args], 0, stdout="user@example.test\n", stderr=""
            )
        if args == ("auth", "application-default", "print-access-token"):
            return subprocess.CompletedProcess(
                ["gcloud", *args], 0, stdout="secret-token\n", stderr=""
            )
        raise AssertionError(args)

    monkeypatch.setattr(google_cloud_control, "find_gcloud", lambda: "/usr/bin/gcloud")
    monkeypatch.setattr(google_cloud_control, "run_gcloud_result", fake_result)

    status = auth_status("all-in-one-498012")

    assert status["data_agent_ready"] is True
    assert status["active_account"] == "user@example.test"
    assert status["application_default_credentials"] == "ok"
    assert "secret-token" not in str(status)
    assert ("auth", "application-default", "print-access-token") in calls


def test_google_cloud_auth_status_warns_about_unresponsive_windows_gcloud(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        google_cloud_control,
        "find_gcloud",
        lambda: (
            "/mnt/c/Program Files (x86)/Google/Cloud SDK/google-cloud-sdk/bin/gcloud"
        ),
    )
    monkeypatch.setattr(google_cloud_control, "run_gcloud_result", lambda *args: None)
    monkeypatch.setattr(google_cloud_control, "gcloud_timeout_seconds", lambda: 8)

    status = auth_status("all-in-one-498012")

    assert status["data_agent_ready"] is False
    assert status["cli_responsive"] is False
    assert status["application_default_credentials"] == "missing_or_unresponsive"
    assert any("/mnt/c" in warning for warning in status["warnings"])
    assert any("8s" in warning for warning in status["warnings"])
    assert "gcloud auth application-default login" in status["required_commands"]
