import os

def verify_environment_variables():
    """
    Verify that required environment variables are set.
    Raises a RuntimeError if any are missing.
    """
    required_env_vars = [
        # Django
        'SECRET_KEY',
        'DEBUG',
        
        # Database configuration
        'DB_ENGINE',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'DB_HOST',
        'DB_PORT',

        # Additional environment variables
        'ALLOWED_HOSTS',
        'CORS_ALLOW_ALL_ORIGINS',
        'CORS_ALLOW_CREDENTIALS',
    ]
    
    for env_var in required_env_vars:
        if not os.getenv(env_var):
            raise RuntimeError(f"Environment variable {env_var} is not set.")