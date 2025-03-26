/**
 * Webcam utility class for face capture and recognition
 */
class Webcam {
    constructor(videoElement, canvasElement, options = {}) {
        this.video = videoElement;
        this.canvas = canvasElement;
        this.context = this.canvas ? this.canvas.getContext('2d') : null;
        this.stream = null;
        this.options = {
            width: options.width || 640,
            height: options.height || 480,
            facingMode: options.facingMode || 'user', // 'user' for front camera, 'environment' for back camera
            imageFormat: options.imageFormat || 'image/jpeg',
            imageQuality: options.imageQuality || 0.92
        };
        this.isStreaming = false;
        
        // Bind methods
        this.start = this.start.bind(this);
        this.stop = this.stop.bind(this);
        this.takePicture = this.takePicture.bind(this);
        this.dataURItoBlob = this.dataURItoBlob.bind(this);
    }
    
    /**
     * Start the webcam stream
     * @returns {Promise} - Resolves when the stream is started, rejects on error
     */
    start() {
        return new Promise((resolve, reject) => {
            // Check if getUserMedia is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                return reject(new Error('getUserMedia is not supported by this browser'));
            }
            
            // Stop any existing stream
            if (this.stream) {
                this.stop();
            }
            
            // Set up constraints
            const constraints = {
                video: {
                    width: { ideal: this.options.width },
                    height: { ideal: this.options.height },
                    facingMode: this.options.facingMode
                },
                audio: false
            };
            
            // Request camera access
            navigator.mediaDevices.getUserMedia(constraints)
                .then((stream) => {
                    this.stream = stream;
                    this.video.srcObject = stream;
                    
                    // Wait for video to start playing
                    this.video.onloadedmetadata = () => {
                        this.video.play();
                        this.isStreaming = true;
                        resolve();
                    };
                })
                .catch((err) => {
                    console.error('Error starting webcam:', err);
                    reject(err);
                });
        });
    }
    
    /**
     * Stop the webcam stream
     */
    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
            this.isStreaming = false;
            this.video.srcObject = null;
        }
    }
    
    /**
     * Take a picture from the webcam
     * @returns {string} - Base64 encoded image data URI
     */
    takePicture() {
        if (!this.isStreaming) {
            console.error('Webcam is not streaming');
            return null;
        }
        
        // Set canvas dimensions to match video
        const width = this.video.videoWidth;
        const height = this.video.videoHeight;
        
        if (width && height) {
            this.canvas.width = width;
            this.canvas.height = height;
            
            // Draw video frame to canvas
            this.context.drawImage(this.video, 0, 0, width, height);
            
            // Get image data URL
            const dataUri = this.canvas.toDataURL(this.options.imageFormat, this.options.imageQuality);
            return dataUri;
        }
        
        return null;
    }
    
    /**
     * Convert a data URI to a Blob object
     * @param {string} dataURI - Base64 encoded image data URI
     * @returns {Blob} - Blob object containing the image data
     */
    dataURItoBlob(dataURI) {
        // Split the data URI to get the base64 data
        const byteString = atob(dataURI.split(',')[1]);
        
        // Get MIME type
        const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
        
        // Create an array buffer
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        
        // Set the bytes of the array buffer
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        
        // Create a blob and return it
        return new Blob([ab], { type: mimeString });
    }
}
