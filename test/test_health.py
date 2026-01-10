from fastapi import status

def test_health_check(client):
    response = client.get('/api/v1/health')
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['status'] == 'ok'
    assert 'timestamp' in data
    assert 'service' in data
    assert data['service'] == 'DailySpeakUp API'

def test_root_endpoint(client):
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['message'] == 'DailySpeakAPI'
    assert data['version'] == '1.0.0'
