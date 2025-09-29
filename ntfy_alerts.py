#!/usr/bin/env python3
"""
ntfy alert system for Metaculus bot notifications.
Sends alerts when new questions drop or when bot activity occurs.
"""
import requests
import json
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class NtfyAlerts:
    """
    Simple ntfy alert system for bot notifications.
    """

    def __init__(self,
                 topic: str = None,
                 server_url: str = "https://ntfy.sh",
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        """
        Initialize ntfy alert system.

        Args:
            topic: ntfy topic name (if None, will read from NTFY_TOPIC env var)
            server_url: ntfy server URL (default: public ntfy.sh)
            username: Optional username for authentication
            password: Optional password for authentication
        """
        self.topic = topic or os.getenv('NTFY_TOPIC', 'metaculus-bot-alerts')
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password

        # Validate configuration
        if not self.topic:
            raise ValueError("ntfy topic must be specified either as parameter or NTFY_TOPIC environment variable")

    def send_alert(self,
                   message: str,
                   title: Optional[str] = None,
                   priority: int = 3,
                   tags: Optional[list] = None,
                   click_url: Optional[str] = None,
                   attach_url: Optional[str] = None) -> bool:
        """
        Send an ntfy notification.

        Args:
            message: The alert message content
            title: Optional title for the notification
            priority: Priority level (1=min, 5=max, default=3)
            tags: Optional list of tags/emojis
            click_url: Optional URL to open when notification is clicked
            attach_url: Optional URL for image/file attachment

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'X-Priority': str(priority)
            }

            # Add optional headers
            if title:
                headers['X-Title'] = title
            if tags:
                headers['X-Tags'] = ','.join(str(tag) for tag in tags)
            if click_url:
                headers['X-Click'] = click_url
            if attach_url:
                headers['X-Attach'] = attach_url

            # Add authentication if provided
            if self.username and self.password:
                import base64
                auth_string = f"{self.username}:{self.password}"
                auth_bytes = auth_string.encode('utf-8')
                auth_header = base64.b64encode(auth_bytes).decode('utf-8')
                headers['Authorization'] = f'Basic {auth_header}'

            # Send the request
            url = f"{self.server_url}/{self.topic}"
            response = requests.post(url, data=message.encode('utf-8'), headers=headers, timeout=10)

            if response.status_code == 200:
                logger.info(f"Successfully sent ntfy alert: {title or 'No title'}")
                return True
            else:
                logger.error(f"Failed to send ntfy alert: HTTP {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Exception sending ntfy alert: {e}")
            return False

    def send_new_question_alert(self,
                              question_title: str,
                              question_url: str,
                              question_type: str = "binary",
                              tournament: Optional[str] = None) -> bool:
        """
        Send alert for new Metaculus question.

        Args:
            question_title: Title of the new question
            question_url: URL to the question
            question_type: Type of question (binary, numeric, multiple_choice)
            tournament: Optional tournament name

        Returns:
            bool: True if successful, False otherwise
        """
        # Create alert message
        message = f"New {question_type} question: {question_title}"

        # Create title with tournament info if available
        if tournament:
            title = f"New {tournament} Question"
        else:
            title = "New Metaculus Question"

        # Set appropriate tags based on question type
        tags = ["new", "metaculus"]
        if question_type == "binary":
            tags.append("yes-no")
        elif question_type == "numeric":
            tags.append("number")
        elif question_type == "multiple_choice":
            tags.append("multiple")

        if tournament:
            tags.append("tournament")

        return self.send_alert(
            message=message,
            title=title,
            priority=4,  # High priority for new questions
            tags=tags,
            click_url=question_url
        )

    def send_bot_status_alert(self,
                             status: str,
                             message: str,
                             priority: int = 2) -> bool:
        """
        Send bot status alert (start, stop, error, etc.).

        Args:
            status: Status type (started, stopped, error, warning)
            message: Detailed status message
            priority: Alert priority (default 2=low)

        Returns:
            bool: True if successful, False otherwise
        """
        # Map status to appropriate text
        status_map = {
            'started': 'Bot',
            'stopped': 'Bot',
            'error': 'Bot',
            'warning': 'Bot',
            'success': 'Bot',
            'info': 'Bot'
        }

        prefix = status_map.get(status.lower(), 'Bot')
        title = f"{prefix} {status.title()}"

        return self.send_alert(
            message=message,
            title=title,
            priority=priority,
            tags=[status, "bot"]
        )

    def send_forecast_alert(self,
                           question_title: str,
                           prediction: float,
                           confidence: str,
                           question_url: str) -> bool:
        """
        Send alert when bot makes a forecast.

        Args:
            question_title: Title of the question
            prediction: The predicted probability/value
            confidence: Bot's confidence level
            question_url: URL to the question

        Returns:
            bool: True if successful, False otherwise
        """
        message = f"Forecast: {prediction} ({confidence})"
        title = "Bot Forecast Complete"

        return self.send_alert(
            message=message,
            title=title,
            priority=3,
            tags=["forecast", "bot"],
            click_url=question_url
        )

    def test_connection(self) -> bool:
        """
        Test the ntfy connection.

        Returns:
            bool: True if connection works, False otherwise
        """
        return self.send_bot_status_alert(
            status="info",
            message="Testing ntfy alert system connection",
            priority=1
        )


# Global instance for easy use
_ntfy_instance: Optional[NtfyAlerts] = None

def get_ntfy_instance() -> NtfyAlerts:
    """
    Get or create the global ntfy instance.
    """
    global _ntfy_instance
    if _ntfy_instance is None:
        _ntfy_instance = NtfyAlerts()
    return _ntfy_instance

def send_new_question_alert(question_title: str, question_url: str,
                           question_type: str = "binary",
                           tournament: Optional[str] = None) -> bool:
    """
    Convenience function to send new question alert.
    """
    return get_ntfy_instance().send_new_question_alert(
        question_title, question_url, question_type, tournament
    )

def send_bot_status_alert(status: str, message: str, priority: int = 2) -> bool:
    """
    Convenience function to send bot status alert.
    """
    return get_ntfy_instance().send_bot_status_alert(status, message, priority)

def send_forecast_alert(question_title: str, prediction: float,
                        confidence: str, question_url: str) -> bool:
    """
    Convenience function to send forecast alert.
    """
    return get_ntfy_instance().send_forecast_alert(
        question_title, prediction, confidence, question_url
    )

def test_ntfy_connection() -> bool:
    """
    Test the ntfy connection.
    """
    return get_ntfy_instance().test_connection()


if __name__ == "__main__":
    # Simple test
    print("Testing ntfy alert system...")

    # Check environment variable
    topic = os.getenv('NTFY_TOPIC')
    if not topic:
        print("Please set NTFY_TOPIC environment variable")
        print("Example: export NTFY_TOPIC='my-metaculus-bot'")
        exit(1)

    # Test connection
    ntfy = NtfyAlerts(topic=topic)

    print(f"Testing with topic: {topic}")
    print(f"Server: {ntfy.server_url}")

    if ntfy.test_connection():
        print("✅ ntfy test successful!")

        # Test different alert types
        ntfy.send_new_question_alert(
            question_title="Will AI achieve AGI by 2030?",
            question_url="https://www.metaculus.com/questions/1234",
            question_type="binary",
            tournament="AI Competition"
        )

        ntfy.send_bot_status_alert(
            status="started",
            message="Bot started processing new questions"
        )

        ntfy.send_forecast_alert(
            question_title="Will AI achieve AGI by 2030?",
            prediction=0.75,
            confidence="high",
            question_url="https://www.metaculus.com/questions/1234"
        )

        print("✅ All test alerts sent successfully!")
        print(f"📱 Check your device or visit: https://ntfy.sh/{topic}")

    else:
        print("❌ ntfy test failed!")
        exit(1)