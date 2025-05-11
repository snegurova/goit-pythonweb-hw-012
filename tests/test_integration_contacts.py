import pytest
import uuid

def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": f"john-{uuid.uuid4()}@example.com",
            "phone_number": "+1234567890",
            "birthday": "1990-01-01"
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == "John"
    assert "id" in data

def test_get_contact(client, get_token):
    # Create a contact first
    create_response = client.post(
        "/api/contacts",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": f"john-{uuid.uuid4()}@example.com",
            "phone_number": "+1234567890",
            "birthday": "1990-01-01"
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert create_response.status_code == 201, create_response.text
    created_data = create_response.json()
    contact_id = created_data["id"]

    # Now fetch the created contact
    response = client.get(f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "John"
    assert "id" in data

def test_get_contact_not_found(client, get_token):
    response = client.get("/api/contacts/999", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact is not found"

def test_get_contacts(client, get_token):
    response = client.get("/api/contacts", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["first_name"] == "John"
    assert "id" in data[0]

def test_update_contact(client, get_token):
    create_response = client.post(
        "/api/contacts",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": f"john-{uuid.uuid4()}@example.com",
            "phone_number": "+1234567890",
            "birthday": "1990-01-01"
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert create_response.status_code == 201, create_response.text
    created_data = create_response.json()
    contact_id = created_data["id"]

    response = client.put(
        f"/api/contacts/{contact_id}",
        json={"first_name": "Johnny"},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Johnny"
    assert "id" in data

def test_update_contact_not_found(client, get_token):
    response = client.put(
        "/api/contacts/999",
        json={"first_name": "Ghost"},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact is not found"

def test_delete_contact(client, get_token):
    update_response = client.put(
        "/api/contacts/1",
        json={"first_name": "Johnny"},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert update_response.status_code == 200, update_response.text
    response = client.delete("/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Johnny"
    assert "id" in data

def test_repeat_delete_contact(client, get_token):
    response = client.delete("/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact is not found"


def test_get_upcoming_birthdays(client, get_token):
    response = client.get("/api/contacts/upcoming-birthdays", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
