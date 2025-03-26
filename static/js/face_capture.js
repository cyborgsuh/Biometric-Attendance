/**
 * Face capture utility for student registration
 */
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const videoElement = document.getElementById('webcam');
    const canvasElement = document.getElementById('canvas');
    const captureBtn = document.getElementById('captureBtn');
    const registerBtn = document.getElementById('registerBtn');
    const retakeBtn = document.getElementById('retakeBtn');
    const previewImg = document.getElementById('previewImg');
    const captureContainer = document.getElementById('captureContainer');
    const previewContainer = document.getElementById('previewContainer');
    const statusMessage = document.getElementById('statusMessage');
    const studentForm = document.getElementById('studentForm');
    
    // Initialize webcam
    let webcam = null;
    
    if (videoElement && canvasElement) {
        webcam = new Webcam(videoElement, canvasElement, {
            width: 640,
            height: 480,
            facingMode: 'user',
            imageFormat: 'image/jpeg',
            imageQuality: 0.9
        });
    }
    
    let capturedImage = null;
    
    // Start webcam when page loads
    if (webcam) {
        webcam.start()
            .then(() => {
                console.log('Webcam started successfully');
                if (captureContainer) {
                    captureContainer.classList.remove('d-none');
                }
            })
            .catch(err => {
                console.error('Error starting webcam:', err);
                if (statusMessage) {
                    statusMessage.textContent = 'Error: Cannot access camera. Please ensure camera permissions are granted.';
                    statusMessage.classList.add('alert', 'alert-danger');
                }
            });
    }
    
    // Capture button click
    if (captureBtn) {
        captureBtn.addEventListener('click', function() {
            if (!webcam || !webcam.isStreaming) {
                alert('Webcam is not available. Please refresh the page and allow camera access.');
                return;
            }
            
            // Take picture
            capturedImage = webcam.takePicture();
            
            if (capturedImage) {
                // Show preview
                if (previewImg) {
                    previewImg.src = capturedImage;
                    if (captureContainer) captureContainer.classList.add('d-none');
                    if (previewContainer) previewContainer.classList.remove('d-none');
                }
                
                // Temporarily stop webcam to save resources
                webcam.stop();
            } else {
                alert('Failed to capture image. Please try again.');
            }
        });
    }
    
    // Retake button click
    if (retakeBtn) {
        retakeBtn.addEventListener('click', function() {
            // Clear captured image
            capturedImage = null;
            
            // Restart webcam
            if (webcam) {
                webcam.start()
                    .then(() => {
                        if (captureContainer) captureContainer.classList.remove('d-none');
                        if (previewContainer) previewContainer.classList.add('d-none');
                    })
                    .catch(err => {
                        console.error('Error restarting webcam:', err);
                        if (statusMessage) {
                            statusMessage.textContent = 'Error: Cannot restart camera.';
                            statusMessage.classList.add('alert', 'alert-danger');
                        }
                    });
            }
        });
    }
    
    // Form submission
    if (studentForm) {
        studentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate form
            const studentId = document.getElementById('studentId').value;
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            
            if (!studentId || !name || !email) {
                alert('Please fill in all fields.');
                return;
            }
            
            if (!capturedImage) {
                alert('Please capture a face image before registering.');
                return;
            }
            
            // First, create student record
            const studentData = {
                student_id: studentId,
                name: name,
                email: email
            };
            
            // Show loading state
            if (registerBtn) {
                registerBtn.disabled = true;
                registerBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registering...';
            }
            
            // Send student data to API
            fetch('/api/students/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(studentData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error creating student record');
                }
                return response.json();
            })
            .then(student => {
                // Now register face for the student
                const faceData = {
                    image_data: capturedImage
                };
                
                // Create form data for the face registration
                const formData = new FormData();
                formData.append('student_id', student.id);
                
                // Send face data to API
                return fetch('/api/students/register-face', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        image_data: capturedImage,
                        student_id: student.id
                    })
                });
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error registering face');
                }
                return response.json();
            })
            .then(result => {
                if (result.success) {
                    // Show success message
                    if (statusMessage) {
                        statusMessage.textContent = 'Student registered successfully!';
                        statusMessage.classList.remove('alert-danger');
                        statusMessage.classList.add('alert', 'alert-success');
                    }
                    
                    // Reset form
                    studentForm.reset();
                    if (previewContainer) previewContainer.classList.add('d-none');
                    
                    // Restart webcam
                    if (webcam) {
                        webcam.start().then(() => {
                            if (captureContainer) captureContainer.classList.remove('d-none');
                        });
                    }
                } else {
                    throw new Error(result.message || 'Failed to register face');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (statusMessage) {
                    statusMessage.textContent = 'Error: ' + error.message;
                    statusMessage.classList.remove('alert-success');
                    statusMessage.classList.add('alert', 'alert-danger');
                }
            })
            .finally(() => {
                // Reset button state
                if (registerBtn) {
                    registerBtn.disabled = false;
                    registerBtn.textContent = 'Register Student';
                }
            });
        });
    }
    
    // Clean up on page unload
    window.addEventListener('beforeunload', function() {
        if (webcam) {
            webcam.stop();
        }
    });
});
