from fastapi.testclient import TestClient 
from lg_deploy.main import app 


def test_health_endpoint():
  client = TestClient(app=app)
  response = client.get("/health")

  assert response.status_code == 200 
  assert response.json() == {"status":"ok"}