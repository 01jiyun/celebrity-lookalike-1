const uploadBox = document.getElementById('uploadBox');
const imageInput = document.getElementById('imageInput');
const preview = document.getElementById('preview');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const resultCards = document.getElementById('resultCards');

let uploadedImage = null;

// 클릭으로 파일 선택
uploadBox.addEventListener('click', () => {
    imageInput.click();
});

// 드래그 앤 드롭
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#667eea';
    uploadBox.style.background = '#f8f9ff';
});

uploadBox.addEventListener('dragleave', () => {
    if (!uploadedImage) {
        uploadBox.style.borderColor = '#ddd';
        uploadBox.style.background = 'white';
    }
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handleImage(file);
    }
});

// 파일 선택 시
imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleImage(file);
    }
});

// 이미지 처리
function handleImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        uploadedImage = e.target.result;
        preview.src = uploadedImage;
        preview.hidden = false;
        uploadBox.querySelector('.upload-content').hidden = true;
        uploadBox.classList.add('has-image');
        analyzeBtn.disabled = false;
        results.hidden = true;
    };
    reader.readAsDataURL(file);
}

// 분석 버튼 클릭
analyzeBtn.addEventListener('click', async () => {
    if (!uploadedImage) return;

    // UI 상태 변경
    analyzeBtn.disabled = true;
    loading.hidden = false;
    results.hidden = true;

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: uploadedImage }),
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data.results);
        } else {
            showError(data.error || '분석 중 오류가 발생했습니다.');
        }
    } catch (error) {
        showError('서버 연결에 실패했습니다.');
    } finally {
        loading.hidden = true;
        analyzeBtn.disabled = false;
    }
});

// 결과 표시
function displayResults(resultData) {
    resultCards.innerHTML = '';

    if (resultData.length === 0) {
        showError('얼굴을 찾을 수 없습니다. 다른 사진을 시도해보세요.');
        return;
    }

    resultData.forEach((result, index) => {
        const card = document.createElement('div');
        card.className = 'result-card';
        card.innerHTML = `
            <div class="result-rank">${index + 1}</div>
            <div class="result-info">
                <div class="result-name">${result.name}</div>
            </div>
            <div class="result-similarity">${result.similarity}%</div>
        `;
        resultCards.appendChild(card);
    });

    results.hidden = false;
}

// 에러 표시
function showError(message) {
    resultCards.innerHTML = `<div class="error-message">${message}</div>`;
    results.hidden = false;
}
