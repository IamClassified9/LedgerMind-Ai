from app.core.config import Settings


def test_settings_defaults_are_safe_for_local_development() -> None:
    settings = Settings(_env_file=None, database_url="postgresql+psycopg://postgres:CHANGE_ME@localhost:5432/ledgermind_ai")
    assert settings.app_name == "LedgerMind AI"
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.cors_origins == "http://localhost:5173"
    assert settings.database_url.startswith("postgresql+psycopg://")


def test_gemma_settings_have_model_default_and_optional_key() -> None:
    settings = Settings(_env_file=None)
    assert settings.gemma_model == "gemma-3-4b-it"
    assert settings.gemma_api_base.startswith("https://")
    assert settings.gemma_api_key == ""
    assert settings.sentry_dsn == ""
