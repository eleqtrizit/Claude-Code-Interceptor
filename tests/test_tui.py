"""Tests for the TUI module."""

import unittest
from unittest.mock import patch

from cci.tui import ConfigTUI


class TestConfigTUI(unittest.TestCase):
    """Test cases for the ConfigTUI class."""

    def setUp(self):
        """Set up test fixtures."""
        with patch('cci.tui.ConfigManager'):
            self.tui = ConfigTUI()

    @patch('cci.tui.Prompt')
    def test_show_main_menu(self, mock_prompt):
        """Test the main menu can be displayed and exits properly."""
        # Mock the prompt to return 'q' to exit immediately
        mock_prompt.ask.return_value = 'q'

        # Call the run method which will show the menu
        with self.assertRaises(SystemExit):
            self.tui.run()


if __name__ == '__main__':
    unittest.main()
