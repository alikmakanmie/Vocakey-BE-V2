"""Auto-fix duplicate and wrong routes in app.py"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Step 1: Find and remove serve_audio function (around line 818)
new_lines = []
skip_serve_audio = False
i = 0

while i < len(lines):
    line = lines[i]
    
    # Detect start of serve_audio with wrong routes
    if '@app.route(\'/api/songs/search/<string:title>/transpose\'' in line:
        # Check if next lines also have routes and then serve_audio
        if (i+3 < len(lines) and 
            'def serve_audio' in lines[i+3]):
            # Skip this entire function
            skip_serve_audio = True
            i += 1
            continue
    
    if skip_serve_audio:
        # Skip until we find next @app.route or def at root level
        if (line.strip().startswith('@app.route') or 
            (line.strip().startswith('def ') and not line.startswith(' '))):
            skip_serve_audio = False
        else:
            i += 1
            continue
    
    # Step 2: Remove orphaned decorator before transpose_song_by_title
    if "        @app.route('/songs/transposed/<filename>')" in line:
        # Skip this line (it's indented wrong and orphaned)
        i += 1
        continue
    
    new_lines.append(line)
    i += 1

# Write fixed file
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Fixed app.py!")
print(f"   Original: {len(lines)} lines")
print(f"   Fixed: {len(new_lines)} lines")
print(f"   Removed: {len(lines) - len(new_lines)} lines")
