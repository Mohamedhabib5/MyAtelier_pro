import pytest
from unittest.mock import MagicMock
from app.db.session import get_db

@pytest.mark.guardrail
def test_get_db_rolls_back_on_exception():
    request = MagicMock()
    session_factory = MagicMock()
    db_session = MagicMock()
    
    session_factory.return_value = db_session
    request.app.state.session_factory = session_factory
    
    generator = get_db(request)
    
    # Start the generator
    db = next(generator)
    assert db is db_session
    
    # Raise an exception inside the try-except of the generator
    with pytest.raises(ValueError, match="test error"):
        generator.throw(ValueError("test error"))
        
    # Verify rollback was called and session was closed
    db_session.rollback.assert_called_once()
    db_session.close.assert_called_once()
