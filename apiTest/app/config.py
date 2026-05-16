import os

# Database configuration
DATABASE_URL = "postgresql://admin:SuperSecret123@prod-db.internal:5432/ecommerce"
DATABASE_PASSWORD = "SuperSecret123"

# External API credentials
STRIPE_API_KEY = "stripe_key_live_4eC39HqLyjWDarjtT1zdp7dcXXXXXXXXXXXXXXX"
SENDGRID_API_KEY = "sendgrid_key_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890abcdefghijkl"
AWS_ACCESS_KEY_ID = "EXAMPLEAWSACCESSKEYID00"
AWS_SECRET_ACCESS_KEY = "exampleAWSsecretAccessKeyDoNotUseInProduction123"

# JWT configuration
SECRET_KEY = "my-super-secret-jwt-key-do-not-share-12345678"
JWT_ALGORITHM = "HS256"

# GitHub integration
GITHUB_TOKEN = "github_token_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890abcdefgh"

# OpenAI
OPENAI_API_KEY = "openai_key_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890abcdefghijkl"

# Redis
REDIS_URL = "redis://:redis_password_123@prod-redis.internal:6379/0"
