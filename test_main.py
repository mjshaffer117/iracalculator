import sys
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("yfinance", types.SimpleNamespace())

import main


class MainCliTests(unittest.TestCase):
    @patch("builtins.input", side_effect=["quit"])
    @patch("sys.argv", ["main.py"])
    def test_main_cli_starts_interactive_mode_without_arguments(self, _mock_input):
        with patch("main.configure_logging"), patch("main.db.init_db") as init_db:
            main.main_cli()

        init_db.assert_called_once()


if __name__ == "__main__":
    unittest.main()
