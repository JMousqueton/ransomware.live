import json

# Charger le fichier JSON
with open('posts.json', 'r') as f:
    data = json.load(f)

# Parcourir chaque élément de la liste et mettre à jour l'attribut 'published' si il est vide
for item in data:
    if not item.get('published'):
        item['published'] = item.get('discovered', '')
    if not item.get('post_url'):
        item['post_url'] = ''

# Enregistrer les modifications dans le fichier JSON
with open('posts.json', 'w') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
