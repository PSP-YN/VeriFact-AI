from app.verify import safe_source_url


def test_safe_source_url_accepts_http_and_https():
    assert safe_source_url("https://example.com/path") == "https://example.com/path"
    assert safe_source_url("http://example.com") == "http://example.com"


def test_safe_source_url_rejects_non_web_schemes():
    assert safe_source_url("javascript:alert(1)") is None
    assert safe_source_url("file:///etc/passwd") is None
    assert safe_source_url("not-a-url") is None
    assert safe_source_url(None) is None
