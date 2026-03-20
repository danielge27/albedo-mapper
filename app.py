# app.py
# Flask web application for Urban Albedo Thermal Audit
# Simple version with interactive map

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image
import base64
from datetime import datetime
import math

# Import the albedo calculation modules
from surface_detector import detect_surfaces, SURFACES
from albedo_calculator import (
    calculate_neighborhood_albedo,
    calculate_heat_index,
    get_heat_grade,
    generate_recommendations,
    estimate_temperature_impact
)
from report_generator import generate_full_report

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/outputs'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def geocode_address(address):
    """Convert address to lat/lon using Nominatim API"""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "AlbedoMapper/1.0"}
    
    # Check if input is a US zip code (5 digits)
    clean_input = address.strip()
    if clean_input.isdigit() and len(clean_input) == 5:
        # For US zip codes, add "USA" to improve accuracy
        query = f"{clean_input}, USA"
        params = {
            "q": query,
            "format": "json",
            "limit": 1,
            "countrycodes": "us"
        }
    else:
        # Regular address search
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        if data:
            display_name = data[0]["display_name"]
            # For zip codes, make the display name cleaner
            if clean_input.isdigit() and len(clean_input) == 5:
                display_name = f"ZIP {clean_input} - {display_name}"
            return {
                "lat": float(data[0]["lat"]),
                "lon": float(data[0]["lon"]),
                "display_name": display_name
            }
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None


def fetch_map_image(lat, lon, zoom, width=800, height=600):
    """Fetch satellite image tiles and stitch them"""
    
    def lat_lon_to_tile(lat, lon, zoom):
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return x, y
    
    tile_size = 256
    tiles_x = math.ceil(width / tile_size) + 1
    tiles_y = math.ceil(height / tile_size) + 1
    
    center_tile_x, center_tile_y = lat_lon_to_tile(lat, lon, zoom)
    
    # Fetch tiles
    start_tile_x = center_tile_x - tiles_x // 2
    start_tile_y = center_tile_y - tiles_y // 2
    
    full_image = np.zeros((tiles_y * tile_size, tiles_x * tile_size, 3), dtype=np.uint8)
    
    for dy in range(tiles_y):
        for dx in range(tiles_x):
            tx = start_tile_x + dx
            ty = start_tile_y + dy
            
            url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{ty}/{tx}"
            
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    tile = np.array(img)
                    if len(tile.shape) == 3 and tile.shape[2] == 4:
                        tile = tile[:, :, :3]
                    full_image[dy*tile_size:(dy+1)*tile_size, dx*tile_size:(dx+1)*tile_size] = tile
            except:
                pass
    
    # Crop to requested size, centered
    center_y = (tiles_y * tile_size) // 2
    center_x = (tiles_x * tile_size) // 2
    
    start_y = max(0, center_y - height // 2)
    start_x = max(0, center_x - width // 2)
    
    cropped = full_image[start_y:start_y+height, start_x:start_x+width]
    
    # Convert RGB to BGR for OpenCV
    result = cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR)
    
    return result


def process_image_for_albedo(image, location_name):
    """Process the image through albedo pipeline"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_path = f"static/outputs/temp_{timestamp}.jpg"
    cv2.imwrite(temp_path, image)
    
    try:
        original, annotated, results, total_px = detect_surfaces(temp_path)
        
        albedo = calculate_neighborhood_albedo(results)
        heat_index = calculate_heat_index(results)
        grade, risk, grade_color = get_heat_grade(heat_index)
        recs = generate_recommendations(results, location_name)
        temp_excess = estimate_temperature_impact(results)
        
        report_path = generate_full_report(
            temp_path, annotated, original, results,
            location_name, output_dir="static/outputs"
        )
        
        _, original_buffer = cv2.imencode('.jpg', original)
        original_b64 = base64.b64encode(original_buffer).decode('utf-8')
        
        _, annotated_buffer = cv2.imencode('.jpg', annotated)
        annotated_b64 = base64.b64encode(annotated_buffer).decode('utf-8')
        
        surface_data = []
        for name, data in sorted(results.items(), key=lambda x: x[1]["coverage_pct"], reverse=True):
            surface_data.append({
                "name": data["label"],
                "coverage": data["coverage_pct"],
                "albedo": data["albedo"],
                "heat_risk": data["heat_risk"],
                "color": f"rgb({data['color'][2]}, {data['color'][1]}, {data['color'][0]})"
            })
        
        rec_data = [{"emoji": r["emoji"], "title": r["title"], "detail": r["detail"], 
                     "policy": r["policy"], "priority": r["priority"]} for r in recs[:4]]
        
        return {
            "success": True,
            "location": location_name,
            "metrics": {
                "albedo": albedo,
                "heat_index": heat_index,
                "grade": grade,
                "risk": risk,
                "grade_color": grade_color,
                "temp_excess": temp_excess
            },
            "surfaces": surface_data,
            "recommendations": rec_data,
            "images": {
                "original": original_b64,
                "annotated": annotated_b64,
                "report": os.path.basename(report_path)
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/geocode', methods=['POST'])
def geocode():
    data = request.get_json()
    address = data.get('address', '')
    
    if not address:
        return jsonify({"success": False, "error": "Enter an address"})
    
    location = geocode_address(address)
    if not location:
        return jsonify({"success": False, "error": "Address not found"})
    
    return jsonify({"success": True, **location})


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    zoom = data.get('zoom', 18)
    location_name = data.get('location_name', 'Selected Area')
    
    # Fetch the visible map area
    image = fetch_map_image(lat, lon, zoom, width=800, height=600)
    
    if image is None:
        return jsonify({"success": False, "error": "Could not fetch imagery"})
    
    result = process_image_for_albedo(image, location_name)
    return jsonify(result)


@app.route('/static/outputs/<filename>')
def serve_output(filename):
    return send_from_directory('static/outputs', filename)


if __name__ == '__main__':
    print("\n" + "="*50)
    print("  Urban Albedo Thermal Audit - Web Version")
    print("="*50)
    print("\n  Open: http://localhost:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
