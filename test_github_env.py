import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_github_env():
    """Test script to check GitHub Actions environment variables"""
    logger.info("Testing GitHub Actions environment variables")
    
    # Check if we're in GitHub Actions
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    logger.info(f"Running in GitHub Actions: {is_github_actions}")
    
    # List all environment variables that start with GITHUB_
    github_vars = {k: v for k, v in os.environ.items() if k.startswith('GITHUB_')}
    logger.info("GitHub environment variables:")
    for key, value in github_vars.items():
        # Mask sensitive values
        if 'TOKEN' in key or 'SECRET' in key:
            logger.info(f"  {key}: {'*' * len(value) if value else 'NOT SET'}")
        else:
            logger.info(f"  {key}: {value[:50]}{'...' if len(value) > 50 else ''}")
    
    # Check required secrets
    required_secrets = ['METACULUS_TOKEN']
    missing_secrets = []
    for secret in required_secrets:
        if not os.getenv(secret):
            missing_secrets.append(secret)
    
    if missing_secrets:
        logger.error(f"Missing required secrets: {missing_secrets}")
        return False
    else:
        logger.info("All required secrets are present")
        return True

if __name__ == "__main__":
    success = test_github_env()
    exit(0 if success else 1)