import sys
print("Python path:", sys.path)

try:
    from app.services.location_service import get_schools_in_radius
    print("✓ Import successful!")
except Exception as e:
    print("✗ Import failed:", e)
    
import os
print("\nFiles in app/services/:")
print(os.listdir("app/services/"))