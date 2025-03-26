/**
 * Attendance marking utility
 */
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const videoElement = document.getElementById('webcam');
    const canvasElement = document.getElementById('canvas');
    const captureBtn = document.getElementById('captureBtn');
    const statusMessage = document.getElementById('statusMessage');
    const resultContainer = document.getElementById('resultContainer');
    const studentName = document.getElementById('studentName');
    const attendanceStatus = document.getElementById('attendanceStatus');
    const attendanceTime = document.getElementById('attendanceTime');
    const resetBtn = document.getElementById('resetBtn');
    
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
    
    // Start webcam when page loads
    if (webcam) {
        webcam.start()
            .then(() => {
                console.log('Webcam started successfully');
            })
            .catch(err => {
                console.error('Error starting webcam:', err);
                if (statusMessage) {
                    statusMessage.textContent = 'Error: Cannot access camera. Please ensure camera permissions are granted.';
                    statusMessage.classList.add('alert', 'alert-danger');
                    statusMessage.classList.remove('d-none');
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
            
            // Show processing state
            captureBtn.disabled = true;
            captureBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            
            if (statusMessage) {
                statusMessage.textContent = 'Processing face recognition...';
                statusMessage.classList.remove('d-none', 'alert-danger', 'alert-success');
                statusMessage.classList.add('alert', 'alert-info');
            }
            
            // Take picture
            const capturedImage = webcam.takePicture();
            
            if (capturedImage) {
                // Send image to API for face recognition
                fetch('/api/attendance/mark', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        image_data: capturedImage
                    })
                })
                .then(response => response.json())
                .then(result => {
                    // Display result
                    if (result.success) {
                        // Successful face recognition
                        if (statusMessage) {
                            statusMessage.textContent = 'Face recognized successfully!';
                            statusMessage.classList.remove('alert-info', 'alert-danger');
                            statusMessage.classList.add('alert-success');
                        }
                        
                        // Show result details
                        if (resultContainer) resultContainer.classList.remove('d-none');
                        if (studentName) studentName.textContent = result.name;
                        if (attendanceStatus) attendanceStatus.textContent = result.message;
                        if (attendanceTime) {
                            const now = new Date();
                            attendanceTime.textContent = now.toLocaleTimeString();
                        }
                        
                        // Temporarily stop webcam
                        webcam.stop();
                    } else {
                        // Failed face recognition
                        if (statusMessage) {
                            statusMessage.textContent = 'Error: ' + result.message;
                            statusMessage.classList.remove('alert-info', 'alert-success');
                            statusMessage.classList.add('alert-danger');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    if (statusMessage) {
                        statusMessage.textContent = 'Error: ' + (error.message || 'Unknown error occurred');
                        statusMessage.classList.remove('alert-info', 'alert-success');
                        statusMessage.classList.add('alert-danger');
                    }
                })
                .finally(() => {
                    // Reset button state
                    captureBtn.disabled = false;
                    captureBtn.textContent = 'Capture Face';
                });
            } else {
                alert('Failed to capture image. Please try again.');
                captureBtn.disabled = false;
                captureBtn.textContent = 'Capture Face';
            }
        });
    }
    
    // Reset button click
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            // Hide result container
            if (resultContainer) resultContainer.classList.add('d-none');
            
            // Hide status message
            if (statusMessage) statusMessage.classList.add('d-none');
            
            // Restart webcam
            if (webcam) {
                webcam.start().catch(err => {
                    console.error('Error restarting webcam:', err);
                });
            }
        });
    }
    
    // Load attendance logs if we're on the attendance log page
    const attendanceTable = document.getElementById('attendanceTable');
    const dateFilter = document.getElementById('dateFilter');
    
    if (attendanceTable && dateFilter) {
        // Set default date to today
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        dateFilter.value = `${year}-${month}-${day}`;
        
        // Load initial attendance data
        loadAttendanceData(dateFilter.value);
        
        // Set up date filter change handler
        dateFilter.addEventListener('change', function() {
            loadAttendanceData(this.value);
        });
    }
    
    // Function to load attendance data
    function loadAttendanceData(date) {
        const tableBody = attendanceTable.querySelector('tbody');
        
        // Show loading state
        tableBody.innerHTML = '<tr><td colspan="6" class="text-center">Loading...</td></tr>';
        
        // Fetch attendance data from API
        fetch(`/api/attendance/report/daily?date=${date}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load attendance data');
                }
                return response.json();
            })
            .then(data => {
                // Clear loading state
                tableBody.innerHTML = '';
                
                if (data.length === 0) {
                    tableBody.innerHTML = '<tr><td colspan="6" class="text-center">No attendance records found for this date</td></tr>';
                    return;
                }
                
                // Populate table
                data.forEach((record, index) => {
                    const row = document.createElement('tr');
                    
                    // Format time
                    const checkInTime = record.check_in ? new Date(record.check_in).toLocaleTimeString() : 'N/A';
                    const checkOutTime = record.check_out ? new Date(record.check_out).toLocaleTimeString() : 'N/A';
                    
                    // Set row class based on status
                    if (record.status === 'absent') {
                        row.classList.add('table-danger');
                    } else if (record.status === 'late') {
                        row.classList.add('table-warning');
                    } else {
                        row.classList.add('table-success');
                    }
                    
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${record.name}</td>
                        <td>${record.student_id}</td>
                        <td>${record.status}</td>
                        <td>${checkInTime}</td>
                        <td>${checkOutTime}</td>
                    `;
                    
                    tableBody.appendChild(row);
                });
            })
            .catch(error => {
                console.error('Error:', error);
                tableBody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Error: ${error.message}</td></tr>`;
            });
    }
    
    // Clean up on page unload
    window.addEventListener('beforeunload', function() {
        if (webcam) {
            webcam.stop();
        }
    });
});
