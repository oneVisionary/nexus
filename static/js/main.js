document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const videoInput = document.getElementById('videoInput');
    const uploadArea = document.getElementById('uploadArea');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            console.log('Login attempt:', { email, password });
            alert('Login functionality will be implemented with backend');
            window.location.href = 'dashboard.html';
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const fullname = document.getElementById('fullname').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }

            console.log('Register attempt:', { fullname, email, password });
            alert('Registration functionality will be implemented with backend');
            window.location.href = 'login.html';
        });
    }

    if (videoInput) {
        videoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                handleVideoUpload(file);
            }
        });
    }

    if (uploadArea) {
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.style.borderColor = 'var(--primary-blue)';
            uploadArea.style.backgroundColor = 'var(--pale-blue)';
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.style.borderColor = 'var(--border-color)';
            uploadArea.style.backgroundColor = 'var(--white)';
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.style.borderColor = 'var(--border-color)';
            uploadArea.style.backgroundColor = 'var(--white)';

            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('video/')) {
                handleVideoUpload(file);
            } else {
                alert('Please upload a valid video file');
            }
        });
    }

    function handleVideoUpload(file) {
        console.log('Uploading file:', file.name);

        uploadArea.classList.add('hidden');
        uploadProgress.classList.remove('hidden');

        let progress = 0;
        const interval = setInterval(function() {
            progress += 10;
            progressFill.style.width = progress + '%';
            progressText.textContent = 'Uploading: ' + progress + '%';

            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(function() {
                    uploadProgress.classList.add('hidden');
                    uploadArea.classList.remove('hidden');
                    progressFill.style.width = '0%';
                    alert('Video uploaded successfully! (This is a UI demo)');
                }, 500);
            }
        }, 300);
    }

    const smoothScroll = document.querySelectorAll('a[href^="#"]');
    smoothScroll.forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
});
