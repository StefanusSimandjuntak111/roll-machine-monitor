"""
Test untuk MonitoringSession.
"""
import pytest
import os
from datetime import datetime
from monitoring.session import MonitoringSession

@pytest.fixture
def session(tmp_path):
    """Fixture untuk MonitoringSession dengan temporary directory."""
    return MonitoringSession(export_dir=str(tmp_path))

def test_session_start(session):
    """Test mulai sesi baru."""
    assert session.start_time is None
    session.start()
    assert isinstance(session.start_time, datetime)
    assert len(session.data) == 0

def test_add_data_auto_start(session):
    """Test add_data otomatis memulai sesi jika belum dimulai."""
    assert session.start_time is None
    session.add_data({"test": "data"})
    assert session.start_time is not None
    assert len(session.data) == 1
    assert "timestamp" in session.data[0]
    assert session.data[0]["test"] == "data"

def test_end_session_export(session):
    """Test akhiri sesi dan ekspor data."""
    session.start()
    session.add_data({"test": "data1"})
    session.add_data({"test": "data2"})
    
    filepath = session.end()
    assert os.path.exists(filepath)
    assert filepath.endswith(".csv")
    
    # Verifikasi file CSV
    with open(filepath, "r") as f:
        content = f.read()
        assert "timestamp" in content
        assert "data1" in content
        assert "data2" in content

def test_end_without_start(session):
    """Test error saat end tanpa start."""
    with pytest.raises(ValueError):
        session.end()

def test_get_current_values_empty(session):
    """Test get_current_values saat data kosong."""
    assert session.get_current_values() == {}

def test_get_current_values(session):
    """Test get_current_values dengan data."""
    session.add_data({"test": "data1"})
    session.add_data({"test": "data2"})
    current = session.get_current_values()
    assert current["test"] == "data2" 