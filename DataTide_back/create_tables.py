import sys
import os

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from DataTide_back.core.database import Base, engine
from DataTide_back.db.models.ground_weather import GroundWeather
from DataTide_back.db.models.item import Item
from DataTide_back.db.models.item_retail import ItemRetail
from DataTide_back.db.models.location import Location
from DataTide_back.db.models.sea_weather import SeaWeather

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
