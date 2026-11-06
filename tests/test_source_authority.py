from app.verify import classify_source_authority


def test_known_primary_source_domain_and_subdomain():
    assert classify_source_authority("https://nodejs.org/en/about/eol") == "known_primary_source"
    assert classify_source_authority("https://blog.nodejs.org/en/announcements") == "known_primary_source"


def test_lookalike_domain_is_not_marked_primary():
    assert classify_source_authority("https://nodejs.org.evil.example/article") == "unclassified"


def test_government_and_academic_suffixes():
    assert classify_source_authority("https://www.example.gov.in/policy") == "government"
    assert classify_source_authority("https://dept.example.ac.in/paper") == "academic"


def test_missing_or_invalid_url_is_unclassified():
    assert classify_source_authority(None) == "unclassified"
    assert classify_source_authority("not a url") == "unclassified"
