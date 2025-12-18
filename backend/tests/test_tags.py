# tests/test_tags.py
"""
Tests for tag operations
Tests: Tag CRUD and paper-tag associations
"""
import pytest


# ============= TAG CRUD TESTS =============

def test_create_tag_success(client, auth_headers):
    """
    Test successfully creating a new tag
    """
    response = client.post(
        '/api/tags',
        headers=auth_headers,
        json={
            'name': 'Machine Learning',
            'color': '#FF5733'
        }
    )
    
    assert response.status_code == 201
    assert response.json['message'] == 'Tag created successfully'
    assert 'tag' in response.json
    assert response.json['tag']['name'] == 'Machine Learning'
    assert response.json['tag']['color'] == '#FF5733'


def test_create_tag_missing_name(client, auth_headers):
    """
    Test creating tag fails without name
    """
    response = client.post(
        '/api/tags',
        headers=auth_headers,
        json={'color': '#FF5733'}
    )
    
    assert response.status_code == 400


def test_create_tag_missing_color(client, auth_headers):
    """
    Test creating tag fails without color
    """
    response = client.post(
        '/api/tags',
        headers=auth_headers,
        json={'name': 'Test Tag'}
    )
    
    assert response.status_code == 400


def test_create_tag_duplicate_name(client, auth_headers, test_tag):
    """
    Test creating tag with duplicate name fails
    """
    response = client.post(
        '/api/tags',
        headers=auth_headers,
        json={
            'name': test_tag['name'],  # Already exists
            'color': '#00FF00'
        }
    )
    
    assert response.status_code == 400
    assert 'already exists' in response.json['error'].lower()


def test_create_tag_without_auth(client):
    """
    Test creating tag fails without authentication
    """
    response = client.post(
        '/api/tags',
        json={'name': 'Test', 'color': '#FF0000'}
    )
    
    assert response.status_code == 401


def test_get_all_tags(client, auth_headers, test_tag):
    """
    Test getting all tags
    """
    # Create additional tags
    client.post('/api/tags', headers=auth_headers, json={'name': 'Tag1', 'color': '#111111'})
    client.post('/api/tags', headers=auth_headers, json={'name': 'Tag2', 'color': '#222222'})
    
    response = client.get('/api/tags', headers=auth_headers)
    
    assert response.status_code == 200
    assert 'tags' in response.json
    assert len(response.json['tags']) >= 3  # At least test_tag + 2 new ones


def test_get_tags_empty(client, auth_headers):
    """
    Test getting tags when none exist
    """
    response = client.get('/api/tags', headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json['tags'] == []


def test_update_tag_success(client, auth_headers, test_tag):
    """
    Test successfully updating a tag
    """
    response = client.put(
        f'/api/tags/{test_tag["id"]}',
        headers=auth_headers,
        json={
            'name': 'Updated Tag Name',
            'color': '#0000FF'
        }
    )
    
    assert response.status_code == 200
    assert response.json['tag']['name'] == 'Updated Tag Name'
    assert response.json['tag']['color'] == '#0000FF'


def test_update_tag_name_only(client, auth_headers, test_tag):
    """
    Test updating only tag name
    """
    response = client.put(
        f'/api/tags/{test_tag["id"]}',
        headers=auth_headers,
        json={'name': 'New Name'}
    )
    
    assert response.status_code == 200
    assert response.json['tag']['name'] == 'New Name'


def test_update_tag_color_only(client, auth_headers, test_tag):
    """
    Test updating only tag color
    """
    response = client.put(
        f'/api/tags/{test_tag["id"]}',
        headers=auth_headers,
        json={'color': '#FF00FF'}
    )
    
    assert response.status_code == 200
    assert response.json['tag']['color'] == '#FF00FF'


def test_update_tag_nonexistent(client, auth_headers):
    """
    Test updating tag that doesn't exist
    """
    response = client.put(
        '/api/tags/99999',
        headers=auth_headers,
        json={'name': 'Test'}
    )
    
    assert response.status_code == 404


def test_update_tag_duplicate_name(client, auth_headers, app):
    """
    Test updating tag to a name that already exists
    """
    from app.models.highlights_and_tags import Tags
    from app.extensions import db
    
    # Create two tags
    with app.app_context():
        tag1 = Tags(name='Tag1', color='#111111')
        tag2 = Tags(name='Tag2', color='#222222')
        db.session.add(tag1)
        db.session.add(tag2)
        db.session.commit()
        tag1_id = tag1.id
    
    # Try to rename tag1 to tag2 (duplicate)
    response = client.put(
        f'/api/tags/{tag1_id}',
        headers=auth_headers,
        json={'name': 'Tag2'}
    )
    
    assert response.status_code == 400
    assert 'already exists' in response.json['error'].lower()


def test_delete_tag_success(client, auth_headers, test_tag):
    """
    Test successfully deleting a tag
    """
    response = client.delete(
        f'/api/tags/{test_tag["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'deleted' in response.json['message'].lower()
    
    # Verify tag is deleted
    get_response = client.get('/api/tags', headers=auth_headers)
    tag_ids = [t['id'] for t in get_response.json['tags']]
    assert test_tag['id'] not in tag_ids


def test_delete_tag_nonexistent(client, auth_headers):
    """
    Test deleting tag that doesn't exist
    """
    response = client.delete('/api/tags/99999', headers=auth_headers)
    
    assert response.status_code == 404


# ============= PAPER-TAG ASSOCIATION TESTS =============

def test_add_tag_to_paper_success(client, auth_headers, test_paper, test_tag):
    """
    Test successfully adding a tag to a paper
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/tags',
        headers=auth_headers,
        json={'tag_id': test_tag['id']}
    )
    
    assert response.status_code == 201
    assert 'added' in response.json['message'].lower()
    assert response.json['paper_id'] == test_paper['id']
    assert response.json['tag']['id'] == test_tag['id']


def test_add_tag_missing_tag_id(client, auth_headers, test_paper):
    """
    Test adding tag fails without tag_id
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/tags',
        headers=auth_headers,
        json={}
    )
    
    assert response.status_code == 400


def test_add_nonexistent_tag(client, auth_headers, test_paper):
    """
    Test adding tag that doesn't exist
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/tags',
        headers=auth_headers,
        json={'tag_id': 99999}
    )
    
    assert response.status_code == 404


def test_add_duplicate_tag(client, auth_headers, test_paper, test_tag):
    """
    Test adding same tag twice to paper fails
    """
    # Add tag first time
    client.post(
        f'/api/papers/{test_paper["id"]}/tags',
        headers=auth_headers,
        json={'tag_id': test_tag['id']}
    )
    
    # Try to add again
    response = client.post(
        f'/api/papers/{test_paper["id"]}/tags',
        headers=auth_headers,
        json={'tag_id': test_tag['id']}
    )
    
    assert response.status_code == 400
    assert 'already associated' in response.json['error'].lower()


def test_assign_multiple_tags(client, auth_headers, test_paper, app):
    """
    Test assigning multiple tags at once
    """
    from app.models.highlights_and_tags import Tags
    from app.extensions import db
    
    # Create 3 tags
    with app.app_context():
        tag1 = Tags(name='Tag1', color='#111')
        tag2 = Tags(name='Tag2', color='#222')
        tag3 = Tags(name='Tag3', color='#333')
        db.session.add_all([tag1, tag2, tag3])
        db.session.commit()
        tag_ids = [tag1.id, tag2.id, tag3.id]
    
    # Assign all tags at once
    response = client.post(
        f'/api/papers/{test_paper["id"]}/tags/assign',
        headers=auth_headers,
        json={'tag_ids': tag_ids}
    )
    
    assert response.status_code == 201
    assert len(response.json['added_tags']) == 3


def test_assign_tags_invalid_format(client, auth_headers, test_paper):
    """
    Test assigning tags with invalid format fails
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/tags/assign',
        headers=auth_headers,
        json={'tag_ids': 'not-a-list'}
    )
    
    assert response.status_code == 400


def test_assign_tags_with_nonexistent_ids(client, auth_headers, test_paper):
    """
    Test assigning tags with invalid IDs
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/tags/assign',
        headers=auth_headers,
        json={'tag_ids': [99998, 99999]}
    )
    
    assert response.status_code == 404


def test_get_paper_tags(client, auth_headers, test_paper, test_tag):
    """
    Test getting all tags for a paper
    """
    # Add tag to paper
    client.post(
        f'/api/papers/{test_paper["id"]}/tags',
        headers=auth_headers,
        json={'tag_id': test_tag['id']}
    )
    
    # Get tags
    response = client.get(
        f'/api/papers/{test_paper["id"]}/tags',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'tags' in response.json
    assert len(response.json['tags']) >= 1
    assert response.json['tags'][0]['id'] == test_tag['id']


def test_get_paper_tags_empty(client, auth_headers, test_paper):
    """
    Test getting tags when paper has no tags
    """
    response = client.get(
        f'/api/papers/{test_paper["id"]}/tags',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['tags'] == []


def test_remove_tag_from_paper_success(client, auth_headers, test_paper, test_tag):
    """
    Test successfully removing a tag from a paper
    """
    # Add tag first
    client.post(
        f'/api/papers/{test_paper["id"]}/tags',
        headers=auth_headers,
        json={'tag_id': test_tag['id']}
    )
    
    # Remove tag
    response = client.delete(
        f'/api/papers/{test_paper["id"]}/tags/{test_tag["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'removed' in response.json['message'].lower()
    
    # Verify tag is removed
    get_response = client.get(
        f'/api/papers/{test_paper["id"]}/tags',
        headers=auth_headers
    )
    tag_ids = [t['id'] for t in get_response.json['tags']]
    assert test_tag['id'] not in tag_ids


def test_remove_tag_not_associated(client, auth_headers, test_paper, test_tag):
    """
    Test removing tag that isn't associated with paper
    """
    response = client.delete(
        f'/api/papers/{test_paper["id"]}/tags/{test_tag["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert 'not associated' in response.json['error'].lower()


def test_remove_nonexistent_tag(client, auth_headers, test_paper):
    """
    Test removing tag that doesn't exist
    """
    response = client.delete(
        f'/api/papers/{test_paper["id"]}/tags/99999',
        headers=auth_headers
    )
    
    assert response.status_code == 404


# ============= AUTHORIZATION TESTS =============

def test_add_tag_to_other_users_paper(client, second_auth_token, test_paper, test_tag):
    """
    Test user cannot add tag to another user's paper
    """
    response = client.post(
        f'/api/papers/{test_paper["id"]}/tags',
        headers={'Authorization': f'Bearer {second_auth_token}'},
        json={'tag_id': test_tag['id']}
    )
    
    assert response.status_code == 404  # Paper not found for this user


def test_get_tags_other_users_paper(client, second_auth_token, test_paper):
    """
    Test user cannot get tags of another user's paper
    """
    response = client.get(
        f'/api/papers/{test_paper["id"]}/tags',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404


# ============= EDGE CASES =============

@pytest.mark.parametrize('color', [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00',
    '#FF5733', '#C70039', '#900C3F', '#581845'
])
def test_create_tag_various_colors(client, auth_headers, color):
    """
    Test creating tags with various colors
    """
    response = client.post(
        '/api/tags',
        headers=auth_headers,
        json={'name': f'Tag-{color}', 'color': color}
    )
    
    assert response.status_code == 201
    assert response.json['tag']['color'] == color


def test_tag_with_special_characters(client, auth_headers):
    """
    Test creating tag with special characters in name
    """
    response = client.post(
        '/api/tags',
        headers=auth_headers,
        json={'name': 'ML/AI & Deep Learning (2024)', 'color': '#FF0000'}
    )
    
    assert response.status_code == 201
    assert response.json['tag']['name'] == 'ML/AI & Deep Learning (2024)'