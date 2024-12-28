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
    # Fixed dimensions matching the original design
    width = 1000
    height = 800
    
    # Create image with white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Colors matching the original design
    header_blue = '#4A90E2'
    text_gray = '#666666'
    row_alt_bg = '#F8F9FA'
    
    # Try to use Arial font, fallback to default if not available
    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        header_font = ImageFont.truetype("arial.ttf", 24)
        normal_font = ImageFont.truetype("arial.ttf", 20)
    except:
        # If Arial is not available, use default font
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
    
    # Draw blue header background
    draw.rectangle([0, 0, width, 120], fill=header_blue)
    
    # Draw title
    draw.text((40, 30), "Writer Reports", fill='white', font=title_font)
    
    # Draw date range
    if start_date and end_date:
        draw.text((40, 70), f"{start_date} - {end_date}", fill='white', font=header_font)
    
    # Calculate summary stats
    total_writers = len(writer_stats["writers"])
    total_articles = sum(w["articles"] for w in writer_stats["writers"])
    total_views = sum(w["views"] for w in writer_stats["writers"])
    avg_views = round(total_views / total_articles) if total_articles > 0 else 0
    
    # Draw summary cards
    card_width = 220
    card_spacing = 20
    cards_y = 140
    
    stats = [
        ("Total Writers", str(total_writers)),
        ("Total Articles", str(total_articles)),
        ("Total Views", f"{total_views:,}"),
        ("Avg Views/Article", str(avg_views))
    ]
    
    for i, (label, value) in enumerate(stats):
        x = 40 + i * (card_width + card_spacing)
        # Draw card shadow
        draw.rectangle([x+2, cards_y+2, x + card_width+2, cards_y + 100+2], fill='#E5E7EB')
        # Draw white card background
        draw.rectangle([x, cards_y, x + card_width, cards_y + 100], fill='white')
        # Draw stats
        draw.text((x + 20, cards_y + 20), value, fill='black', font=header_font)
        draw.text((x + 20, cards_y + 60), label, fill=text_gray, font=normal_font)
    
    # Draw writer leaderboard
    y = cards_y + 140
    
    # Draw "Writer Leaderboard" heading
    draw.text((40, y), "Writer Leaderboard", fill='black', font=header_font)
    y += 40
    
    # Draw table headers
    headers = ["Writer", "Articles", "Views", "Avg Views/Article"]
    header_positions = [40, 400, 600, 800]
    
    for header, x in zip(headers, header_positions):
        draw.text((x, y), header, fill=text_gray, font=normal_font)
    y += 30
    
    # Draw separator line
    draw.line([40, y, width - 40, y], fill='#E5E7EB')
    y += 20
    
    # Draw writer stats
    for i, writer in enumerate(writer_stats["writers"]):
        # Draw alternating row background
        if i % 2 == 1:
            draw.rectangle([40, y - 10, width - 40, y + 30], fill=row_alt_bg)
        
        # Draw writer stats
        text = f"{i+1}. {writer['name']}"
        draw.text((40, y), text, fill='black', font=normal_font)
        draw.text((400, y), str(writer["articles"]), fill='black', font=normal_font)
        draw.text((600, y), f"{writer['views']:,}", fill='black', font=normal_font)
        draw.text((800, y), str(writer["avg_views"]), fill='black', font=normal_font)
        
        y += 40
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG', quality=95)
    img_bytes.seek(0)
    
    return img_bytes

# Initialize WriterStats
stats = WriterStats()

@app.route('/api/writers', methods=['GET'])
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

@app.route('/api/writers', methods=['POST'])
def add_writer():
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({"error": "Name is required"}), 400
        
    writer_id = stats.add_writer(name)
    return jsonify({"id": writer_id, "name": name}), 201

@app.route('/api/writers/<writer_id>', methods=['PUT'])
def update_writer_stats(writer_id):
    data = request.get_json()
    articles = data.get('articles', 0)
    views = data.get('views', 0)
    
    if not isinstance(articles, int) or not isinstance(views, int):
        return jsonify({"error": "Articles and views must be integers"}), 400
        
    stats.update_stats(writer_id, articles, views)
    return jsonify({"success": True})

@app.route('/api/writers/<writer_id>', methods=['DELETE'])
def remove_writer(writer_id):
    stats.remove_writer(writer_id)
    return jsonify({"success": True})

@app.route('/api/export', methods=['POST', 'OPTIONS'])
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
    
    img_bytes = generate_report_image(writer_stats, start_date, end_date)
    
    response = send_file(
        img_bytes,
        mimetype='image/png',
        as_attachment=True,
        download_name=f'writer_report_{start_date}_to_{end_date}.png'
    )
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(debug=True)
