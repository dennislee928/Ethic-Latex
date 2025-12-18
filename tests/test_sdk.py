import pytest
from unittest.mock import MagicMock, patch
from erh.client import ERHLocalClient, ERHRemoteClient

def test_local_client_simulation():
    """Test local simulation execution."""
    client = ERHLocalClient(seed=42)
    result = client.run_simulation(num_actions=100, complexity_dist='zipf')
    
    assert result['num_actions'] == 100
    assert 'mistake_rate' in result
    assert 'analysis' in result
    assert 'raw_data' in result

@patch('requests.post')
def test_remote_client_simulation(mock_post):
    """Test remote simulation execution via API."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "mistakes": 5, 
        "primes": 10, 
        "erh_satisfied": True
    }
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    client = ERHRemoteClient(base_url="http://test-api")
    result = client.run_simulation(num_actions=100)
    
    assert result['mistakes'] == 5
    assert result['erh_satisfied'] is True
    mock_post.assert_called_once()
