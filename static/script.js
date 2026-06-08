document.addEventListener('DOMContentLoaded', () => {
    const fetchBtn = document.getElementById('fetch-btn');
    const urlInput = document.getElementById('url-input');
    const loader = document.getElementById('loader');
    const errorMsg = document.getElementById('error-message');
    const resultsGrid = document.getElementById('results');
    const productInfo = document.getElementById('product-info');

    fetchBtn.addEventListener('click', () => {
        const url = urlInput.value.trim();
        if (!url) {
            showError('Please paste a link first!');
            return;
        }

        // Reset UI
        errorMsg.classList.add('hidden');
        productInfo.classList.add('hidden');
        resultsGrid.innerHTML = '';
        loader.classList.remove('hidden');

        // Auto-detect Instagram vs Product
        const isInstagram = url.includes('instagram.com');
        const endpoint = isInstagram ? '/api/fetch' : '/api/fetch_product';

        // Call backend API
        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        })
        .then(response => response.json())
        .then(data => {
            loader.classList.add('hidden');
            if (data.error) {
                showError('Error: ' + data.error);
            } else {
                if (data.is_product) {
                    renderProductInfo(data);
                }
                renderResults(data.media, data.shortcode || 'product');
            }
        })
        .catch(err => {
            loader.classList.add('hidden');
            showError('Failed to communicate with server.');
            console.error(err);
        });
    });

    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.classList.remove('hidden');
    }

    function renderProductInfo(data) {
        productInfo.innerHTML = `
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; line-height: 1.8; color: #111; font-weight: 700;">
                •브랜드 - ${data.brand}<br>
                •제품명 - ${data.title}<br>
                •가격 - ${data.price}<br>
                <br>
                출처: ${data.brand}
            </div>
            <div style="display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
                <button id="copy-info-btn" class="neo-btn" style="font-size: 1rem; padding: 0.5rem 1rem; background-color: #fff; color: #111;">정보 복사 (INFO)</button>
                <button id="copy-src-btn" class="neo-btn" style="font-size: 1rem; padding: 0.5rem 1rem; background-color: #fff; color: #111;">출처 복사 (SOURCE)</button>
            </div>
        `;
        productInfo.classList.remove('hidden');

        document.getElementById('copy-info-btn').addEventListener('click', (e) => {
            const textToCopy = `•브랜드 - ${data.brand}\n•제품명 - ${data.title}\n•가격 - ${data.price}`;
            navigator.clipboard.writeText(textToCopy).then(() => {
                e.target.textContent = 'COPIED!';
                setTimeout(() => { e.target.textContent = '정보 복사 (INFO)'; }, 2000);
            });
        });

        document.getElementById('copy-src-btn').addEventListener('click', (e) => {
            const textToCopy = `출처: ${data.brand}`;
            navigator.clipboard.writeText(textToCopy).then(() => {
                e.target.textContent = 'COPIED!';
                setTimeout(() => { e.target.textContent = '출처 복사 (SOURCE)'; }, 2000);
            });
        });
    }

    function renderResults(mediaArray, shortcode) {
        if (!mediaArray || mediaArray.length === 0) {
            showError("No media found!");
            return;
        }
        mediaArray.forEach((media, index) => {
            const card = document.createElement('div');
            card.className = 'media-card neo-box';

            const proxyUrl = `/api/preview?url=${encodeURIComponent(media.url)}`;

            let mediaPreview;
            if (media.type === 'video') {
                mediaPreview = `<video class="media-preview" src="${proxyUrl}" controls></video>`;
            } else {
                mediaPreview = `<img class="media-preview" src="${proxyUrl}" alt="Instagram Media">`;
            }

            const filename = `insta_${shortcode}_${index + 1}.${media.type === 'video' ? 'mp4' : 'jpg'}`;

            const cardContent = `
                ${mediaPreview}
                <div class="media-actions">
                    <button class="neo-btn download-btn" data-url="${media.url}" data-filename="${filename}">
                        DOWNLOAD
                    </button>
                </div>
            `;
            card.innerHTML = cardContent;
            resultsGrid.appendChild(card);
        });

        // Add download event listeners
        document.querySelectorAll('.download-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const url = e.target.getAttribute('data-url');
                const filename = e.target.getAttribute('data-filename');
                downloadMedia(url, filename, e.target);
            });
        });
    }

    function downloadMedia(url, filename, btnElement) {
        // Change button state
        const originalText = btnElement.textContent;
        btnElement.textContent = 'DOWNLOADING...';
        btnElement.style.opacity = '0.7';

        fetch('/api/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, filename: filename })
        })
        .then(response => {
            if (!response.ok) throw new Error('Download failed');
            return response.blob();
        })
        .then(blob => {
            // Create object URL and trigger download
            const blobUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = blobUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(blobUrl);
            document.body.removeChild(a);

            // Restore button state
            btnElement.textContent = 'DONE!';
            btnElement.style.backgroundColor = '#ffd000';
            setTimeout(() => {
                btnElement.textContent = 'DOWNLOAD';
                btnElement.style.backgroundColor = '';
                btnElement.style.opacity = '1';
            }, 2000);
        })
        .catch(err => {
            alert('Failed to download media.');
            console.error(err);
            btnElement.textContent = 'DOWNLOAD';
            btnElement.style.opacity = '1';
        });
    }
});
