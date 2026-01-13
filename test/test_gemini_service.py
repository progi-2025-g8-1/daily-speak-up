import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.src.services.gemini_service import GeminiService
from backend.src.models.enums import AppLang


class TestGeminiService:
    """Unit tests for GeminiService."""

    @pytest.fixture
    def gemini_service(self):
        """Create a GeminiService instance with mock credentials."""
        return GeminiService(api_key="test_api_key", model_id="test_model")

    @pytest.mark.asyncio
    async def test_generate_topic_english_success(self, gemini_service):
        """Test successful topic generation in English."""
        # Arrange
        interest = "artificial intelligence"
        expected_topic = "The Future of AI in Healthcare"
        
        # Mock the Gemini API response
        mock_response = MagicMock()
        mock_response.text = expected_topic
        
        with patch.object(
            gemini_service.client.aio.models,
            'generate_content',
            new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = mock_response
            
            # Act
            result = await gemini_service.generate_topic(interest, AppLang.EN)
            
            # Assert
            assert result == expected_topic
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args
            assert call_args.kwargs['model'] == "test_model"
            assert interest in call_args.kwargs['contents']
            assert "English" in call_args.kwargs['contents']

    @pytest.mark.asyncio
    async def test_generate_topic_croatian_success(self, gemini_service):
        """Test successful topic generation in Croatian."""
        # Arrange
        interest = "glazba"
        expected_topic = "Utjecaj klasične glazbe na moderno društvo"
        
        # Mock the Gemini API response
        mock_response = MagicMock()
        mock_response.text = expected_topic
        
        with patch.object(
            gemini_service.client.aio.models,
            'generate_content',
            new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = mock_response
            
            # Act
            result = await gemini_service.generate_topic(interest, AppLang.HR)
            
            # Assert
            assert result == expected_topic
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args
            assert call_args.kwargs['model'] == "test_model"
            assert interest in call_args.kwargs['contents']
            assert "hrvatskom" in call_args.kwargs['contents']

    @pytest.mark.asyncio
    async def test_generate_topic_default_language(self, gemini_service):
        """Test that default language is English when not specified."""
        # Arrange
        interest = "technology"
        expected_topic = "The Impact of 5G on IoT Devices"
        
        mock_response = MagicMock()
        mock_response.text = expected_topic
        
        with patch.object(
            gemini_service.client.aio.models,
            'generate_content',
            new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = mock_response
            
            # Act - not passing lang parameter
            result = await gemini_service.generate_topic(interest)
            
            # Assert
            assert result == expected_topic
            call_args = mock_generate.call_args
            assert "English" in call_args.kwargs['contents']

    @pytest.mark.asyncio
    async def test_generate_topic_empty_response_text(self, gemini_service):
        """Test error handling when API returns None text."""
        # Arrange
        interest = "science"
        
        mock_response = MagicMock()
        mock_response.text = None
        
        with patch.object(
            gemini_service.client.aio.models,
            'generate_content',
            new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = mock_response
            
            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await gemini_service.generate_topic(interest)
            
            assert "No text in response from Gemini API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_topic_api_raises_exception(self, gemini_service):
        """Test error handling when API call fails."""
        # Arrange
        interest = "history"
        api_error_message = "API rate limit exceeded"
        
        with patch.object(
            gemini_service.client.aio.models,
            'generate_content',
            new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.side_effect = Exception(api_error_message)
            
            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await gemini_service.generate_topic(interest)
            
            assert "Error generating topic" in str(exc_info.value)
            assert api_error_message in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_topic_network_timeout(self, gemini_service):
        """Test error handling for network timeout."""
        # Arrange
        interest = "literature"
        
        with patch.object(
            gemini_service.client.aio.models,
            'generate_content',
            new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.side_effect = TimeoutError("Request timed out")
            
            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await gemini_service.generate_topic(interest)
            
            assert "Error generating topic" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_topic_different_interests(self, gemini_service):
        """Test topic generation with various interest types."""
        # Test data with different interest types
        test_cases = [
            ("programming", "Building Scalable Microservices"),
            ("cooking", "The Art of French Cuisine"),
            ("travel", "Hidden Gems in Southeast Asia"),
            ("fitness", "HIIT Training for Beginners"),
        ]
        
        for interest, expected_topic in test_cases:
            mock_response = MagicMock()
            mock_response.text = expected_topic
            
            with patch.object(
                gemini_service.client.aio.models,
                'generate_content',
                new_callable=AsyncMock
            ) as mock_generate:
                mock_generate.return_value = mock_response
                
                # Act
                result = await gemini_service.generate_topic(interest, AppLang.EN)
                
                # Assert
                assert result == expected_topic
                assert mock_generate.called

    @pytest.mark.asyncio
    async def test_generate_topic_with_special_characters(self, gemini_service):
        """Test topic generation with special characters in interest."""
        # Arrange
        interest = "AI & Machine Learning"
        expected_topic = "The Future of AI & ML Integration"
        
        mock_response = MagicMock()
        mock_response.text = expected_topic
        
        with patch.object(
            gemini_service.client.aio.models,
            'generate_content',
            new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = mock_response
            
            # Act
            result = await gemini_service.generate_topic(interest)
            
            # Assert
            assert result == expected_topic
            call_args = mock_generate.call_args
            assert interest in call_args.kwargs['contents']

    def test_gemini_service_initialization(self):
        """Test GeminiService initialization with correct parameters."""
        # Arrange
        api_key = "test_key_123"
        model_id = "gemini-pro"
        
        # Act
        service = GeminiService(api_key=api_key, model_id=model_id)
        
        # Assert
        assert service.model_id == model_id
        assert service.client is not None
