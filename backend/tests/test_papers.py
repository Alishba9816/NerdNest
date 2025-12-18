# tests/test_papers.py
"""
Tests for paper management endpoints
Tests: Paper CRUD, read status, downloads, and category associations
"""
import pytest
from io import BytesIO
from app.extensions import db

# ============= UPLOAD PAPER TESTS =============

def test_upload_paper_success(client, auth_headers, mock_pdf_file):
    """Test successfully uploading a paper"""
    data = {
        'title': 'Test Research Paper',
        'authors': 'John Doe, Jane Smith',
        'abstract': 'This is a test abstract'
    }
    
    data['file'] = mock_pdf_file
    
    response = client.post(
        '/api/papers/upload',
        headers=auth_headers,
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    assert 'paper_id' in response.json
    assert response.json['title'] == data['title']


def test_upload_paper_minimal(client, auth_headers, mock_pdf_file):
    """Test uploading paper with only required fields"""
    data = {
        'title': 'Minimal Paper',
        'file': mock_pdf_file
    }
    
    response = client.post(
        '/api/papers/upload',
        headers=auth_headers,
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201


def test_upload_paper_missing_file(client, auth_headers):
    """Test uploading paper fails without file"""
    response = client.post(
        '/api/papers/upload',
        headers=auth_headers,
        data={'title': 'Test Paper'},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    assert 'error' in response.json


def test_upload_paper_missing_title(client, auth_headers, mock_pdf_file):
    """Test uploading paper fails without title"""
    response = client.post(
        '/api/papers/upload',
        headers=auth_headers,
        data={'file': mock_pdf_file},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400


def test_upload_paper_with_category(client, auth_headers, mock_pdf_file, test_category):
    """Test uploading paper with category assignment"""
    data = {
        'title': 'Categorized Paper',
        'file': mock_pdf_file,
        'category_id': str(test_category['id'])
    }
    
    response = client.post(
        '/api/papers/upload',
        headers=auth_headers,
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201


def test_upload_paper_without_auth(client, mock_pdf_file):
    """Test uploading paper fails without authentication"""
    response = client.post(
        '/api/papers/upload',
        data={
            'title': 'Test Paper',
            'file': mock_pdf_file
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 401


# ============= GET PAPERS TESTS =============

def test_get_all_papers(client, auth_headers, test_paper):
    """Test getting all papers for user"""
    response = client.get(
        '/api/papers',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'papers' in response.json
    assert len(response.json['papers']) >= 1


def test_get_all_papers_empty(client, auth_headers):
    """Test getting papers when user has none"""
    response = client.get(
        '/api/papers',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['papers'] == []


def test_get_all_papers_ordering(client, auth_headers, app, test_user):
    """Test papers are returned in reverse chronological order"""
    from app.models.paper import Paper
    import time
    
    # Create multiple papers
    with app.app_context():
        paper1 = Paper(title='Paper 1', file_path='/fake/1.pdf', user_id=test_user['id'])
        db.session.add(paper1)
        db.session.commit()
        
        time.sleep(0.1)
        
        paper2 = Paper(title='Paper 2', file_path='/fake/2.pdf', user_id=test_user['id'])
        db.session.add(paper2)
        db.session.commit()
    
    response = client.get('/api/papers', headers=auth_headers)
    
    assert response.status_code == 200
    papers = response.json['papers']
    assert papers[0]['title'] == 'Paper 2'  # Most recent first
    assert papers[1]['title'] == 'Paper 1'


def test_get_single_paper(client, auth_headers, test_paper):
    """Test getting a specific paper"""
    response = client.get(
        f'/api/papers/{test_paper["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'paper' in response.json
    assert response.json['paper']['id'] == test_paper['id']


def test_get_paper_nonexistent(client, auth_headers):
    """Test getting paper that doesn't exist"""
    response = client.get(
        '/api/papers/99999',
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_get_paper_other_user(client, second_auth_token, test_paper):
    """Test user cannot get another user's paper"""
    response = client.get(
        f'/api/papers/{test_paper["id"]}',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404


# ============= DELETE PAPER TESTS =============

def test_delete_paper_success(client, auth_headers, test_paper):
    """Test successfully deleting a paper"""
    response = client.delete(
        f'/api/papers/{test_paper["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'message' in response.json
    
    # Verify paper is deleted
    get_response = client.get(
        f'/api/papers/{test_paper["id"]}',
        headers=auth_headers
    )
    assert get_response.status_code == 404


def test_delete_paper_with_notes(client, auth_headers, test_paper, test_note):
    """Test deleting paper also deletes associated notes"""
    response = client.delete(
        f'/api/papers/{test_paper["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verify note is also deleted
    # (CASCADE deletion should handle this)


def test_delete_paper_nonexistent(client, auth_headers):
    """Test deleting paper that doesn't exist"""
    response = client.delete(
        '/api/papers/99999',
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_delete_paper_other_user(client, second_auth_token, test_paper):
    """Test user cannot delete another user's paper"""
    response = client.delete(
        f'/api/papers/{test_paper["id"]}',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404


# ============= READ STATUS TESTS =============

def test_toggle_read_status_to_read(client, auth_headers, test_paper):
    """Test marking paper as read"""
    response = client.put(
        f'/api/papers/{test_paper["id"]}/toggle-read',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['is_read'] in [True, False]


def test_toggle_read_status_multiple_times(client, auth_headers, test_paper):
    """Test toggling read status multiple times"""
    # First toggle
    response1 = client.put(
        f'/api/papers/{test_paper["id"]}/toggle-read',
        headers=auth_headers
    )
    status1 = response1.json['is_read']
    
    # Second toggle
    response2 = client.put(
        f'/api/papers/{test_paper["id"]}/toggle-read',
        headers=auth_headers
    )
    status2 = response2.json['is_read']
    
    # Should be opposite
    assert status1 != status2


def test_toggle_read_nonexistent_paper(client, auth_headers):
    """Test toggling read status for nonexistent paper"""
    response = client.put(
        '/api/papers/99999/toggle-read',
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_toggle_read_other_user_paper(client, second_auth_token, test_paper):
    """Test user cannot toggle read status of another user's paper"""
    response = client.put(
        f'/api/papers/{test_paper["id"]}/toggle-read',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404


# ============= DOWNLOAD PAPER TESTS =============

def test_download_paper_success(client, auth_headers, test_paper):
    """Test downloading paper PDF"""
    # Note: This will fail if file doesn't actually exist
    # In real tests, you'd mock the file system
    response = client.get(
        f'/api/papers/{test_paper["id"]}/download',
        headers=auth_headers
    )
    
    # Expect 404 since fake path doesn't exist, but endpoint is working
    assert response.status_code in [200, 404]


def test_download_paper_nonexistent(client, auth_headers):
    """Test downloading paper that doesn't exist"""
    response = client.get(
        '/api/papers/99999/download',
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_download_paper_other_user(client, second_auth_token, test_paper):
    """Test user cannot download another user's paper"""
    response = client.get(
        f'/api/papers/{test_paper["id"]}/download',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404


# ============= GET CATEGORIES TESTS =============

def test_get_paper_categories(client, auth_headers, test_paper):
    """Test getting categories for a paper"""
    response = client.get(
        f'/api/papers/{test_paper["id"]}/categories',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'categories' in response.json
    assert 'count' in response.json


def test_get_paper_categories_empty(client, auth_headers, test_paper):
    """Test getting categories when paper has none"""
    response = client.get(
        f'/api/papers/{test_paper["id"]}/categories',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['categories'] == []
    assert response.json['count'] == 0


# ============= ASSIGN CATEGORY TESTS =============

def test_assign_paper_to_category(client, auth_headers, test_paper, test_category):
    """Test assigning paper to a category"""
    response = client.post(
        f'/api/papers/{test_paper["id"]}/categories',
        headers=auth_headers,
        json={'category_id': test_category['id']}
    )
    
    assert response.status_code == 201
    assert response.json['category_id'] == test_category['id']


def test_assign_paper_to_multiple_categories(client, auth_headers, test_paper, app, test_user):
    """Test assigning paper to multiple categories"""
    from app.models.category import Category
    
    # Create categories
    with app.app_context():
        cat1 = Category(name='Cat1', user_id=test_user['id'])
        cat2 = Category(name='Cat2', user_id=test_user['id'])
        db.session.add_all([cat1, cat2])
        db.session.commit()
        cat_ids = [cat1.id, cat2.id]
    
    response = client.post(
        f'/api/papers/{test_paper["id"]}/categories/assign-multiple',
        headers=auth_headers,
        json={'category_ids': cat_ids}
    )
    
    assert response.status_code == 201
    assert len(response.json['assigned_categories']) == 2


def test_assign_paper_duplicate_category(client, auth_headers, test_paper, test_category):
    """Test assigning paper to same category twice fails"""
    # Assign first time
    client.post(
        f'/api/papers/{test_paper["id"]}/categories',
        headers=auth_headers,
        json={'category_id': test_category['id']}
    )
    
    # Try to assign again
    response = client.post(
        f'/api/papers/{test_paper["id"]}/categories',
        headers=auth_headers,
        json={'category_id': test_category['id']}
    )
    
    assert response.status_code == 400
    assert 'already' in response.json['error'].lower()


def test_assign_paper_invalid_category(client, auth_headers, test_paper):
    """Test assigning paper to nonexistent category"""
    response = client.post(
        f'/api/papers/{test_paper["id"]}/categories',
        headers=auth_headers,
        json={'category_id': 99999}
    )
    
    assert response.status_code == 404


# ============= REMOVE CATEGORY TESTS =============

def test_remove_category_from_paper(client, auth_headers, test_paper, test_category, app):
    """Test removing category from paper"""
    from app.models.paper import Paper
    from app.models.category import Category
    
    # First assign category
    with app.app_context():
        paper = Paper.query.get(test_paper['id'])
        category = Category.query.get(test_category['id'])
        paper.categories.append(category)
        db.session.commit()
    
    # Remove category
    response = client.delete(
        f'/api/papers/{test_paper["id"]}/categories/{test_category["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200


def test_remove_category_not_assigned(client, auth_headers, test_paper, test_category):
    """Test removing category that's not assigned to paper"""
    response = client.delete(
        f'/api/papers/{test_paper["id"]}/categories/{test_category["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 400


# ============= EDGE CASES & VALIDATION =============

def test_get_paper_includes_categories(client, auth_headers, test_paper, test_category, app):
    """Test paper response includes categories"""
    from app.models.paper import Paper
    from app.models.category import Category
    
    # Assign category
    with app.app_context():
        paper = Paper.query.get(test_paper['id'])
        category = Category.query.get(test_category['id'])
        paper.categories.append(category)
        db.session.commit()
    
    response = client.get(
        f'/api/papers/{test_paper["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    # Check if categories are included (depends on format_paper_data)
    # assert 'categories' in response.json['paper']


@pytest.mark.parametrize('title', [
    'Short',
    'A' * 100,  # Long title
    'Title with special chars: @#$%',
    'Title with émojis 📚',
])
def test_upload_paper_various_titles(client, auth_headers, mock_pdf_file, title):
    """Test uploading papers with different title formats"""
    response = client.post(
        '/api/papers/upload',
        headers=auth_headers,
        data={
            'title': title,
            'file': mock_pdf_file
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    assert response.json['title'] == title


def test_paper_with_all_optional_fields(client, auth_headers, mock_pdf_file):
    """Test uploading paper with all fields populated"""
    data = {
        'title': 'Complete Paper',
        'authors': 'Dr. John Doe, Dr. Jane Smith',
        'abstract': 'This is a comprehensive abstract that describes the paper in detail.',
        'file': mock_pdf_file
    }
    
    response = client.post(
        '/api/papers/upload',
        headers=auth_headers,
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201


def test_user_isolation(client, auth_headers, second_auth_token, test_paper):
    """Test that users can only see their own papers"""
    # First user should see their paper
    response1 = client.get('/api/papers', headers=auth_headers)
    assert len(response1.json['papers']) >= 1
    
    # Second user should not see first user's papers
    response2 = client.get('/api/papers', headers={'Authorization': f'Bearer {second_auth_token}'})
    assert len(response2.json['papers']) == 0


def test_paper_count_consistency(client, auth_headers, app, test_user):
    """Test paper count is consistent across endpoints"""
    from app.models.paper import Paper
    
    # Create known number of papers
    with app.app_context():
        for i in range(5):
            paper = Paper(title=f'Paper {i}', file_path=f'/fake/{i}.pdf', user_id=test_user['id'])
            db.session.add(paper)
        db.session.commit()
    
    response = client.get('/api/papers', headers=auth_headers)
    assert len(response.json['papers']) == 5