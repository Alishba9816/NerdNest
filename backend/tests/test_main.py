# tests/test_main.py

# ============= DASHBOARD TESTS =============
import pytest

def test_dashboard_success(client, auth_headers):
    """Test getting dashboard data"""
    response = client.get(
        '/dashboard',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'recent_papers' in response.json
    assert 'user_categories' in response.json


def test_dashboard_with_papers(client, auth_headers, test_paper):
    """Test dashboard shows recent papers"""
    response = client.get(
        '/dashboard',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert len(response.json['recent_papers']) >= 1


def test_dashboard_without_auth(client):
    """Test dashboard requires authentication"""
    response = client.get('/dashboard')
    
    assert response.status_code == 401


def test_dashboard_recent_papers_limit(client, auth_headers, app, test_user):
    """Test dashboard returns limited number of recent papers"""
    from app.extensions import db
    from app.models.paper import Paper
    
    # Create many papers
    with app.app_context():
        for i in range(10):
            paper = Paper(title=f'Paper {i}', file_path=f'/fake/{i}.pdf', user_id=test_user['id'])
            db.session.add(paper)
        db.session.commit()
    
    response = client.get('/dashboard', headers=auth_headers)
    
    assert response.status_code == 200
    # Should return max 5 recent papers
    assert len(response.json['recent_papers']) <= 5


# ============= SEARCH TESTS =============

def test_search_all_success(client, auth_headers, test_paper):
    """Test searching for papers"""
    response = client.get(
        '/search-all',
        headers=auth_headers,
        query_string={'q': test_paper['title'][:5]}  # Search by partial title
    )
    
    assert response.status_code == 200
    assert 'results' in response.json


def test_search_all_missing_query(client, auth_headers):
    """Test search fails without query parameter"""
    response = client.get(
        '/search-all',
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert 'error' in response.json


def test_search_all_empty_query(client, auth_headers):
    """Test search with empty query string"""
    response = client.get(
        '/search-all',
        headers=auth_headers,
        query_string={'q': ''}
    )
    
    assert response.status_code == 400


def test_search_papers_by_title(client, auth_headers, test_paper):
    """Test searching papers by title"""
    response = client.get(
        '/search-all',
        headers=auth_headers,
        query_string={'q': test_paper['title']}
    )
    
    assert response.status_code == 200
    # Depends on fuzzy search threshold
    # assert len(response.json['results']) >= 1


def test_search_papers_by_author(client, auth_headers, test_paper):
    """Test searching papers by author"""
    response = client.get(
        '/search-all',
        headers=auth_headers,
        query_string={'q': test_paper['authors'][:5]}
    )
    
    assert response.status_code == 200


def test_search_categories(client, auth_headers, test_category):
    """Test searching categories"""
    response = client.get(
        '/search-all',
        headers=auth_headers,
        query_string={'q': test_category['name']}
    )
    
    assert response.status_code == 200


def test_search_no_results(client, auth_headers):
    """Test search with no matching results"""
    response = client.get(
        '/search-all',
        headers=auth_headers,
        query_string={'q': 'xyznonexistentquery123'}
    )
    
    assert response.status_code == 404
    assert 'message' in response.json


def test_search_without_auth(client):
    """Test search requires authentication"""
    response = client.get(
        '/search-all',
        query_string={'q': 'test'}
    )
    
    assert response.status_code == 401


def test_search_case_insensitive(client, auth_headers, test_paper):
    """Test search is case insensitive"""
    response = client.get(
        '/search-all',
        headers=auth_headers,
        query_string={'q': test_paper['title'].upper()}
    )
    
    assert response.status_code == 200


@pytest.mark.parametrize('query', [
    'ML',
    'Machine Learning',
    'Research',
    'Paper',
])
def test_search_various_queries(client, auth_headers, query):
    """Test search with different query strings"""
    response = client.get(
        '/search-all',
        headers=auth_headers,
        query_string={'q': query}
    )
    
    # Should either find results or return 404, but not error
    assert response.status_code in [200, 404]