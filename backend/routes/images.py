from flask import Blueprint, request, jsonify
import os

images_bp = Blueprint('images', __name__)

FALLBACK_IMAGES = {
    'spinach': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400',
    'kale': 'https://images.unsplash.com/photo-1524179091875-bf99a9a6af57?w=400',
    'carrot': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400',
    'broccoli': 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=400',
    'tomato': 'https://images.unsplash.com/photo-1546094096-0df4bcabd337?w=400',
    'potato': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400',
    'onion': 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400',
    'garlic': 'https://images.unsplash.com/photo-1471943038886-2e8393ea0b9b?w=400',
    'cucumber': 'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400',
    'corn': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400',
    'default': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400',
}

@images_bp.route('/search', methods=['GET'])
def search_image():
    query = request.args.get('q', 'vegetable').lower()
    for key, url in FALLBACK_IMAGES.items():
        if key in query:
            return jsonify({'url': url, 'source': 'fallback'})
    return jsonify({'url': FALLBACK_IMAGES['default'], 'source': 'fallback'})

@images_bp.route('/bulk', methods=['POST'])
def bulk_images():
    names = request.json.get('names', [])
    result = {}
    for name in names:
        found = False
        for key, url in FALLBACK_IMAGES.items():
            if key in name.lower():
                result[name] = url
                found = True
                break
        if not found:
            result[name] = FALLBACK_IMAGES['default']
    return jsonify(result)