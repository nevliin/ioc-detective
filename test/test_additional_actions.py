import logging
import unittest

from src.additional_actions import find_rule_links
from src.util import LogCollector, LogEntry
from test.util import create_mock_document

DOCUMENT_WITH_SIGMA_RULE = create_mock_document("""
Etiam ac lorem a eros hendrerit tempor. Nullam luctus convallis nulla, et facilisis lacus interdum id. 
Interdum et malesuada fames ac ante ipsum primis in faucibus. Quisque iaculis ultricies ante.
Sigma Rule can be found here: https://github.com/SigmaHQ/sigma/blob/master/rules/web/example_sigma_rule.yml.
Aliquam in sem non eros feugiat venenatis. Sed eget elit lorem. Phasellus in hendrerit ante. Aenean eget tincidunt dui. 
Vivamus laoreet velit tortor, eget mollis dui tristique ac. Proin malesuada egestas nulla, sit amet
""")


class TestPDFParser(unittest.TestCase):

    def test_sigma_rule_detection(self):
        log_collector = LogCollector()
        find_rule_links(log_collector, DOCUMENT_WITH_SIGMA_RULE)
        assert len(log_collector.logs) == 1
        actual = log_collector.logs[0]
        expected = LogEntry(tag='Rule Link Detection',
                            message='Link to Sigma Rule detected: https://github.com/SigmaHQ/sigma/blob/master/rules/web/example_sigma_rule.yml',
                            level=logging.INFO)
        assert actual == expected
