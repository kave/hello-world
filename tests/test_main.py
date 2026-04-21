import os
import importlib
import pytest
from unittest.mock import patch

from main import app, strtobool


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# strtobool — one parametrized case per value so failures name the bad input
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", ["y", "yes", "on", "1", "true", "t", "YES", "True", "ON"])
def test_strtobool_returns_true_for(value):
    assert strtobool(value) is True


@pytest.mark.parametrize("value", ["n", "no", "off", "0", "false", "f", "NO", "False", ""])
def test_strtobool_returns_false_for(value):
    assert strtobool(value) is False


# ---------------------------------------------------------------------------
# GET /favicon.ico
# ---------------------------------------------------------------------------

def test_favicon_returns_200(client):
    assert client.get("/favicon.ico").status_code == 200


def test_favicon_returns_empty_json_object(client):
    assert client.get("/favicon.ico").get_json() == {}


# ---------------------------------------------------------------------------
# GET /healthz
# ---------------------------------------------------------------------------

def test_healthz_returns_200(client):
    assert client.get("/healthz").status_code == 200


def test_healthz_body_reports_healthy_status(client):
    assert client.get("/healthz").get_json() == {"status": "healthy"}


def test_healthz_prints_healthy_to_stdout(client, capsys):
    client.get("/healthz")
    assert "Healthy!" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# GET /  — clean mode (USE_CLEAN=true, the default)
# ---------------------------------------------------------------------------


def test_root_clean_mode_returns_200(client):
    with patch.dict("os.environ", {"USE_CLEAN": "true"}):
        assert client.get("/").status_code == 200


def test_root_clean_mode_renders_logo_path(client):
    with patch.dict("os.environ", {"USE_CLEAN": "true", "LOGO_PATH": "/img/custom.png"}):
        assert b"/img/custom.png" in client.get("/").data


def test_root_clean_mode_uses_default_logo_path_when_env_not_set(client):
    env = {k: v for k, v in os.environ.items() if k != "LOGO_PATH"}
    with patch.dict("os.environ", {**env, "USE_CLEAN": "true"}, clear=True):
        assert b"logo.png" in client.get("/").data


def test_root_clean_mode_does_not_render_request_headers_section(client):
    with patch.dict("os.environ", {"USE_CLEAN": "true"}):
        assert b"Request info" not in client.get("/").data


def test_root_clean_mode_does_not_render_pod_url_block(client):
    with patch.dict("os.environ", {"USE_CLEAN": "true"}):
        assert b"Pod url" not in client.get("/").data


# ---------------------------------------------------------------------------
# GET /  — full mode (USE_CLEAN=false)
# ---------------------------------------------------------------------------

def test_root_full_mode_returns_200(client):
    with patch.dict("os.environ", {"USE_CLEAN": "false"}):
        assert client.get("/").status_code == 200


def test_root_full_mode_renders_hostname(client):
    with patch.dict("os.environ", {"USE_CLEAN": "false"}):
        with patch("socket.gethostname", return_value="test-pod-xyz"):
            assert b"test-pod-xyz" in client.get("/").data


def test_root_full_mode_renders_request_headers_section(client):
    with patch.dict("os.environ", {"USE_CLEAN": "false"}):
        assert b"Request info" in client.get("/").data


def test_root_full_mode_renders_logo_path(client):
    with patch.dict("os.environ", {"USE_CLEAN": "false", "LOGO_PATH": "/img/custom.svg"}):
        assert b"/img/custom.svg" in client.get("/").data


def test_root_full_mode_renders_pod_url_when_hello_world_port_is_set(client):
    with patch.dict("os.environ", {"USE_CLEAN": "false", "HELLO_WORLD_PORT": "tcp://10.0.0.1:9000"}):
        assert b"10.0.0.1" in client.get("/").data


def test_root_full_mode_renders_svc_url_when_both_port_vars_are_set(client):
    # KUBERNETES_PORT (svc_ip) only renders inside {% if app_ip %} —
    # HELLO_WORLD_PORT must also be set for the block to appear.
    env = {
        "USE_CLEAN": "false",
        "HELLO_WORLD_PORT": "tcp://10.0.0.1:9000",
        "KUBERNETES_PORT": "tcp://10.96.0.1:443",
    }
    with patch.dict("os.environ", env):
        assert b"10.96.0.1" in client.get("/").data


def test_root_full_mode_omits_pod_url_block_when_hello_world_port_not_set(client):
    env = {k: v for k, v in os.environ.items() if k not in ("HELLO_WORLD_PORT", "KUBERNETES_PORT")}
    with patch.dict("os.environ", {**env, "USE_CLEAN": "false"}, clear=True):
        assert b"Pod url" not in client.get("/").data


# ---------------------------------------------------------------------------
# GET /<path>  — catch-all for unknown routes
# ---------------------------------------------------------------------------

def test_catch_all_returns_500_for_unknown_single_segment_path(client):
    assert client.get("/nonexistent").status_code == 500


def test_catch_all_body_contains_unknown_path_message(client):
    assert client.get("/nonexistent").get_json() == {"msg": "unknown path"}


def test_catch_all_prints_healthz_hint_to_stdout(client, capsys):
    client.get("/badpath")
    assert "healthz" in capsys.readouterr().out



# ---------------------------------------------------------------------------
# config module — PORT and HOST read from environment at import time
# ---------------------------------------------------------------------------

def test_config_port_defaults_to_9000():
    env = {k: v for k, v in os.environ.items() if k != "PORT"}
    with patch.dict("os.environ", env, clear=True):
        import config
        importlib.reload(config)
        assert config.PORT == 9000


def test_config_port_reads_from_env():
    with patch.dict("os.environ", {"PORT": "8080"}):
        import config
        importlib.reload(config)
        assert config.PORT == 8080


def test_config_host_defaults_to_all_interfaces():
    env = {k: v for k, v in os.environ.items() if k != "HOST"}
    with patch.dict("os.environ", env, clear=True):
        import config
        importlib.reload(config)
        assert config.HOST == "0.0.0.0"


def test_config_host_reads_from_env():
    with patch.dict("os.environ", {"HOST": "127.0.0.1"}):
        import config
        importlib.reload(config)
        assert config.HOST == "127.0.0.1"
