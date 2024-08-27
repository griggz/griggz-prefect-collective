import unittest

from dotenv import load_dotenv

from utils.email import send_email

# load .env file
load_dotenv()


class TestSendEmail(unittest.TestCase):
    def setUp(self):
        """Called before every test."""
        self.recipients = ["", ""]
        self.subject = "Test Email"
        self.content = "This to test the email function with Microsoft."

    def test_initialization(self):
        """Test that the FormResponse class initializes correctly."""
        success = send_email(self.recipients, self.subject, self.content)
        # Make some basic assertions
        # For example, we expect form_response to have answers from our mock_data
        # self.assertEqual(pipeline_response["success"], True)


if __name__ == "__main__":
    unittest.main()
