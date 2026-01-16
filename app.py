from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os
import base64
import tempfile
import json

app = Flask(__name__)

# 미리 계산된 연예인 데이터 로드
DATA_FILE = os.path.join(os.path.dirname(__file__), 'celebrity_data.json')
CELEBRITY_DATA = {}

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        CELEBRITY_DATA = json.load(f)
    # 리스트를 numpy 배열로 변환
    for name in CELEBRITY_DATA:
        CELEBRITY_DATA[name] = np.array(CELEBRITY_DATA[name], dtype=np.float32)
except Exception as e:
    print(f"데이터 로드 실패: {e}")

# 얼굴 검출기
face_cascade = None
try:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
except:
    pass

def get_user_histogram(image_path):
    """사용자 이미지에서 히스토그램 추출"""
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None

        # 크기 제한
        max_size = 300
        h, w = img.shape[:2]
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale)

        # 얼굴 검출
        if face_cascade is not None:
            faces = face_cascade.detectMultiScale(img, 1.1, 4)
            if len(faces) > 0:
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                img = img[y:y+h, x:x+w]

        img = cv2.resize(img, (64, 64))
        hist = cv2.calcHist([img], [0], None, [32], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()

        return hist
    except:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'celebrities': len(CELEBRITY_DATA)
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    tmp_path = None
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': '이미지가 없습니다.'})

        # 이미지 디코딩
        image_data = data['image'].split(',')[1]

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(base64.b64decode(image_data))
            tmp_path = tmp.name

        # 사용자 히스토그램
        user_hist = get_user_histogram(tmp_path)

        if user_hist is None:
            return jsonify({'success': False, 'error': '얼굴을 찾을 수 없습니다.'})

        # 미리 계산된 데이터와 비교 (매우 빠름!)
        results = []
        for name, celeb_hist in CELEBRITY_DATA.items():
            correlation = cv2.compareHist(user_hist, celeb_hist, cv2.HISTCMP_CORREL)
            similarity = (correlation + 1) / 2 * 100
            results.append({
                'name': name,
                'similarity': round(similarity, 1)
            })

        # 정렬
        results.sort(key=lambda x: x['similarity'], reverse=True)

        return jsonify({
            'success': True,
            'results': results[:3]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
