# tests/test_categories.py
"""
Tests for category management endpoints
Tests: Category CRUD, hierarchy, and paper associations
"""
import pytest
from app.models.category import Category
from app.extensions import db


# ============= CREATE CATEGORY TESTS =============

def test_create_category_success(client, auth_headers):
    """Test successfully creating a new category"""
    response = client.post(
        '/api/categories/create',
        headers=auth_headers,
        json={
            'name': 'Machine Learning',
            'color': '#3498db',
            'icon': 'fa-brain'
        }
    )
    
    assert response.status_code == 201
    assert 'message' in response.json
    assert 'category' in response.json
    assert response.json['category']['name'] == 'Machine Learning'
    assert response.json['category']['color'] == '#3498db'
    assert response.json['category']['icon'] == 'fa-brain'


def test_create_category_minimal(client, auth_headers):
    """Test creating category with only required fields"""
    response = client.post(
        '/api/categories/create',
        headers=auth_headers,
        json={'name': 'Computer Science'}
    )
    
    assert response.status_code == 201
    assert response.json['category']['name'] == 'Computer Science'
    assert response.json['category']['color'] == '#3498db'  # Default
    assert response.json['category']['icon'] == 'fa-folder'  # Default


def test_create_category_missing_name(client, auth_headers):
    """Test creating category fails without name"""
    response = client.post(
        '/api/categories/create',
        headers=auth_headers,
        json={'color': '#FF0000'}
    )
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'required' in response.json['error'].lower()


def test_create_category_empty_name(client, auth_headers):
    """Test creating category with empty name fails"""
    response = client.post(
        '/api/categories/create',
        headers=auth_headers,
        json={'name': '   '}
    )
    
    assert response.status_code == 400


def test_create_category_invalid_color(client, auth_headers):
    """Test creating category with invalid color format"""
    response = client.post(
        '/api/categories/create',
        headers=auth_headers,
        json={
            'name': 'Test Category',
            'color': 'red'  # Invalid format
        }
    )
    
    assert response.status_code == 400
    assert 'color' in response.json['error'].lower()


def test_create_category_invalid_icon(client, auth_headers):
    """Test creating category with invalid icon format"""
    response = client.post(
        '/api/categories/create',
        headers=auth_headers,
        json={
            'name': 'Test Category',
            'icon': 'invalid-icon'
        }
    )
    
    assert response.status_code == 400
    assert 'icon' in response.json['error'].lower()


def test_create_category_duplicate_name(client, auth_headers, test_category):
    """Test creating category with duplicate name fails"""
    response = client.post(
        '/api/categories/create',
        headers=auth_headers,
        json={'name': test_category['name']}
    )
    
    assert response.status_code == 400
    assert 'already exists' in response.json['error'].lower()


def test_create_category_without_auth(client):
    """Test creating category fails without authentication"""
    response = client.post(
        '/api/categories/create',
        json={'name': 'Test Category'}
    )
    
    assert response.status_code == 401


def test_create_category_long_name(client, auth_headers):
    """Test creating category with name exceeding 100 characters"""
    long_name = 'A' * 101
    response = client.post(
        '/api/categories/create',
        headers=auth_headers,
        json={'name': long_name}
    )
    
    assert response.status_code == 400
    assert '100 characters' in response.json['error']


# ============= VIEW CATEGORY TESTS =============

def test_view_all_categories(client, auth_headers, test_category):
    """Test viewing all top-level categories"""
    response = client.get(
        '/api/categories/view_all',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'categories' in response.json
    assert 'total' in response.json
    assert len(response.json['categories']) >= 1


def test_view_all_categories_empty(client, auth_headers):
    """Test viewing categories when none exist"""
    response = client.get(
        '/api/categories/view_all',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['categories'] == []
    assert response.json['total'] == 0


def test_view_specific_category(client, auth_headers, test_category):
    """Test viewing a specific category"""
    response = client.get(
        f'/api/categories/view/{test_category["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'category' in response.json
    assert 'papers' in response.json
    assert response.json['category']['id'] == test_category['id']


def test_view_category_with_papers(client, auth_headers, app, test_category, test_user):
    """Test viewing category shows its papers"""
    from app.models.paper import Paper
    
    # Create paper and assign to category
    with app.app_context():
        paper = Paper(
            title='Test Paper',
            file_path='/fake/path.pdf',
            user_id=test_user['id']
        )
        category = Category.query.get(test_category['id'])
        paper.categories.append(category)
        db.session.add(paper)
        db.session.commit()
    
    response = client.get(
        f'/api/categories/view/{test_category["id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert len(response.json['papers']) == 1
    assert response.json['paper_count'] == 1


def test_view_category_nonexistent(client, auth_headers):
    """Test viewing category that doesn't exist"""
    response = client.get(
        '/api/categories/view/99999',
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_view_category_other_user(client, second_auth_token, test_category):
    """Test user cannot view another user's category"""
    response = client.get(
        f'/api/categories/view/{test_category["id"]}',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404


# ============= UPDATE CATEGORY TESTS =============

def test_update_category_name(client, auth_headers, test_category):
    """Test updating category name"""
    response = client.put(
        f'/api/categories/{test_category["id"]}/update',
        headers=auth_headers,
        json={'name': 'Updated Name'}
    )
    
    assert response.status_code == 200
    assert response.json['category']['name'] == 'Updated Name'


def test_update_category_color(client, auth_headers, test_category):
    """Test updating category color"""
    response = client.put(
        f'/api/categories/{test_category["id"]}/update',
        headers=auth_headers,
        json={'color': '#FF0000'}
    )
    
    assert response.status_code == 200
    assert response.json['category']['color'] == '#FF0000'


def test_update_category_icon(client, auth_headers, test_category):
    """Test updating category icon"""
    response = client.put(
        f'/api/categories/{test_category["id"]}/update',
        headers=auth_headers,
        json={'icon': 'fa-star'}
    )
    
    assert response.status_code == 200
    assert response.json['category']['icon'] == 'fa-star'


def test_update_category_multiple_fields(client, auth_headers, test_category):
    """Test updating multiple fields at once"""
    response = client.put(
        f'/api/categories/{test_category["id"]}/update',
        headers=auth_headers,
        json={
            'name': 'New Name',
            'color': '#00FF00',
            'icon': 'fa-rocket'
        }
    )
    
    assert response.status_code == 200
    assert response.json['category']['name'] == 'New Name'
    assert response.json['category']['color'] == '#00FF00'
    assert response.json['category']['icon'] == 'fa-rocket'


def test_update_category_empty_name(client, auth_headers, test_category):
    """Test updating category with empty name fails"""
    response = client.put(
        f'/api/categories/{test_category["id"]}/update',
        headers=auth_headers,
        json={'name': '   '}
    )
    
    assert response.status_code == 400


def test_update_category_invalid_color(client, auth_headers, test_category):
    """Test updating with invalid color fails"""
    response = client.put(
        f'/api/categories/{test_category["id"]}/update',
        headers=auth_headers,
        json={'color': 'invalid'}
    )
    
    assert response.status_code == 400


def test_update_category_duplicate_name(client, auth_headers, app, test_user):
    """Test updating to duplicate name fails"""
    from app.models.category import Category
    
    # Create two categories
    with app.app_context():
        cat1 = Category(name='Category 1', user_id=test_user['id'])
        cat2 = Category(name='Category 2', user_id=test_user['id'])
        db.session.add_all([cat1, cat2])
        db.session.commit()
        cat1_id = cat1.id
    
    # Try to rename cat1 to cat2's name
    response = client.put(
        f'/api/categories/{cat1_id}/update',
        headers=auth_headers,
        json={'name': 'Category 2'}
    )
    
    assert response.status_code == 400
    assert 'already exists' in response.json['error'].lower()


def test_update_category_nonexistent(client, auth_headers):
    """Test updating category that doesn't exist"""
    response = client.put(
        '/api/categories/99999/update',
        headers=auth_headers,
        json={'name': 'New Name'}
    )
    
    assert response.status_code == 404


# ============= DELETE CATEGORY TESTS =============

def test_delete_category_success(client, auth_headers, test_category):
    """Test successfully deleting a category"""
    response = client.delete(
        f'/api/categories/{test_category["id"]}/delete',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'message' in response.json
    assert 'deleted' in response.json['message'].lower()
    
    # Verify category is deleted
    get_response = client.get(
        f'/api/categories/view/{test_category["id"]}',
        headers=auth_headers
    )
    assert get_response.status_code == 404


def test_delete_category_with_children(client, auth_headers, app, test_category, test_user):
    """Test deleting category reassigns child categories"""
    from app.models.category import Category
    
    # Create child category
    with app.app_context():
        child = Category(
            name='Child Category',
            parent_id=test_category['id'],
            user_id=test_user['id']
        )
        db.session.add(child)
        db.session.commit()
        child_id = child.id
    
    # Delete parent
    response = client.delete(
        f'/api/categories/{test_category["id"]}/delete',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['details']['children_reassigned'] == 1
    
    # Verify child is now top-level
    with app.app_context():
        child = Category.query.get(child_id)
        assert child.parent_id is None


def test_delete_category_with_papers(client, auth_headers, app, test_category, test_user):
    """Test deleting category detaches papers"""
    from app.models.paper import Paper
    
    # Create paper in category
    with app.app_context():
        paper = Paper(
            title='Test Paper',
            file_path='/fake/path.pdf',
            user_id=test_user['id']
        )
        category = Category.query.get(test_category['id'])
        paper.categories.append(category)
        db.session.add(paper)
        db.session.commit()
        paper_id = paper.id
    
    # Delete category
    response = client.delete(
        f'/api/categories/{test_category["id"]}/delete',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['details']['papers_detached'] == 1
    
    # Verify paper still exists but not in category
    with app.app_context():
        paper = Paper.query.get(paper_id)
        assert paper is not None
        assert len(paper.categories) == 0


def test_delete_category_nonexistent(client, auth_headers):
    """Test deleting category that doesn't exist"""
    response = client.delete(
        '/api/categories/99999/delete',
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_delete_category_other_user(client, second_auth_token, test_category):
    """Test user cannot delete another user's category"""
    response = client.delete(
        f'/api/categories/{test_category["id"]}/delete',
        headers={'Authorization': f'Bearer {second_auth_token}'}
    )
    
    assert response.status_code == 404


# ============= HIERARCHY TESTS =============

def test_get_child_categories(client, auth_headers, app, test_category, test_user):
    """Test getting child categories of a parent"""
    from app.models.category import Category
    
    # Create child categories
    with app.app_context():
        child1 = Category(
            name='Child 1',
            parent_id=test_category['id'],
            user_id=test_user['id']
        )
        child2 = Category(
            name='Child 2',
            parent_id=test_category['id'],
            user_id=test_user['id']
        )
        db.session.add_all([child1, child2])
        db.session.commit()
    
    response = client.get(
        f'/api/categories/{test_category["id"]}/children',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'children' in response.json
    assert response.json['total'] == 2
    assert response.json['parent_id'] == test_category['id']


def test_get_child_categories_empty(client, auth_headers, test_category):
    """Test getting children when category has none"""
    response = client.get(
        f'/api/categories/{test_category["id"]}/children',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['children'] == []
    assert response.json['total'] == 0


def test_get_available_parents(client, auth_headers, test_category):
    """Test getting valid parent options for a category"""
    response = client.get(
        f'/api/categories/{test_category["id"]}/available_parents',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_create_category_with_parent(client, auth_headers, test_category):
    """Test creating subcategory with parent"""
    response = client.post(
        '/api/categories/create',
        headers=auth_headers,
        json={
            'name': 'Subcategory',
            'parent_id': test_category['id']
        }
    )
    
    assert response.status_code == 201
    assert response.json['category']['parent_id'] == test_category['id']


def test_create_category_invalid_parent(client, auth_headers):
    """Test creating category with nonexistent parent fails"""
    response = client.post(
        '/api/categories/create',
        headers=auth_headers,
        json={
            'name': 'Subcategory',
            'parent_id': 99999
        }
    )
    
    assert response.status_code == 404


# ============= EDGE CASES =============

@pytest.mark.parametrize('color', [
    '#000000',  # Black
    '#FFFFFF',  # White
    '#FF5733',  # Custom
    '#3498db',  # Default
])
def test_create_category_various_colors(client, auth_headers, color):
    """Test creating categories with different valid colors"""
    response = client.post(
        '/api/categories/create',
        headers=auth_headers,
        json={
            'name': f'Category {color}',
            'color': color
        }
    )
    
    assert response.status_code == 201
    assert response.json['category']['color'] == color


def test_category_name_with_special_characters(client, auth_headers):
    """Test creating category with special characters in name"""
    response = client.post(
        '/api/categories/create',
        headers=auth_headers,
        json={'name': 'ML/AI & Deep Learning (2024)'}
    )
    
    assert response.status_code == 201
    assert response.json['category']['name'] == 'ML/AI & Deep Learning (2024)'


def test_category_ordering(client, auth_headers, app, test_user):
    """Test categories are returned in alphabetical order"""
    from app.models.category import Category
    
    # Create categories
    with app.app_context():
        cat_z = Category(name='Zebra', user_id=test_user['id'])
        cat_a = Category(name='Apple', user_id=test_user['id'])
        cat_m = Category(name='Mango', user_id=test_user['id'])
        db.session.add_all([cat_z, cat_a, cat_m])
        db.session.commit()
    
    response = client.get('/api/categories/view_all', headers=auth_headers)
    
    assert response.status_code == 200
    categories = response.json['categories']
    names = [cat['name'] for cat in categories]
    assert names == sorted(names)