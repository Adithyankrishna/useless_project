document.addEventListener('DOMContentLoaded', function() {
    const codeInput = document.getElementById('code-input');
    const chaosLevelSlider = document.getElementById('chaos-level');
    const chaosValueSpan = document.getElementById('chaos-value');
    const injectBtn = document.getElementById('inject-btn');
    const fileUpload = document.getElementById('file-upload');
    const outputSection = document.getElementById('output-section');
    const loading = document.getElementById('loading');
    const errorDisplay = document.getElementById('error-display');
    const copyBtn = document.getElementById('copy-btn');

    // Update chaos level display
    chaosLevelSlider.addEventListener('input', function() {
        chaosValueSpan.textContent = this.value;
        
        // Change emoji based on chaos level
        const level = parseInt(this.value);
        let emoji = '😇';
        if (level >= 4 && level <= 7) emoji = '😈';
        if (level >= 8) emoji = '🔥';
        
        chaosValueSpan.innerHTML = `${this.value} ${emoji}`;
    });

    // File upload handler
    fileUpload.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        loading.style.display = 'flex';
        hideError();

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loading.style.display = 'none';
            
            if (data.success) {
                codeInput.value = data.code;
                codeInput.classList.add('pulse');
                setTimeout(() => codeInput.classList.remove('pulse'), 500);
                
                showSuccess(`📁 Loaded ${data.filename}`);
            } else {
                showError(data.error);
            }
        })
        .catch(error => {
            loading.style.display = 'none';
            showError('Failed to upload file');
            console.error('Upload error:', error);
        });
    });

    // Main inject bugs button
    injectBtn.addEventListener('click', function() {
        const code = codeInput.value.trim();
        
        if (!code) {
            showError('Please enter some Python code first! 🐍');
            return;
        }

        const chaosLevel = parseInt(chaosLevelSlider.value);
        
        // Show loading
        loading.style.display = 'flex';
        hideError();
        injectBtn.disabled = true;

        // Send request to backend
        fetch('/inject-bugs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code,
                chaos_level: chaosLevel
            })
        })
        .then(response => response.json())
        .then(data => {
            loading.style.display = 'none';
            injectBtn.disabled = false;

            if (data.success) {
                displayResults(data);
            } else {
                showError(data.error);
            }
        })
        .catch(error => {
            loading.style.display = 'none';
            injectBtn.disabled = false;
            showError('Something went wrong! Please try again. 💥');
            console.error('Error:', error);
        });
    });

    // Copy code functionality
    copyBtn.addEventListener('click', function() {
        const buggyCode = document.getElementById('buggy-code').textContent;
        navigator.clipboard.writeText(buggyCode).then(() => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = '✅ Copied!';
            copyBtn.style.background = '#4CAF50';
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.background = '#4CAF50';
            }, 2000);
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = buggyCode;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            copyBtn.textContent = '✅ Copied!';
            setTimeout(() => copyBtn.textContent = '📋 Copy', 2000);
        });
    });

    function displayResults(data) {
        // Show the output section
        outputSection.style.display = 'block';
        outputSection.classList.add('fade-in');
        
        // Update the info badges
        document.getElementById('bug-count').textContent = `${data.bug_count} bugs injected 🐛`;
        document.getElementById('chaos-info').textContent = `Chaos Level ${data.chaos_level}/10`;
        
        // Display the buggy code with syntax highlighting
        const buggyCodeElement = document.getElementById('buggy-code');
        buggyCodeElement.textContent = data.buggy_code;
        
        // Re-highlight the code
        if (typeof Prism !== 'undefined') {
            Prism.highlightElement(buggyCodeElement);
        }
        
        // Display the bug list
        const bugList = document.getElementById('bug-list');
        bugList.innerHTML = '';
        
        if (data.bugs_injected.length === 0) {
            bugList.innerHTML = '<li style="color: #666;">🍀 No bugs were injected this time! Try increasing the chaos level.</li>';
        } else {
            data.bugs_injected.forEach((bug, index) => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${index + 1}.</strong> ${bug}`;
                bugList.appendChild(li);
            });
        }
        
        // Scroll to results
        outputSection.scrollIntoView({ behavior: 'smooth' });
    }

    function showError(message) {
        errorDisplay.style.display = 'block';
        document.getElementById('error-message').textContent = message;
        errorDisplay.scrollIntoView({ behavior: 'smooth' });
    }

    function hideError() {
        errorDisplay.style.display = 'none';
    }

    function showSuccess(message) {
        // Simple success notification (you can enhance this)
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Add some example code on first load
    if (!codeInput.value.trim()) {
        codeInput.value = `# Simple odd/even checker
number = int(input("Enter a number: "))

if number % 2 == 0:
    print(f"{number} is even")
else:
    print(f"{number} is odd")`;
    }
});
