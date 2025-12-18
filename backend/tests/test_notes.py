# tests/test_notes.py
"""
Tests for note management endpoints
Tests: Create, view, delete notes on papers
"""
import pytest


# ============= CREATE NOTE TESTS =============

def test_create_note_success(client, auth_headers, test_paper):
    """Test successfully creating a note"""
    response = client.post(
        f'/api/papers/{test_paper["id"]}/notes',
        headers=auth_headers,
        json={'content': 'This is a test note about the paper.'}
    )
    
    assert response.status_code == 201
    assert 'note' in response.json
    assert response.json['note']['content'] == 'This is a test note about the paper.'


def test_create_note_missing_content(client, auth_headers, test_paper):
    """Test creating note fails without content"""
    response = client.post(
        f'/api/papers/{test_paper["id"]}/notes',
        headers=auth_headers,
        json={}
    )
    
    assert response.status_code == 400
    assert 'error' in response.json


def test_create_note_empty_content(client, auth_headers, test_paper):
    """Test creating note with empty content fails"""
    response = client.post(
        f'/api/papers/{test_paper["id"]}/notes',
        headers=auth_headers,
        json={'content': '   '}
    )
    
    assert response.status_code == 400


def test_create_note_nonexistent_paper(client, auth_headers):
    """Test creating note for nonexistent paper"""
    response = client.post(
        '/api/papers/99999/notes',
        headers=auth_headers,
        json={'content': 'Test note'}
    )
    
    assert response.status_code == 404


def test_create_note_other_user_paper(client, second_auth_token, test_paper):
    """Test user cannot create note on another user's paper"""
    response = client.post(
        f'/api/papers/{test_paper["id"]}/notes',
        headers={'Authorization': f'Bearer {second_auth_token}'},
        json={'content': 'Test note'}
    )
    
    assert response.status_code == 404


def test_create_note_long_content(client, auth_headers, test_paper):
    """Test creating note with long content"""
    long_content = 'A' * 5000
    response = client.post(
        f'/api/papers/{test_paper["id"]}/notes',
        headers=auth_headers,
        json={'content': long_content}
    )
    
    assert response.status_code == 201
    assert len(response.json['note']['content']) == 5000


def test_create_multiple_notes(client, auth_headers, test_paper):
    """Test creating multiple notes on same paper"""
    for i in range(3):
        response = client.post(
            f'/api/papers/{test_paper["id"]}/notes',
            headers=auth_headers,
            json={'content': f'Note {i}'}
        )
        assert response.status_code == 201


# ============= GET NOTES TESTS =============

def test_get_notes_success(client, auth_headers, test_paper, test_note):
    """Test getting all notes for a paper"""
    response = client.get(
        f'/api/papers/{test_paper["id"]}/notes',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'notes' in response.json
    assert len(response.json['notes']) >= 1


def test_get_notes_empty(client, auth_headers, test_paper):
    """Test getting notes when paper has none"""
    response = client.get(
        f'/api/papers/{test_paper["id"]}/notes',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['notes'] == []


def test_get_notes_ordering(client, auth_headers, test_paper):
    """Test notes are returned in reverse chronological order"""
    import time
    
    # Create notes
    client.post(
        f'/api/papers/{test_paper["id"]}/notes',
        headers=auth_headers,
        json={'content': 'First note'}
    )
    
    time.sleep(0.1)
    
    client.post(
        f'/api/papers/{test_paper["id"]}/notes',
        headers=auth_headers,
        json={'content': 'Second note'}
    )
    
    response = client.get(
        f'/api/papers/{test_paper["id"]}/notes',
        headers=auth_headers
    )
    
    notes = response.json['notes']
    assert notes[0]['content'] == 'Second note'  # Most recent first
    assert notes[1]['content'] == 'First note'


def test_get_notes_other_user_paper(client, second_auth_token, test_paper):
    """Test user cannot get notes from another user's paper"""
    response = client.get(
        f'/api/papers/{test_paper["id"]}/notes',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404


# ============= DELETE NOTE TESTS =============

def test_delete_note_success(client, auth_headers, test_note):
    """Test successfully deleting a note"""
    response = client.delete(
        f'/api/papers/notes/{test_note["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'message' in response.json


def test_delete_note_nonexistent(client, auth_headers):
    """Test deleting note that doesn't exist"""
    response = client.delete(
        '/api/papers/notes/99999',
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_delete_note_other_user(client, second_auth_token, test_note):
    """Test user cannot delete another user's note"""
    response = client.delete(
        f'/api/papers/notes/{test_note["id"]}',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404


# ============= EDGE CASES =============

@pytest.mark.parametrize('content', [
    'Short note',
    'Note with special chars: @#$%^&*()',
    'Note with\nmultiple\nlines',
    'Note with émojis 📝✍️📚',
])
def test_create_note_various_content(client, auth_headers, test_paper, content):
    """Test creating notes with different content formats"""
    response = client.post(
        f'/api/papers/{test_paper["id"]}/notes',
        headers=auth_headers,
        json={'content': content}
    )
    
    assert response.status_code == 201
    assert response.json['note']['content'] == content


def test_note_with_markdown(client, auth_headers, test_paper):
    """Test creating note with markdown formatting"""
    markdown_content = """
# Header
## Subheader
- Bullet 1
- Bullet 2

**Bold text** and *italic text*
    """
    
    response = client.post(
        f'/api/papers/{test_paper["id"]}/notes',
        headers=auth_headers,
        json={'content': markdown_content}
    )
    
    assert response.status_code == 201

