#!/usr/bin/env python3
"""
Simple APEX Icon Generator
Creates a basic icon for the APEX application
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_apex_icon():
        # Create a 512x512 icon (standard macOS app icon size)
        size = 512
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Create a modern gradient background
        for i in range(size):
            # Cyberpunk-style gradient: dark blue to bright cyan
            r = int(20 + (i / size) * 20)  # 20-40
            g = int(40 + (i / size) * 160)  # 40-200
            b = int(80 + (i / size) * 175)  # 80-255
            draw.line([(0, i), (size, i)], fill=(r, g, b, 255))
        
        # Add a rounded rectangle border
        border_radius = 60
        border_width = 8
        draw.rounded_rectangle(
            [border_width, border_width, size-border_width, size-border_width],
            radius=border_radius,
            outline=(255, 255, 255, 200),
            width=border_width
        )
        
        # Add "APEX" text in the center
        try:
            # Try to use a system font
            font_size = 120
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        text = "APEX"
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - 20  # Slightly above center
        
        # Draw text with shadow
        draw.text((x+3, y+3), text, fill=(0, 0, 0, 100), font=font)  # Shadow
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)  # Main text
        
        # Add a small subtitle
        try:
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        except:
            subtitle_font = ImageFont.load_default()
            
        subtitle = "Command Center"
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sub_width = bbox[2] - bbox[0]
        sub_x = (size - sub_width) // 2
        sub_y = y + text_height + 20
        
        draw.text((sub_x+1, sub_y+1), subtitle, fill=(0, 0, 0, 80), font=subtitle_font)  # Shadow
        draw.text((sub_x, sub_y), subtitle, fill=(200, 255, 255, 255), font=subtitle_font)  # Subtitle
        
        return img
    
    def create_icns_file():
        """Create an .icns file for macOS"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create the base icon
        icon_512 = create_apex_icon()
        
        # Create different sizes for the icns file
        sizes = [16, 32, 64, 128, 256, 512]
        temp_files = []
        
        for size in sizes:
            resized = icon_512.resize((size, size), Image.Resampling.LANCZOS)
            temp_file = f"/tmp/icon_{size}.png"
            resized.save(temp_file, "PNG")
            temp_files.append(temp_file)
        
        # Use macOS iconutil to create .icns
        iconset_dir = "/tmp/APEX.iconset"
        os.makedirs(iconset_dir, exist_ok=True)
        
        # Copy files with proper naming
        icon_mappings = {
            16: "icon_16x16.png",
            32: ["icon_16x16@2x.png", "icon_32x32.png"],
            64: "icon_32x32@2x.png", 
            128: ["icon_64x64@2x.png", "icon_128x128.png"],
            256: ["icon_128x128@2x.png", "icon_256x256.png"],
            512: ["icon_256x256@2x.png", "icon_512x512.png"]
        }
        
        for size in sizes:
            resized = icon_512.resize((size, size), Image.Resampling.LANCZOS)
            mappings = icon_mappings[size]
            if isinstance(mappings, str):
                mappings = [mappings]
            
            for mapping in mappings:
                resized.save(os.path.join(iconset_dir, mapping), "PNG")
        
        # Create the .icns file
        icns_path = os.path.join(base_dir, "icon.icns")
        os.system(f"iconutil -c icns {iconset_dir} -o {icns_path}")
        
        # Clean up
        os.system(f"rm -rf {iconset_dir}")
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        print(f"✅ Created icon: {icns_path}")
        return icns_path
    
    if __name__ == "__main__":
        create_icns_file()

except ImportError:
    print("⚠️  PIL (Pillow) not available, creating simple fallback")
    # Create a simple text-based icon as fallback
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icns_path = os.path.join(base_dir, "icon.icns")
    
    # Create a minimal PNG and convert it
    print("Creating minimal icon...")
    # This is a very basic approach - in production you'd want a proper icon
    os.system(f"echo 'APEX icon placeholder created at {icns_path}'")
    print(f"⚠️  Basic icon created: {icns_path}")