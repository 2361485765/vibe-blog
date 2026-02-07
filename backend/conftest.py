"""
Shared pytest fixtures for VibeBlog backend tests.
"""
import os
import sys
import pytest
from unittest.mock import Mock, MagicMock
from typing import Generator

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)


# ============ Flask App Fixtures ============

@pytest.fixture
def app():
    """Create Flask app for testing."""
    from app import app as flask_app
    flask_app.config.update({
        'TESTING': True,
        'DEBUG': False,
    })
    yield flask_app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create Flask CLI test runner."""
    return app.test_cli_runner()


# ============ Database Fixtures ============

@pytest.fixture
def mock_db():
    """Mock database connection."""
    db = MagicMock()
    db.cursor.return_value = MagicMock()
    return db


@pytest.fixture
def sample_blog_data():
    """Sample blog data for testing."""
    return {
        'id': 'test-blog-123',
        'title': 'Test Blog Title',
        'content': '# Test Content\n\nThis is a test blog.',
        'cover_image': 'https://example.com/cover.jpg',
        'cover_video': 'https://example.com/cover.mp4',
        'word_count': 1500,
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z',
    }


# ============ LLM Service Fixtures ============

@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return {
        'content': 'This is a generated blog post about AI.',
        'usage': {
            'prompt_tokens': 100,
            'completion_tokens': 200,
            'total_tokens': 300,
        },
    }


@pytest.fixture
def mock_llm_service(mock_llm_response):
    """Mock LLM service."""
    service = MagicMock()
    service.generate.return_value = mock_llm_response['content']
    service.generate_async.return_value = mock_llm_response['content']
    return service


# ============ Image/Video Service Fixtures ============

@pytest.fixture
def mock_image_service():
    """Mock image generation service."""
    service = MagicMock()
    service.generate_image.return_value = 'https://example.com/generated-image.jpg'
    service.generate_images.return_value = [
        'https://example.com/image1.jpg',
        'https://example.com/image2.jpg',
    ]
    return service


@pytest.fixture
def mock_video_service():
    """Mock video generation service."""
    service = MagicMock()
    service.generate_video.return_value = 'https://example.com/generated-video.mp4'
    return service


# ============ OSS Service Fixtures ============

@pytest.fixture
def mock_oss_service():
    """Mock OSS upload service."""
    service = MagicMock()
    service.upload_file.return_value = 'https://oss.example.com/uploaded-file.jpg'
    service.upload_bytes.return_value = 'https://oss.example.com/uploaded-bytes.jpg'
    return service


# ============ Blog Generator Fixtures ============

@pytest.fixture
def mock_blog_generator(mock_llm_service, mock_image_service, mock_video_service):
    """Mock blog generator."""
    generator = MagicMock()
    generator.generate.return_value = {
        'title': 'Generated Blog Title',
        'content': '# Generated Content\n\nThis is generated.',
        'cover_image': 'https://example.com/cover.jpg',
        'cover_video': 'https://example.com/cover.mp4',
    }
    return generator


# ============ Environment Fixtures ============

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables."""
    env_vars = {
        'OPENAI_API_KEY': 'test-openai-key',
        'GOOGLE_API_KEY': 'test-google-key',
        'OSS_ACCESS_KEY_ID': 'test-oss-key',
        'OSS_ACCESS_KEY_SECRET': 'test-oss-secret',
        'OSS_BUCKET_NAME': 'test-bucket',
        'OSS_ENDPOINT': 'https://oss.example.com',
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


# ============ Cleanup Fixtures ============

@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks after each test."""
    yield
    # Cleanup happens automatically with pytest-mock
