"""
Tests for the configuration.
"""

from fastapi_qengine.core.config import (
    CacheConfig,
    OptimizerConfig,
    ParserConfig,
    QEngineConfig,
    ValidatorConfig,
    default_config,
)
from fastapi_qengine.core.types import SecurityPolicy


def test_qengine_config_defaults():
    """Test the default values for the main QEngineConfig."""
    config = QEngineConfig()
    assert config.default_backend == "beanie"
    assert config.debug is False
    assert isinstance(config.security_policy, SecurityPolicy)
    assert isinstance(config.parser, ParserConfig)
    assert isinstance(config.validator, ValidatorConfig)
    assert isinstance(config.optimizer, OptimizerConfig)
    assert isinstance(config.cache, CacheConfig)
    assert config.backend_settings == {}


def test_parser_config_defaults():
    """Test the default values for ParserConfig."""
    config = ParserConfig()
    assert config.max_nesting_depth == 10
    assert config.strict_mode is False
    assert config.case_sensitive_operators is True
    assert config.allow_empty_conditions is False


def test_validator_config_defaults():
    """Test the default values for ValidatorConfig."""
    config = ValidatorConfig()
    assert config.validate_types is True
    assert config.validate_operators is True
    assert config.validate_field_names is True
    assert config.custom_validators == []


def test_optimizer_config_defaults():
    """Test the default values for OptimizerConfig."""
    config = OptimizerConfig()
    assert config.enabled is True
    assert config.simplify_logical_operators is True
    assert config.combine_range_conditions is True
    assert config.remove_redundant_conditions is True
    assert config.max_optimization_passes == 3


def test_cache_config_defaults():
    """Test the default values for CacheConfig."""
    config = CacheConfig()
    assert config.enabled is False
    assert config.ttl_seconds == 300
    assert config.max_size == 1000
    assert config.cache_parsed_filters is True
    assert config.cache_compiled_queries is True


def test_custom_qengine_config():
    """Test creating a QEngineConfig with custom values."""
    custom_parser = ParserConfig(max_nesting_depth=5)
    custom_optimizer = OptimizerConfig(enabled=False)
    config = QEngineConfig(
        default_backend="sqlalchemy",
        debug=True,
        parser=custom_parser,
        optimizer=custom_optimizer,
    )
    assert config.default_backend == "sqlalchemy"
    assert config.debug is True
    assert config.parser.max_nesting_depth == 5
    assert config.optimizer.enabled is False
    assert isinstance(config.validator, ValidatorConfig)  # Check it's still default


def test_backend_settings():
    """Test the backend-specific settings methods."""
    config = QEngineConfig()
    assert config.get_backend_setting("beanie", "some_key") is None
    assert config.get_backend_setting("beanie", "some_key", "default_val") == "default_val"

    config.set_backend_setting("beanie", "some_key", "some_value")
    assert config.get_backend_setting("beanie", "some_key") == "some_value"

    config.set_backend_setting("sqlalchemy", "another_key", 123)
    assert config.backend_settings == {
        "beanie": {"some_key": "some_value"},
        "sqlalchemy": {"another_key": 123},
    }
    assert config.get_backend_setting("sqlalchemy", "another_key") == 123


def test_default_config_instance():
    """Test that the global default_config instance exists and is a QEngineConfig."""
    assert isinstance(default_config, QEngineConfig)
    assert default_config.default_backend == "beanie"
