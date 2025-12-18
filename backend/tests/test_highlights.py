# tests/test_highlights.py
"""
Tests for highlight operations
Tests: create, view, delete highlights on papers
"""
import pytest


# ============= CREATE HIGHLIGHT TESTS =============

def test_create_highlight_success(client, auth_headers, test_paper, sample_highlight_data):
    """
    Test successfully creating a highlight on a paper
    """
    paper_id = test_paper['id']
    
    response = client.post(
        f'/api/papers/{paper_id}/highlights',
        headers=auth_headers,
        json=sample_highlight_data
    )
    
    assert response.status_code == 201
    assert response.json['message'] == 'Highlight created successfully'
    assert 'highlight' in response.json
    
    # Check highlight data
    highlight = response.json['highlight']
    assert highlight['start_offset'] == sample_highlight_data['start_offset']
    assert highlight['end_offset'] == sample_highlight_data['end_offset']
    assert highlight['color'] == sample_highlight_data['color']
    assert highlight['text_content'] == sample_highlight_data['text_content']
    assert highlight['paper_id'] == paper_id


def test_create_highlight_missing_start_offset(client, auth_headers, test_paper):
    """
    Test creating highlight fails without start_offset
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers=auth_headers,
        json={
            'end_offset': 200,
            'color': '#FFFF00',
            'text_content': 'Test text'
        }
    )
    
    assert response.status_code == 400
    assert 'error' in response.json


def test_create_highlight_missing_end_offset(client, auth_headers, test_paper):
    """
    Test creating highlight fails without end_offset
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers=auth_headers,
        json={
            'start_offset': 100,
            'color': '#FFFF00',
            'text_content': 'Test text'
        }
    )
    
    assert response.status_code == 400


def test_create_highlight_missing_color(client, auth_headers, test_paper):
    """
    Test creating highlight fails without color
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers=auth_headers,
        json={
            'start_offset': 100,
            'end_offset': 200,
            'text_content': 'Test text'
        }
    )
    
    assert response.status_code == 400


def test_create_highlight_missing_text_content(client, auth_headers, test_paper):
    """
    Test creating highlight fails without text_content
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers=auth_headers,
        json={
            'start_offset': 100,
            'end_offset': 200,
            'color': '#FFFF00'
        }
    )
    
    assert response.status_code == 400


def test_create_highlight_on_nonexistent_paper(client, auth_headers, sample_highlight_data):
    """
    Test creating highlight fails for paper that doesn't exist
    """
    response = client.post(
        '/api/papers/99999/highlights',
        headers=auth_headers,
        json=sample_highlight_data
    )
    
    assert response.status_code == 404


def test_create_highlight_without_auth(client, test_paper, sample_highlight_data):
    """
    Test creating highlight fails without authentication
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/highlights',
        json=sample_highlight_data
    )
    
    assert response.status_code == 401


def test_create_highlight_on_other_users_paper(client, second_auth_token, test_paper, sample_highlight_data):
    """
    Test user cannot create highlight on another user's paper
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers={'Authorization': f'Bearer {second_auth_token}'},
        json=sample_highlight_data
    )
    
    assert response.status_code == 404  # Paper not found for this user


# ============= VIEW HIGHLIGHTS TESTS =============

def test_view_highlights_success(client, auth_headers, test_paper, test_highlight):
    """
    Test viewing all highlights for a paper
    """
    response = client.get(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['message'] == 'Highlights retrieved successfully'
    assert 'highlights' in response.json
    assert response.json['paper_id'] == test_paper['id']
    
    # Should have at least the test_highlight
    highlights = response.json['highlights']
    assert len(highlights) >= 1
    
    # Check first highlight matches test_highlight
    highlight = highlights[0]
    assert highlight['id'] == test_highlight['id']
    assert highlight['text_content'] == test_highlight['text_content']


def test_view_highlights_empty(client, auth_headers, test_paper):
    """
    Test viewing highlights when paper has no highlights
    """
    response = client.get(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['highlights'] == []


def test_view_highlights_multiple(client, auth_headers, test_paper, sample_highlight_data):
    """
    Test viewing multiple highlights on same paper
    """
    # Create 3 highlights
    for i in range(3):
        data = sample_highlight_data.copy()
        data['start_offset'] = 100 * (i + 1)
        data['end_offset'] = 200 * (i + 1)
        data['text_content'] = f'Highlight {i + 1}'
        
        client.post(
            f'/api/papers/{test_paper["id"]}/highlights',
            headers=auth_headers,
            json=data
        )
    
    # Get all highlights
    response = client.get(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert len(response.json['highlights']) == 3


def test_view_highlights_without_auth(client, test_paper):
    """
    Test viewing highlights fails without authentication
    """
    response = client.get(f'/api/papers/{test_paper["id"]}/highlights')
    
    assert response.status_code == 401


def test_view_highlights_other_users_paper(client, second_auth_token, test_paper):
    """
    Test user cannot view highlights on another user's paper
    """
    response = client.get(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404


def test_view_highlights_nonexistent_paper(client, auth_headers):
    """
    Test viewing highlights for paper that doesn't exist
    """
    response = client.get(
        '/api/papers/99999/highlights',
        headers=auth_headers
    )
    
    assert response.status_code == 404


# ============= DELETE HIGHLIGHT TESTS =============

def test_delete_highlight_success(client, auth_headers, test_paper, test_highlight):
    """
    Test successfully deleting a highlight
    """
    paper_id = test_paper['id']
    highlight_id = test_highlight['id']
    
    response = client.delete(
        f'/api/papers/{paper_id}/highlights/{highlight_id}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['message'] == 'Highlight deleted successfully'
    assert response.json['paper_id'] == paper_id
    assert response.json['highlight_id'] == highlight_id
    
    # Verify highlight is actually deleted
    get_response = client.get(
        f'/api/papers/{paper_id}/highlights',
        headers=auth_headers
    )
    highlights = get_response.json['highlights']
    highlight_ids = [h['id'] for h in highlights]
    assert highlight_id not in highlight_ids


def test_delete_highlight_nonexistent(client, auth_headers, test_paper):
    """
    Test deleting highlight that doesn't exist
    """
    response = client.delete(
        f'/api/papers/{test_paper["id"]}/highlights/99999',
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_delete_highlight_without_auth(client, test_paper, test_highlight):
    """
    Test deleting highlight fails without authentication
    """
    response = client.delete(
        f'/api/papers/{test_paper["id"]}/highlights/{test_highlight["id"]}'
    )
    
    assert response.status_code == 401


def test_delete_highlight_other_users(client, second_auth_token, test_paper, test_highlight):
    """
    Test user cannot delete another user's highlight
    """
    response = client.delete(
        f'/api/papers/{test_paper["id"]}/highlights/{test_highlight["id"]}',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404  # Paper not found for this user


def test_delete_highlight_wrong_paper(client, auth_headers, test_paper, test_highlight, app, test_user):
    """
    Test deleting highlight from wrong paper fails
    Create a second paper and try to delete highlight with wrong paper_id
    """
    from app.models.paper import Paper
    from app.extensions import db
    
    # Create second paper
    with app.app_context():
        paper2 = Paper(
            title='Another Paper',
            authors='Author',
            file_path='/fake/path2.pdf',
            user_id=test_user['id']
        )
        db.session.add(paper2)
        db.session.commit()
        paper2_id = paper2.id
    
    # Try to delete highlight using wrong paper_id
    response = client.delete(
        f'/api/papers/{paper2_id}/highlights/{test_highlight["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 404


# ============= EDGE CASES & VALIDATION =============

@pytest.mark.parametrize('color', [
    '#FF0000',  # Red
    '#00FF00',  # Green
    '#0000FF',  # Blue
    '#FFFF00',  # Yellow
    '#FF00FF',  # Magenta
])
def test_create_highlight_various_colors(client, auth_headers, test_paper, color):
    """
    Test creating highlights with different colors
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers=auth_headers,
        json={
            'start_offset': 100,
            'end_offset': 200,
            'color': color,
            'text_content': f'Text in {color}'
        }
    )
    
    assert response.status_code == 201
    assert response.json['highlight']['color'] == color


def test_create_highlight_overlapping_offsets(client, auth_headers, test_paper):
    """
    Test creating highlights with overlapping text ranges
    This should be allowed (multiple highlights can overlap)
    """
    # Create first highlight
    response1 = client.post(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers=auth_headers,
        json={
            'start_offset': 100,
            'end_offset': 200,
            'color': '#FFFF00',
            'text_content': 'Overlapping text'
        }
    )
    
    # Create second highlight that overlaps
    response2 = client.post(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers=auth_headers,
        json={
            'start_offset': 150,
            'end_offset': 250,
            'color': '#00FF00',
            'text_content': 'Also overlapping text'
        }
    )
    
    assert response1.status_code == 201
    assert response2.status_code == 201


def test_create_highlight_large_text(client, auth_headers, test_paper):
    """
    Test creating highlight with very long text content
    """
    long_text = 'A' * 10000  # 10,000 characters
    
    response = client.post(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers=auth_headers,
        json={
            'start_offset': 0,
            'end_offset': 10000,
            'color': '#FFFF00',
            'text_content': long_text
        }
    )
    
    assert response.status_code == 201
    assert len(response.json['highlight']['text_content']) == 10000


def test_highlight_ordering(client, auth_headers, test_paper):
    """
    Test that highlights are returned in correct order (most recent first)
    """
    import time
    
    # Create 3 highlights with small delays
    for i in range(3):
        client.post(
            f'/api/papers/{test_paper["id"]}/highlights',
            headers=auth_headers,
            json={
                'start_offset': i * 100,
                'end_offset': (i + 1) * 100,
                'color': '#FFFF00',
                'text_content': f'Highlight {i}'
            }
        )
        time.sleep(0.1)  # Small delay to ensure different timestamps
    
    # Get highlights
    response = client.get(
        f'/api/papers/{test_paper["id"]}/highlights',
        headers=auth_headers
    )
    
    highlights = response.json['highlights']
    assert len(highlights) == 3
    
    # Should be ordered by created_at descending (most recent first)
    assert highlights[0]['text_content'] == 'Highlight 2'
    assert highlights[2]['text_content'] == 'Highlight 0'