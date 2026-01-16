from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os
import base64
import tempfile
import gc

app = Flask(__name__)

# 연예인 이미지 폴더 경로
CELEBRITY_FOLDER = os.path.join(os.path.dirname(__file__), 'celebrities')

# 얼굴 검출기 로드
face_cascade = None
try:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
except:
    pass

def get_face_histogram(image_path):
    """이미지에서 얼굴 히스토그램 추출 (메모리 최적화)"""
    try:
        # 작은 크기로 이미지 로드
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None

        # 이미지 크기 제한 (메모리 절약)
        max_size = 300
        h, w = img.shape[:2]
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale)

        # 얼굴 영역으로 크롭 (가능하면)
        if face_cascade is not None:
            faces = face_cascade.detectMultiScale(img, 1.1, 4)
            if len(faces) > 0:
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                img = img[y:y+h, x:x+w]

        # 고정 크기로 리사이즈
        img = cv2.resize(img, (64, 64))

        # 히스토그램 계산
        hist = cv2.calcHist([img], [0], None, [32], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()

        return hist
    except:
        return None

def compare_histograms(hist1, hist2):
    """히스토그램 비교"""
    correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return (correlation + 1) / 2 * 100

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    celeb_count = 0
    try:
        celeb_count = len([f for f in os.listdir(CELEBRITY_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    except:
        pass
    return jsonify({'status': 'ok', 'celebrities': celeb_count})

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
        user_hist = get_face_histogram(tmp_path)

        if user_hist is None:
            return jsonify({'success': False, 'error': '얼굴을 찾을 수 없습니다.'})

        # 연예인과 비교 (하나씩 처리해서 메모리 절약)
        results = []

        for filename in os.listdir(CELEBRITY_FOLDER):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                celeb_path = os.path.join(CELEBRITY_FOLDER, filename)
                celeb_name = os.path.splitext(filename)[0]

                celeb_hist = get_face_histogram(celeb_path)

                if celeb_hist is not None:
                    similarity = compare_histograms(user_hist, celeb_hist)
                    results.append({
                        'name': celeb_name,
                        'similarity': round(similarity, 1)
                    })

                # 메모리 정리
                del celeb_hist
                gc.collect()

        # 정렬 및 상위 3명
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
        gc.collect()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
