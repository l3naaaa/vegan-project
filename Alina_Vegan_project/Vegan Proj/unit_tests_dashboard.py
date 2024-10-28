import pytest
import requests

@pytest.fixture
def app_url():
    return "http://localhost:5000"  # Replace with the URL of your application

def test_access_dashboard_successfully(app_url):
    # Assuming login is required to access the dashboard
    # Fill in login form with valid credentials
    login_data = {
        'username': 'user',
        'password': '123'
    }

    # Send a POST request to the login endpoint
    login_response = requests.post(f"http://127.0.0.1:5000/", data=login_data)

    # Check if login was successful
    assert login_response.status_code == 200 
    dashboard_response = requests.get(login_response.url)

    # Check if dashboard page is accessible
    assert dashboard_response.status_code == 200  # Assuming 200 status code indicates successful page access
    assert "VEGAN FOOD" in dashboard_response.text  # Assuming "Dashboard" is present in the response body indicating successful access
