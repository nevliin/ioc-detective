import unittest

from src.ioc_extraction.patterns.hash_pattern import HashPattern
from src.ioc_extraction.patterns.http_request_method_pattern import HTTPRequestMethodPattern
from src.ioc_extraction.patterns.indicator_pattern import IndicatorPattern
from src.ioc_extraction.patterns.ip_pattern import IPv4Pattern
from src.ioc_extraction.patterns.ip_range_pattern import IPv4RangePattern
from src.ioc_extraction.patterns.uri_pattern import URIPattern
from test.util import create_mock_paragraph

IOC_PATTERN_TESTS = [
    {
        "pattern": IPv4Pattern,
        "text": "255.255.1.3:5000  1.2.3.4 127.0.0.1",
        "expected": [
            "255.255.1.3:5000",
            "1.2.3.4"
        ]
    },
    {
        "pattern": IPv4RangePattern,
        "text": "193.242.106.0 - 193.242.106.255 "
                "193.242.109.0 - 193.242.109.255 "
                "193.242.145.0 - 193.242.145.255 "
                "193.242.153.0 - 193.242.153.255 "
                "193.43.79.0 - 193.43.79.255 ",
        "expected": [
            "193.242.106.0 - 193.242.106.255",
            "193.242.109.0 - 193.242.109.255",
            "193.242.145.0 - 193.242.145.255",
            "193.242.153.0 - 193.242.153.255",
            "193.43.79.0 - 193.43.79.255"
        ]
    },
    {
        "pattern": HashPattern,
        "text": "Konkret betroffen ist die SolarWinds.Orion.Core.BusinessLayer.dll Programmbibliothek (MD5-Hash: "
                "b91ce2fa41029f6955bff20079468448, signiert am 24. März 2020 mit Zertifikat-Seriennummer "
                "0f:e9:73:75:20:22:a6:06:ad:f2:a3:6e:34:5d:c0:ed) [FIE2020a], [TWI2020]."
                "So wie der Hash b91ce2fa41029f6955bff27079468448b91ce2fa41029f6955bff20079468448",
        "expected": [
            "b91ce2fa41029f6955bff20079468448",
            "b91ce2fa41029f6955bff27079468448b91ce2fa41029f6955bff20079468448"
        ]
    },
    {
        "pattern": URIPattern,
        "text": "Die Ausnutzung der o.a. Schwachstelle kann mittels Log-Einträgen nachvollzogen werden. Im Fall von "
                "Outlook on the Web/Outlook Web App (OWA) nutzen die Täter POST-Anfragen auf statische Inhalte unter dem "
                "Pfad /owa/auth/Current/themes/resources. Mit speziell präparierten SOAP-Payloads ist es den Tätern dann "
                "möglich, EMails ohne Authentifizierung zu exfiltrieren.",
        "expected": [
            "/owa/auth/Current/themes/resources"
        ]
    },
    {
        "pattern": HTTPRequestMethodPattern,
        "text": "Die Ausnutzung der o.a. Schwachstelle kann mittels Log-Einträgen nachvollzogen werden. Im Fall von "
                "Outlook on the Web/Outlook Web App (OWA) nutzen die Täter POST-Anfragen auf statische Inhalte unter dem "
                "Pfad /owa/auth/Current/themes/resources. Mit speziell präparierten SOAP-Payloads ist es den Tätern dann "
                "möglich, EMails ohne Authentifizierung zu exfiltrieren.",
        "expected": [
            "POST"
        ]
    }
]


class TestPDFParser(unittest.TestCase):

    def test_ioc_patterns(self):
        for ioc_pattern_test in IOC_PATTERN_TESTS:
            paragraph = create_mock_paragraph(ioc_pattern_test["text"])
            pattern: IndicatorPattern = ioc_pattern_test["pattern"]()
            indicators = pattern.find_in_paragraph(paragraph, [])

            for i in range(len(indicators)):
                assert indicators[i].value == ioc_pattern_test["expected"][i]
