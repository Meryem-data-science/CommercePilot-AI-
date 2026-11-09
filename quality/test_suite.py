"""Suite unittest sous garde réseau globale et avec résultat machine lisible."""
import json
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch


def main():
    suite = unittest.defaultTestLoader.discover('tests')
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('Réseau interdit pendant les tests')), \
         patch.object(socket, 'create_connection', side_effect=AssertionError('Réseau interdit pendant les tests')):
        result = unittest.TextTestRunner(verbosity=1).run(suite)
    Path('work/quality/test_results.json').write_text(json.dumps({
        'run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'skipped': len(result.skipped), 'expected_failures': len(result.expectedFailures),
        'unexpected_successes': len(result.unexpectedSuccesses),
        'successful': result.wasSuccessful()}, indent=2)+'\n')
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
