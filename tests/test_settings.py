#!/usr/bin/env python3
"""Test the settings loading to identify the issue."""

import os
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from typing import List

# Simple test to understand the issue
class TestSettings(BaseSettings):
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        print(f"Validating CORS origins: {v} (type: {type(v)})")
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

if __name__ == "__main__":
    try:
        print("Loading settings...")
        settings = TestSettings()
        print(f"CORS Origins: {settings.cors_origins}")
        print("✅ Settings loaded successfully!")
    except Exception as e:
        print(f"❌ Settings loading failed: {e}")
        print(f"CORS_ORIGINS env var: {os.getenv('CORS_ORIGINS', 'NOT SET')}")
        
        # Try loading with dotenv
        from dotenv import load_dotenv
        load_dotenv()
        print(f"After dotenv load: {os.getenv('CORS_ORIGINS', 'NOT SET')}")
