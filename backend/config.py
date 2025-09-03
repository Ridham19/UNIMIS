import os

# Roles
ROLES = ["student", "teacher", "hod", "dean", "admin"]

# JWT secret
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")

# Token expiration (in seconds)
TOKEN_EXPIRY = 3600