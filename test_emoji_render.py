from PIL import Image, ImageDraw, ImageFont
import io

def test_emoji_render():
    # Create a simple test image
    img = Image.new('RGB', (400, 200), 'white')
    draw = ImageDraw.Draw(img)
    
    print("Testing emoji rendering...")
    
    # Test with default font
    try:
        default_font = ImageFont.load_default()
        draw.text((20, 20), "Default font: 🥇🥈🥉", font=default_font, fill='black')
        print("Drew with default font")
    except Exception as e:
        print(f"Default font failed: {str(e)}")
    
    # Test with system fonts
    system_fonts = [
        'segoe ui emoji',  # Windows emoji font
        'apple color emoji',  # macOS emoji font
        'noto color emoji',  # Linux emoji font
    ]
    
    y = 60
    for font_name in system_fonts:
        try:
            font = ImageFont.truetype(font_name, 32)
            draw.text((20, y), f"{font_name}: 🥇🥈🥉", font=font, fill='black')
            print(f"Drew with {font_name}")
            y += 40
        except Exception as e:
            print(f"{font_name} failed: {str(e)}")
    
    # Save the test image
    img.save('emoji_test.png')
    print("Saved test image as emoji_test.png")

if __name__ == "__main__":
    test_emoji_render()
