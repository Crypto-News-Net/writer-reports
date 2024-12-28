from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import sys

def test_imagemagick():
    print("Testing ImageMagick setup...")
    
    try:
        # Print Wand version
        print(f"Wand version: {Image.version}")
        
        # Try to get ImageMagick version info
        with Image() as img:
            print(f"ImageMagick version: {img.quantum_range}")
    except Exception as e:
        print(f"ImageMagick not properly installed: {str(e)}")
        print("Please install ImageMagick from: https://imagemagick.org/script/download.php")
        sys.exit(1)
    
    print("\nTesting emoji rendering...")
    
    try:
        with Drawing() as draw:
            # Set up the drawing context
            draw.font_size = 32
            draw.fill_color = Color('black')
            
            # Try to get system fonts
            print("Available fonts:")
            print(draw.font)
            
            # Create a new image
            with Image(width=400, height=200, background=Color('white')) as img:
                # Draw test text with emojis
                draw.text(20, 40, "Test: 🥇🥈🥉")
                
                # Render the drawing onto the image
                draw(img)
                
                # Save the image
                img.save(filename='imagemagick_test.png')
                print("\nSaved test image as imagemagick_test.png")
    except Exception as e:
        print(f"Error during rendering: {str(e)}")

if __name__ == "__main__":
    test_imagemagick()
