from app.services.country_settings import country_settings, valid_timezone

def test_country_settings_for_required_countries():
    assert country_settings("NG")["currency"] == "NGN"
    assert country_settings("NG")["timezones"] == ["Africa/Lagos"]
    assert country_settings("GB")["currency"] == "GBP"
    assert country_settings("US")["currency"] == "USD"
    assert len(country_settings("US")["timezones"]) > 1
    assert country_settings("JP")["currency"] == "JPY"
    assert country_settings("JP")["timezones"] == ["Asia/Tokyo"]

def test_invalid_timezone_falls_back_to_utc():
    assert valid_timezone("Not/A_Real_Zone") == "UTC"

def test_valid_timezone_is_preserved():
    assert valid_timezone("Asia/Tokyo") == "Asia/Tokyo"
