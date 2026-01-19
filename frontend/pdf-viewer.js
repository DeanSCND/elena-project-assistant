// PDF Viewer Module

const API_BASE = window.location.hostname === 'localhost'
    ? 'http://localhost:8100'
    : '';

class PDFViewer {
    constructor() {
        this.pdfDoc = null;
        this.pageNum = 1;
        this.pageRendering = false;
        this.pageNumPending = null;
        this.scale = 1.0;
        this.baseScale = 1.0; // Base scale for fitting page
        this.canvas = document.getElementById('pdf-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.currentPdfPath = null;
        this.isFullscreen = false;

        // Pan state
        this.isPanning = false;
        this.panX = 0;
        this.panY = 0;
        this.startX = 0;
        this.startY = 0;

        this.initializeControls();
    }

    initializeControls() {
        // Page navigation
        document.getElementById('pdf-prev-page').addEventListener('click', () => {
            if (this.pageNum <= 1) return;
            this.pageNum--;
            this.queueRenderPage(this.pageNum);
        });

        document.getElementById('pdf-next-page').addEventListener('click', () => {
            if (this.pageNum >= this.pdfDoc.numPages) return;
            this.pageNum++;
            this.queueRenderPage(this.pageNum);
        });

        // Zoom controls
        document.getElementById('pdf-zoom-in').addEventListener('click', () => {
            this.scale = Math.min(this.scale * 1.25, 3.0);
            this.queueRenderPage(this.pageNum);
        });

        document.getElementById('pdf-zoom-out').addEventListener('click', () => {
            this.scale = Math.max(this.scale / 1.25, 0.5);
            this.queueRenderPage(this.pageNum);
        });

        // Fullscreen button
        document.getElementById('pdf-fullscreen').addEventListener('click', () => {
            this.toggleFullscreen();
        });

        // Close button
        document.getElementById('pdf-close').addEventListener('click', () => {
            this.closePdfViewer();
        });

        // Close on modal background click
        document.getElementById('pdf-viewer-modal').addEventListener('click', (e) => {
            if (e.target.id === 'pdf-viewer-modal') {
                this.closePdfViewer();
            }
        });

        // Pan functionality
        this.initializePanControls();

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (!this.isOpen()) return;

            switch(e.key) {
                case 'ArrowLeft':
                    document.getElementById('pdf-prev-page').click();
                    break;
                case 'ArrowRight':
                    document.getElementById('pdf-next-page').click();
                    break;
                case 'Escape':
                    this.closePdfViewer();
                    break;
                case '+':
                case '=':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        document.getElementById('pdf-zoom-in').click();
                    }
                    break;
                case '-':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        document.getElementById('pdf-zoom-out').click();
                    }
                    break;
            }
        });
    }

    initializePanControls() {
        const container = document.querySelector('.pdf-canvas-container');

        container.addEventListener('mousedown', (e) => {
            if (e.button === 0 && this.scale > 1.0) { // Left click and zoomed in
                this.isPanning = true;
                this.startX = e.clientX - this.panX;
                this.startY = e.clientY - this.panY;
                this.canvas.classList.add('dragging');
                e.preventDefault();
            }
        });

        container.addEventListener('mousemove', (e) => {
            if (this.isPanning) {
                this.panX = e.clientX - this.startX;
                this.panY = e.clientY - this.startY;
                this.updateCanvasTransform();
                e.preventDefault();
            }
        });

        container.addEventListener('mouseup', () => {
            this.isPanning = false;
            this.canvas.classList.remove('dragging');
        });

        container.addEventListener('mouseleave', () => {
            this.isPanning = false;
            this.canvas.classList.remove('dragging');
        });

        // Mouse wheel zoom
        container.addEventListener('wheel', (e) => {
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                const delta = e.deltaY > 0 ? 0.9 : 1.1;
                const newScale = Math.min(Math.max(this.scale * delta, 0.5), 3.0);

                if (newScale !== this.scale) {
                    // Zoom towards mouse position
                    const rect = container.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;

                    const scaleRatio = newScale / this.scale;
                    this.panX = x - (x - this.panX) * scaleRatio;
                    this.panY = y - (y - this.panY) * scaleRatio;

                    this.scale = newScale;
                    this.queueRenderPage(this.pageNum);
                }
            }
        });
    }

    updateCanvasTransform() {
        this.canvas.style.transform = `translate(${this.panX}px, ${this.panY}px) scale(${this.scale})`;
    }

    toggleFullscreen() {
        const container = document.querySelector('.pdf-viewer-container');
        const btn = document.getElementById('pdf-fullscreen');

        this.isFullscreen = !this.isFullscreen;

        if (this.isFullscreen) {
            container.classList.add('fullscreen');
            btn.textContent = '⛶'; // Exit fullscreen icon
            btn.title = 'Exit Fullscreen';
        } else {
            container.classList.remove('fullscreen');
            btn.textContent = '⛶'; // Fullscreen icon
            btn.title = 'Fullscreen';
        }

        // Re-render to adjust to new size
        this.queueRenderPage(this.pageNum);
    }

    async openPdf(pdfPath, pageNumber = 1, section = '') {
        try {
            // Show modal and loading indicator
            const modal = document.getElementById('pdf-viewer-modal');
            modal.classList.remove('hidden');
            document.getElementById('pdf-loading').classList.remove('hidden');

            // Set title
            const filename = pdfPath.split('/').pop();
            document.getElementById('pdf-title').textContent = `📄 ${filename}`;

            // Set section info if available
            if (section) {
                document.getElementById('pdf-section-info').textContent = `Section: ${section}`;
            } else {
                document.getElementById('pdf-section-info').textContent = '';
            }

            // Construct PDF URL - properly encode the path to handle special characters
            const encodedPath = encodeURIComponent(pdfPath);
            const pdfUrl = `${API_BASE}/documents/${encodedPath}`;

            // Load PDF
            const loadingTask = pdfjsLib.getDocument(pdfUrl);
            this.pdfDoc = await loadingTask.promise;

            // Update page info
            document.getElementById('pdf-page-info').textContent =
                `Page ${pageNumber} of ${this.pdfDoc.numPages}`;

            // Store current PDF path
            this.currentPdfPath = pdfPath;

            // Set initial page
            this.pageNum = Math.min(pageNumber, this.pdfDoc.numPages);

            // Hide loading indicator
            document.getElementById('pdf-loading').classList.add('hidden');

            // Initial page rendering
            await this.renderPage(this.pageNum);

            // Update navigation buttons
            this.updateNavigationButtons();

        } catch (error) {
            console.error('Error opening PDF:', error);
            alert('Failed to open PDF document. Please try again.');
            this.closePdfViewer();
        }
    }

    async renderPage(num) {
        this.pageRendering = true;

        try {
            // Get page
            const page = await this.pdfDoc.getPage(num);

            // Calculate base scale to fit modal
            const modalBody = document.querySelector('.pdf-viewer-body');
            const maxWidth = modalBody.clientWidth - 40; // Padding
            const maxHeight = modalBody.clientHeight - 40;

            const viewport = page.getViewport({ scale: 1.0 });
            const widthScale = maxWidth / viewport.width;
            const heightScale = maxHeight / viewport.height;

            // Store base scale for fitting (removed 1.5 cap)
            this.baseScale = Math.min(widthScale, heightScale);

            // Account for device pixel ratio for high-DPI displays
            const pixelRatio = window.devicePixelRatio || 1;
            const renderScale = this.baseScale * pixelRatio * 2; // 2x for extra sharpness

            // Render at high resolution
            const renderViewport = page.getViewport({ scale: renderScale });

            // Set canvas buffer size to high resolution
            this.canvas.height = renderViewport.height;
            this.canvas.width = renderViewport.width;

            // Set canvas display size to base scale
            this.canvas.style.width = `${this.baseScale * viewport.width}px`;
            this.canvas.style.height = `${this.baseScale * viewport.height}px`;

            // Reset transform for rendering
            this.canvas.style.transform = '';

            // Render PDF page into canvas context at high resolution
            const renderContext = {
                canvasContext: this.ctx,
                viewport: renderViewport
            };

            const renderTask = page.render(renderContext);
            await renderTask.promise;

            // Apply zoom transform after rendering
            this.updateCanvasTransform();

            this.pageRendering = false;

            // Update page info
            document.getElementById('pdf-page-info').textContent =
                `Page ${num} of ${this.pdfDoc.numPages}`;

            // Update navigation buttons
            this.updateNavigationButtons();

            // If another page rendering was requested while rendering
            if (this.pageNumPending !== null) {
                await this.renderPage(this.pageNumPending);
                this.pageNumPending = null;
            }

        } catch (error) {
            console.error('Error rendering page:', error);
            this.pageRendering = false;
        }
    }

    queueRenderPage(num) {
        if (this.pageRendering) {
            this.pageNumPending = num;
        } else {
            this.renderPage(num);
        }
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('pdf-prev-page');
        const nextBtn = document.getElementById('pdf-next-page');

        prevBtn.disabled = this.pageNum <= 1;
        nextBtn.disabled = this.pageNum >= this.pdfDoc.numPages;
    }

    closePdfViewer() {
        const modal = document.getElementById('pdf-viewer-modal');
        modal.classList.add('hidden');

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Reset state
        this.pdfDoc = null;
        this.currentPdfPath = null;
        this.pageNum = 1;
        this.scale = 1.0;
        this.baseScale = 1.0;
        this.panX = 0;
        this.panY = 0;
        this.isPanning = false;

        // Reset canvas transform
        this.canvas.style.transform = '';

        // Exit fullscreen if active
        if (this.isFullscreen) {
            this.toggleFullscreen();
        }
    }

    isOpen() {
        return !document.getElementById('pdf-viewer-modal').classList.contains('hidden');
    }
}

// Initialize PDF viewer
const pdfViewer = new PDFViewer();

// Export for global access
window.pdfViewer = pdfViewer;
window.closePdfViewer = () => pdfViewer.closePdfViewer();