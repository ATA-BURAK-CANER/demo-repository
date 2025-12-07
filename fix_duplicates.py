with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# İki adet @app.route('/') def index(): bloğunu bul
route_indices = []
for i, line in enumerate(lines):
    if "@app.route('/')" in line:
        route_indices.append(i)

print(f"Found @app.route('/') at lines: {[i+1 for i in route_indices]}")

if len(route_indices) >= 2:
    # İlk bloğu sil (route_indices[0]'dan route_indices[1]'e kadar)
    start = route_indices[0]
    end = route_indices[1]
    
    print(f"Removing lines {start+1} to {end}")
    
    # Yeni içerik: başlangıç + ikinci route sonrası
    new_lines = lines[:start] + lines[end:]
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Fixed! Duplicate block removed.")
else:
    print("No duplicate found.")
