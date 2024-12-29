from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)
CORS(app)

class WriterStats:
    def __init__(self):
        self.data_file = Path("writer_stats.json")
        self.writers = self.load_data()

    def load_data(self):
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                # Fix any duplicate IDs
                used_ids = set()
                next_id = 1
                fixed_writers = []
                fixed_stats = {}
                
                for writer in data["writers"]:
                    old_id = writer["id"]
                    # If ID is already used, assign a new one
                    while str(next_id) in used_ids:
                        next_id += 1
                    new_id = str(next_id)
                    used_ids.add(new_id)
                    
                    # Update writer with new ID
                    writer["id"] = new_id
                    fixed_writers.append(writer)
                    
                    # Transfer stats to new ID if they exist
                    if old_id in data["stats"]:
                        fixed_stats[new_id] = data["stats"][old_id]
                    else:
                        fixed_stats[new_id] = {"articles": 0, "views": 0}
                    
                    next_id += 1
                
                data["writers"] = fixed_writers
                data["stats"] = fixed_stats
                
                # Save the fixed data
                with open(self.data_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return data
        return {
            "writers": [],
            "stats": {}
        }

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.writers, f, indent=2)

    def add_writer(self, name):
        # Get all existing IDs
        existing_ids = {w["id"] for w in self.writers["writers"]}
        next_id = 1
        
        # Find the next available ID
        while str(next_id) in existing_ids:
            next_id += 1
        
        new_id = str(next_id)
        
        # Add writer with unique ID
        self.writers["writers"].append({
            "id": new_id,
            "name": name
        })
        
        # Initialize stats
        if "stats" not in self.writers:
            self.writers["stats"] = {}
        self.writers["stats"][new_id] = {
            "articles": 0,
            "views": 0
        }
        
        self.save_data()
        return new_id

    def update_stats(self, writer_id, articles, views):
        if "stats" not in self.writers:
            self.writers["stats"] = {}
        
        self.writers["stats"][writer_id] = {
            "articles": articles,
            "views": views
        }
        self.save_data()

    def remove_writer(self, writer_id):
        # Remove writer from writers list
        self.writers["writers"] = [w for w in self.writers["writers"] if w["id"] != writer_id]
        # Remove writer's stats
        if writer_id in self.writers["stats"]:
            del self.writers["stats"][writer_id]
        self.save_data()

    def get_writer_stats(self):
        stats = []
        for writer in self.writers["writers"]:
            writer_id = writer["id"]
            writer_stats = self.writers["stats"].get(writer_id, {"articles": 0, "views": 0})
            stats.append({
                "id": writer_id,
                "name": writer["name"],
                "articles": writer_stats["articles"],
                "views": writer_stats["views"],
                "avg_views": round(writer_stats["views"] / writer_stats["articles"]) if writer_stats["articles"] > 0 else 0
            })
        return sorted(stats, key=lambda x: (x["articles"], x["views"]), reverse=True)

def generate_report_image(writer_stats, start_date=None, end_date=None):
    # Fixed width
    width = 1000
    
    # Calculate dynamic height based on content
    header_height = 100
    cards_section_height = 250  # Cards (120) + padding (80 top, 50 bottom)
    table_header_height = 140   # Title + headers + borders + padding
    row_height = 50
    row_spacing = 8
    
    # Calculate needed height for all writers
    num_writers = len(writer_stats["writers"])
    writers_section_height = (row_height + row_spacing) * num_writers - row_spacing  # Subtract last spacing
    
    # Total height with minimum of 800px
    total_height = max(800, header_height + cards_section_height + table_header_height + writers_section_height + 40)  # 40px bottom padding
    
    # Create image with white background
    img = Image.new('RGB', (width, total_height), 'white')
    
    # Verify image dimensions
    assert img.size == (width, total_height), f"Image dimensions mismatch. Expected {width}x{total_height}, got {img.size[0]}x{img.size[1]}"
    
    # Enable anti-aliasing
    draw = ImageDraw.Draw(img, 'RGB')
    
    # Enhanced colors for better contrast
    header_blue = '#2563EB'  # Darker, more vibrant blue
    text_gray = '#374151'    # Darker gray for better readability
    row_alt_bg = '#E8EDF5'   # More distinct alternate row color
    border_color = '#D1D5DB' # Border color for cards and table
    
    # Use Windows system fonts directly for better rendering
    WINDOWS_FONT_PATH = "C:/Windows/Fonts/"
    
    try:
        # Use bold fonts for headers and titles
        title_font = ImageFont.truetype(WINDOWS_FONT_PATH + "arialbd.ttf", 44)  # Arial Bold
        header_font = ImageFont.truetype(WINDOWS_FONT_PATH + "arialbd.ttf", 32)  # Arial Bold
        normal_font = ImageFont.truetype(WINDOWS_FONT_PATH + "arial.ttf", 24)    # Arial Regular
    except Exception as e:
        print(f"Error loading fonts: {str(e)}")
        # Fallback to basic fonts with larger sizes
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
    
    # Draw blue header background
    draw.rectangle([0, 0, width, header_height], fill=header_blue)
    
    # Draw title
    draw.text((40, 20), "Writer Reports", fill='white', font=title_font)
    
    # Draw date range
    if start_date and end_date:
        draw.text((40, 65), f"{start_date} - {end_date}", fill='white', font=header_font)
    
    # Calculate summary stats
    total_writers = len(writer_stats["writers"])
    total_articles = sum(w["articles"] for w in writer_stats["writers"])
    total_views = sum(w["views"] for w in writer_stats["writers"])
    avg_views = round(total_views / total_articles) if total_articles > 0 else 0
    
    # Draw summary cards with larger dimensions for better spacing
    card_width = 230
    card_height = 120
    card_spacing = 20
    cards_y = 120
    
    stats = [
        ("Total Writers", str(total_writers)),
        ("Total Articles", str(total_articles)),
        ("Total Views", f"{total_views:,}"),
        ("Avg Views/Article", str(avg_views))
    ]
    
    # Calculate total cards width and start position to center them
    total_cards_width = (card_width * 4) + (card_spacing * 3)
    cards_start_x = (width - total_cards_width) // 2
    
    for i, (label, value) in enumerate(stats):
        x = cards_start_x + i * (card_width + card_spacing)
        # Draw enhanced card with border
        # Shadow
        draw.rectangle([x+3, cards_y+3, x + card_width+3, cards_y + card_height+3], fill='#E5E7EB')
        # Background
        draw.rectangle([x, cards_y, x + card_width, cards_y + card_height], fill='white')
        # Border
        draw.rectangle([x, cards_y, x + card_width, cards_y + card_height], outline=border_color, width=2)
        # Stats with increased padding
        value_bbox = header_font.getbbox(value)
        value_width = value_bbox[2] - value_bbox[0]
        value_x = x + (card_width - value_width) // 2  # Center text horizontally
        draw.text((value_x, cards_y + 25), value, fill='black', font=header_font)
        label_bbox = normal_font.getbbox(label)
        label_width = label_bbox[2] - label_bbox[0]
        label_x = x + (card_width - label_width) // 2  # Center text horizontally
        draw.text((label_x, cards_y + 70), label, fill=text_gray, font=normal_font)
    
    # Draw writer leaderboard with increased spacing
    y = cards_y + 160
    
    # Draw "Writer Leaderboard" heading with more padding
    draw.text((40, y), "Writer Leaderboard", fill='black', font=header_font)
    y += 60
    
    # Draw table headers with wider spacing for larger width
    headers = ["Writer", "Articles", "Views", "Avg Views/Article"]
    header_positions = [40, 400, 600, 780]
    
    for header, x in zip(headers, header_positions):
        draw.text((x, y), header, fill=text_gray, font=normal_font)
    y += 35
    
    # Draw table border and separator
    # Top border
    draw.line([40, y - 5, width - 40, y - 5], fill=border_color, width=2)
    # Bottom border of header
    draw.line([40, y + 30, width - 40, y + 30], fill=border_color, width=2)
    y += 40
    
    # Draw writer stats with consistent spacing
    for i, writer in enumerate(writer_stats["writers"]):
        row_y = y + (row_height + row_spacing) * i
        
        # Draw alternating row background
        if i % 2 == 1:
            draw.rectangle([40, row_y, width - 40, row_y + row_height], fill=row_alt_bg)
        
        # Draw row border
        draw.line([40, row_y + row_height, width - 40, row_y + row_height], fill=border_color)
        
        # Center text vertically within row (using approximate font height)
        text_y = row_y + (row_height - 30) // 2  # 30 is approximate height for 24px font
        
        # Draw writer stats with improved alignment
        text = f"{i+1}. {writer['name']}"
        draw.text((40, text_y), text, fill='black', font=normal_font)
        
        # Draw stats with proper alignment
        draw.text((400, text_y), str(writer["articles"]), fill='black', font=normal_font)
        draw.text((600, text_y), f"{writer['views']:,}", fill='black', font=normal_font)
        draw.text((780, text_y), str(writer["avg_views"]), fill='black', font=normal_font)
    
    # Convert to bytes with maximum quality
    img_bytes = io.BytesIO()
    # Debug logging before save
    print(f"Final image size before save: {img.size[0]}x{img.size[1]}")
    print(f"Image mode: {img.mode}")
    
    # Verify final dimensions before saving
    if img.size != (width, total_height):
        raise ValueError(f"Image dimensions changed during processing. Expected {width}x{total_height}, got {img.size[0]}x{img.size[1]}")
    
    # Save with maximum quality and no compression
    img.save(
        img_bytes,
        format='PNG',
        quality=100,
        dpi=(600, 600),
        optimize=False,
        compress_level=0
    )
    img_bytes.seek(0)
    
    return img_bytes

# Initialize WriterStats
stats = WriterStats()

@app.route('/writers', methods=['GET'])
def get_writers():
    writer_stats = stats.get_writer_stats()
    total_articles = sum(w["articles"] for w in writer_stats)
    total_views = sum(w["views"] for w in writer_stats)
    
    return jsonify({
        "writers": writer_stats,
        "summary": {
            "total_writers": len(writer_stats),
            "total_articles": total_articles,
            "total_views": total_views,
            "avg_views_per_article": round(total_views / total_articles) if total_articles > 0 else 0
        }
    })

@app.route('/writers', methods=['POST'])
def add_writer():
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({"error": "Name is required"}), 400
        
    writer_id = stats.add_writer(name)
    return jsonify({"id": writer_id, "name": name}), 201

@app.route('/writers/<writer_id>', methods=['PUT'])
def update_writer_stats(writer_id):
    data = request.get_json()
    articles = data.get('articles', 0)
    views = data.get('views', 0)
    
    if not isinstance(articles, int) or not isinstance(views, int):
        return jsonify({"error": "Articles and views must be integers"}), 400
        
    stats.update_stats(writer_id, articles, views)
    return jsonify({"success": True})

@app.route('/writers/<writer_id>', methods=['DELETE'])
def remove_writer(writer_id):
    stats.remove_writer(writer_id)
    return jsonify({"success": True})

def log_image_info(img):
    """Debug helper to log image details"""
    print(f"Image Details:")
    print(f"Size: {img.size}")
    print(f"Mode: {img.mode}")
    print(f"Format: {img.format if hasattr(img, 'format') else 'N/A'}")
    print(f"Info: {img.info if hasattr(img, 'info') else 'N/A'}")

@app.route('/export', methods=['POST', 'OPTIONS'])
def export_report():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    writer_stats = {
        "writers": stats.get_writer_stats()
    }
    
    try:
        print("Starting report generation...")
        img_bytes = generate_report_image(writer_stats, start_date, end_date)
        print("Report generation completed successfully")
        
        response = send_file(
            img_bytes,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'writer_report_{start_date}_to_{end_date}.png'
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({"error": "Failed to generate report"}), 500

if __name__ == '__main__':
    app.run(debug=True)
