import csv
from PIL import Image, ImageDraw, ImageFont
import os

# Configuration: Path to the CSV file
DATA_FILE = 'locations.csv'

def find_location(query):
    """
    Smart Search Logic:
    1. Check if query matches Name or ID (Start) exactly.
    2. Check if query is contained within the Name (Fuzzy Search).
    3. Finally, treat as a Call Number and check the range (Range Check).
    """
    query = query.strip().upper() # Convert to uppercase for case-insensitive matching
    print(f"🔍 Searching for: {query} ...")

    # --- Phase 1: Exact Match & Name Fuzzy Match (Targets Rooms/Spaces) ---
    with open(DATA_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Prepare data: Convert to uppercase for comparison
            row_start = row['call_start'].upper()
            row_name = row['name'].upper()
            
            # 1. Check ID (e.g., input "N607")
            if query == row_start:
                return row
            
            # 2. Check Name (e.g., input "Scholars Space")
            # If the query is part of the Name column, we consider it a match
            if query in row_name:
                return row

    # --- Phase 2: Call Number Range Match (Targets Shelves) ---
    # If no match found above, re-read the file specifically for range checks
    with open(DATA_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['type'] == 'Shelf':
                start = row['call_start'].upper()
                end = row['call_end'].upper()
                
                # Compare alphabetically/numerically within the range
                if start <= query <= end:
                    return row
                    
    return None # No match found

def draw_pin_on_map(location_data):
    """
    Draw a pin on the map and save as a new image.
    """
    # 1. Open the base map
    base_map_path = location_data['map_file']
    if not os.path.exists(base_map_path):
        print(f"Error: Base map not found at {base_map_path}")
        return None
        
    image = Image.open(base_map_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    
    # 2. Get Coordinates
    x = int(location_data['x'])
    y = int(location_data['y'])
    
    # 3. Draw a prominent red pin
    radius = 40  # Circle size, adjust based on image resolution
    color = "red"
    # Draw outer circle
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline="white", width=5)
    # Draw center dot
    draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="white")
    
    # (Optional) Add text label
    # draw.text((x + radius + 10, y), location_data['name'], fill="black")

    # 4. Save the result
    output_filename = f"result_{location_data['name'].replace(' ', '_')}.jpg"
    image.save(output_filename)
    print(f"✅ Map generated! Saved as: {output_filename}")
    return output_filename

# --- Main Program Simulation ---
if __name__ == "__main__":
    print("--- Library Visual Navigation MVP ---")
    
    user_input = input("Please enter a Room ID or Call Number (e.g., N607 or QA 76.5): ")
    
    result = find_location(user_input)
    
    if result:
        print(f"Found! Location: {result['floor']} - {result['name']}")
        
        # Generate image and get the filename
        output_filename = draw_pin_on_map(result)
        
        # Automatically open the image
        try:
            # Added quotes to handle filenames with spaces or special characters
            os.system(f"open '{output_filename}'")
        except:
            pass
            
    else:
        print("❌ Sorry, no coordinate data found for that location.")