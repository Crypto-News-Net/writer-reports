import cairo
import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango, PangoCairo

def test_cairo():
    # Create a surface and context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 200)
    context = cairo.Context(surface)
    
    # Set white background
    context.set_source_rgb(1, 1, 1)
    context.paint()
    
    # Create Pango layout
    layout = PangoCairo.create_layout(context)
    
    # Set text with emojis
    text = "Test: 🥇🥈🥉"
    layout.set_text(text, -1)
    
    # Set font
    font = Pango.FontDescription("Sans 20")
    layout.set_font_description(font)
    
    # Draw text
    context.set_source_rgb(0, 0, 0)
    PangoCairo.show_layout(context, layout)
    
    # Save to PNG
    surface.write_to_png("cairo_test.png")
    print("Saved test image as cairo_test.png")

if __name__ == "__main__":
    test_cairo()
