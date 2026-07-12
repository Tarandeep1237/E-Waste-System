import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app import create_app
from utils.rewards_utils import calculate_reward_points

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_calculate_reward_points():
    # Test base points calculation
    assert calculate_reward_points('Laptop') == 150
    assert calculate_reward_points('Smartphone') == 100
    assert calculate_reward_points('Cables/Wires') == 20
    assert calculate_reward_points('Unknown E-Waste') == 50

