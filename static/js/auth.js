// 认证相关JavaScript

// 登录表单处理
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showMessage('登录成功，正在跳转...', 'success');
                setTimeout(() => window.location.href = '/diary/', 1000);
            } else {
                showMessage(data.message, 'error');
            }
        } catch (error) {
            showMessage('网络错误，请稍后重试', 'error');
        }
    });
}

// 注册表单处理
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        
        if (password !== confirmPassword) {
            showMessage('两次输入的密码不一致', 'error');
            return;
        }
        
        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showMessage('注册成功，正在跳转到登录页...', 'success');
                setTimeout(() => window.location.href = '/auth/login', 1500);
            } else {
                showMessage(data.message, 'error');
            }
        } catch (error) {
            showMessage('网络错误，请稍后重试', 'error');
        }
    });
}

// 忘记密码表单处理
const forgotForm = document.getElementById('forgotForm');
if (forgotForm) {
    forgotForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        
        try {
            const response = await fetch('/auth/forgot-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showMessage('已提交申请，请联系管理员重置密码', 'success');
            } else {
                showMessage(data.message, 'error');
            }
        } catch (error) {
            showMessage('网络错误，请稍后重试', 'error');
        }
    });
}

// 显示消息函数
function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.textContent = text;
        messageDiv.className = `message ${type}`;
        
        // 3秒后自动隐藏
        setTimeout(() => {
            messageDiv.className = 'message';
        }, 3000);
    }
}