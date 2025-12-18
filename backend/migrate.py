from flask_migrate import Migrate
from app import create_app, db
from app.models import *

app = create_app()
migrate = Migrate(app, db)
print("Flask app and database migration setup complete.")

# queries to run on cli
# flask db init
# flask db migrate -m "Initial migration."
# flask db upgrade
