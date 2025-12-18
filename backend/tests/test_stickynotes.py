# ============================================
# tests/test_stickynotes.py
# ============================================
"""
Tests for sticky note management endpoints
Tests: Create, view, update, delete sticky notes on papers
"""
import pytest

# ============= CREATE STICKY NOTE TESTS =============

def test_create_sticky_note_success(client, auth_headers, test_paper, sample_sticky_note_data):
    """Test successfully creating a sticky note"""
    response = client.post(
        f'/api/papers/{test_paper["id"]}/sticky-notes',
        headers=auth_headers,
        json=sample_sticky_note_data
    )
    
    assert response.status_code == 201
    assert 'note' in response.json
    assert response.json['note']['position_x'] == sample_sticky_note_data['position_x']
    assert response.json['note']['content'] == sample_sticky_note_data['content']


def test_create_sticky_note_missing_fields(client, auth_headers, test_paper):
    """Test creating sticky note fails with missing required fields"""
    incomplete_data = {
        'position_x': 100,
        'content': 'Test'
        # Missing position_y, width, height
    }
    
    response = client.post(
        f'/api/papers/{test_paper["id"]}/sticky-notes',
        headers=auth_headers,
        json=incomplete_data
    )
    
    assert response.status_code == 400


def test_create_sticky_note_nonexistent_paper(client, auth_headers, sample_sticky_note_data):
    """Test creating sticky note for nonexistent paper"""
    response = client.post(
        '/api/papers/99999/sticky-notes',
        headers=auth_headers,
        json=sample_sticky_note_data
    )
    
    assert response.status_code == 404


def test_create_sticky_note_other_user_paper(client, second_auth_token, test_paper, sample_sticky_note_data):
    """Test user cannot create sticky note on another user's paper"""
    response = client.post(
        f'/api/papers/{test_paper["id"]}/sticky-notes',
        headers={'Authorization': f'Bearer {second_auth_token}'},
        json=sample_sticky_note_data
    )
    
    assert response.status_code == 404


# ============= GET STICKY NOTES TESTS =============

def test_get_sticky_notes_success(client, auth_headers, test_paper, test_sticky_note):
    """Test getting all sticky notes for a paper"""
    response = client.get(
        f'/api/papers/{test_paper["id"]}/sticky-notes',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'notes' in response.json
    assert len(response.json['notes']) >= 1


def test_get_sticky_notes_empty(client, auth_headers, test_paper):
    """Test getting sticky notes when paper has none"""
    response = client.get(
        f'/api/papers/{test_paper["id"]}/sticky-notes',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['notes'] == []


def test_get_sticky_notes_other_user_paper(client, second_auth_token, test_paper):
    """Test user cannot get sticky notes from another user's paper"""
    response = client.get(
        f'/api/papers/{test_paper["id"]}/sticky-notes',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404


# ============= UPDATE STICKY NOTE TESTS =============

def test_update_sticky_note_position(client, auth_headers, test_sticky_note):
    """Test updating sticky note position"""
    response = client.put(
        f'/api/papers/sticky-notes/{test_sticky_note["id"]}',
        headers=auth_headers,
        json={
            'position_x': 500,
            'position_y': 600
        }
    )
    
    assert response.status_code == 200
    assert response.json['note']['position_x'] == 500
    assert response.json['note']['position_y'] == 600


def test_update_sticky_note_size(client, auth_headers, test_sticky_note):
    """Test updating sticky note size"""
    response = client.put(
        f'/api/papers/sticky-notes/{test_sticky_note["id"]}',
        headers=auth_headers,
        json={
            'width': 300,
            'height': 250
        }
    )
    
    assert response.status_code == 200
    assert response.json['note']['width'] == 300
    assert response.json['note']['height'] == 250


def test_update_sticky_note_content(client, auth_headers, test_sticky_note):
    """Test updating sticky note content"""
    response = client.put(
        f'/api/papers/sticky-notes/{test_sticky_note["id"]}',
        headers=auth_headers,
        json={'content': 'Updated content'}
    )
    
    assert response.status_code == 200
    assert response.json['note']['content'] == 'Updated content'


def test_update_sticky_note_all_fields(client, auth_headers, test_sticky_note):
    """Test updating all sticky note fields at once"""
    response = client.put(
        f'/api/papers/sticky-notes/{test_sticky_note["id"]}',
        headers=auth_headers,
        json={
            'position_x': 700,
            'position_y': 800,
            'width': 400,
            'height': 300,
            'content': 'Completely updated'
        }
    )
    
    assert response.status_code == 200
    note = response.json['note']
    assert note['position_x'] == 700
    assert note['content'] == 'Completely updated'


def test_update_sticky_note_nonexistent(client, auth_headers):
    """Test updating sticky note that doesn't exist"""
    response = client.put(
        '/api/papers/sticky-notes/99999',
        headers=auth_headers,
        json={'content': 'Test'}
    )
    
    assert response.status_code == 404


def test_update_sticky_note_other_user(client, second_auth_token, test_sticky_note):
    """Test user cannot update another user's sticky note"""
    response = client.put(
        f'/api/papers/sticky-notes/{test_sticky_note["id"]}',
        headers={'Authorization': f'Bearer {second_auth_token}'},
        json={'content': 'Test'}
    )
    
    assert response.status_code == 404


# ============= DELETE STICKY NOTE TESTS =============

def test_delete_sticky_note_success(client, auth_headers, test_sticky_note):
    """Test successfully deleting a sticky note"""
    response = client.delete(
        f'/api/papers/sticky-notes/{test_sticky_note["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'message' in response.json


def test_delete_sticky_note_nonexistent(client, auth_headers):
    """Test deleting sticky note that doesn't exist"""
    response = client.delete(
        '/api/papers/sticky-notes/99999',
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_delete_sticky_note_other_user(client, second_auth_token, test_sticky_note):
    """Test user cannot delete another user's sticky note"""
    response = client.delete(
        f'/api/papers/sticky-notes/{test_sticky_note["id"]}',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404


def test_delete_all_sticky_notes(client, auth_headers, test_paper, sample_sticky_note_data):
    """Test deleting all sticky notes for a paper"""
    # Create multiple sticky notes
    for i in range(3):
        data = sample_sticky_note_data.copy()
        data['position_x'] = 100 * (i + 1)
        client.post(
            f'/api/papers/{test_paper["id"]}/sticky-notes',
            headers=auth_headers,
            json=data
        )
    
    # Delete all
    response = client.delete(
        f'/api/papers/{test_paper["id"]}/sticky-notes/all',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['deleted_count'] == 3


def test_delete_all_sticky_notes_empty(client, auth_headers, test_paper):
    """Test deleting all sticky notes when paper has none"""
    response = client.delete(
        f'/api/papers/{test_paper["id"]}/sticky-notes/all',
        headers=auth_headers
    )
    
    assert response.status_code == 404


# ============= EDGE CASES =============

@pytest.mark.parametrize('position_x,position_y', [
    (0, 0),
    (1000, 1000),
    (50, 100),
])
def test_sticky_note_various_positions(client, auth_headers, test_paper, position_x, position_y):
    """Test creating sticky notes at different positions"""
    response = client.post(
        f'/api/papers/{test_paper["id"]}/sticky-notes',
        headers=auth_headers,
        json={
            'position_x': position_x,
            'position_y': position_y,
            'width': 200,
            'height': 150,
            'content': 'Test'
        }
    )
    
    assert response.status_code == 201
    assert response.json['note']['position_x'] == position_x
    assert response.json['note']['position_y'] == position_y

