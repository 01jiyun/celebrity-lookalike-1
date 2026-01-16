from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os
import base64
import tempfile

app = Flask(__name__)

# 연예인 이미지 폴더 경로
CELEBRITY_FOLDER = os.path.join(os.path.dirname(__file__), 'celebrities')

# 얼굴 검출기 로드
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def get_face_encoding(image_path):
    """이미지에서 얼굴 특징 추출"""
    img = cv2.imread(image_path)
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        # 얼굴을 못 찾으면 전체 이미지 사용
        face_img = cv2.resize(gray, (100, 100))
    else:
        # 가장 큰 얼굴 선택
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face_img = gray[y:y+h, x:x+w]
        face_img = cv2.resize(face_img, (100, 100))

    # 히스토그램을 특징으로 사용
    hist = cv2.calcHist([face_img], [0], None, [256], [0, 256])
    hist = cv2.normalize(hist, hist).flatten()

    return hist

def compare_faces(hist1, hist2):
    """두 얼굴 히스토그램 비교 (상관계수 사용)"""
    correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    # 상관계수를 0~100% 범위로 변환
    similarity = (correlation + 1) / 2 * 100
    return similarity

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # 업로드된 이미지 받기
        data = request.json
        image_data = data['image'].split(',')[1]

        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(base64.b64decode(image_data))
            tmp_path = tmp.name

        # 사용자 얼굴 특징 추출
        user_encoding = get_face_encoding(tmp_path)

        if user_encoding is None:
            os.unlink(tmp_path)
            return jsonify({
                'success': False,
                'error': '얼굴을 찾을 수 없습니다.'
            })

        # 연예인 폴더의 모든 이미지와 비교
        results = []

        for filename in os.listdir(CELEBRITY_FOLDER):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                celeb_path = os.path.join(CELEBRITY_FOLDER, filename)
                celeb_name = os.path.splitext(filename)[0]

                celeb_encoding = get_face_encoding(celeb_path)

                if celeb_encoding is not None:
                    similarity = compare_faces(user_encoding, celeb_encoding)

                    results.append({
                        'name': celeb_name,
                        'similarity': round(similarity, 1),
                        'image': filename
                    })

        # 임시 파일 삭제
        os.unlink(tmp_path)

        # 유사도 높은 순으로 정렬
        results.sort(key=lambda x: x['similarity'], reverse=True)

        # 상위 3명 반환
        return jsonify({
            'success': True,
            'results': results[:3]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
