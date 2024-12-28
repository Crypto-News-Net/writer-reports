from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def test_reportlab():
    print("Testing reportlab for emoji rendering...")
    
    # Register the emoji font
    try:
        pdfmetrics.registerFont(TTFont('NotoEmoji', 'NotoColorEmoji.ttf'))
        print("Successfully registered NotoEmoji font")
    except Exception as e:
        print(f"Font registration failed: {str(e)}")
    
    # Create a PDF
    c = canvas.Canvas("emoji_test.pdf", pagesize=letter)
    
    # Try different font sizes
    try:
        c.setFont('NotoEmoji', 32)
        c.drawString(72, 720, "🥇 Gold Medal")
        c.setFont('NotoEmoji', 24)
        c.drawString(72, 680, "🥈 Silver Medal")
        c.setFont('NotoEmoji', 16)
        c.drawString(72, 640, "🥉 Bronze Medal")
        print("Drew emoji text")
    except Exception as e:
        print(f"Drawing failed: {str(e)}")
    
    try:
        c.save()
        print("Saved test PDF")
    except Exception as e:
        print(f"Save failed: {str(e)}")

if __name__ == "__main__":
    test_reportlab()
