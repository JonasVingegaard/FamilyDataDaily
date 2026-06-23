// 管理员后台JavaScript

// ============================================
// 页面初始化
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    // 侧边栏导航
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', function() {
            switchPage(this.dataset.page);
        });
    });

    // 返回日记按钮
    document.getElementById('backToDiary').addEventListener('click', function() {
        window.location.href = '/diary/';
    });

    // 加载用户列表
    loadUsers();
});

// ============================================
// 页面切换
// ============================================
function switchPage(pageId) {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    
    document.querySelector(`[data-page="${pageId}"]`).classList.add('active');
    document.getElementById(pageId).classList.add('active');
    
    // 加载对应内容
    if (pageId === 'admin-users') {
        loadUsers();
    } else if (pageId === 'admin-diaries') {
        loadAllDiaries();
    } else if (pageId === 'admin-files') {
        loadFiles();
    }
}

// ============================================
// 用户管理
// ============================================
async function loadUsers() {
    try {
        const response = await fetch('/admin/users');
        const data = await response.json();
        
        if (data.success) {
            displayUsers(data.users);
        }
    } catch (error) {
        console.error('加载用户失败:', error);
    }
}

function displayUsers(users) {
    const tbody = document.getElementById('usersTableBody');
    
    if (!users || users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#999;padding:40px;">暂无用户</td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.id}</td>
            <td><strong>${escapeHtml(user.username)}</strong></td>
            <td>${escapeHtml(user.email)}</td>
            <td><span class="badge ${user.is_admin ? 'badge-admin' : 'badge-user'}">${user.is_admin ? '管理员' : '普通用户'}</span></td>
            <td>${user.created_at}</td>
            <td>
                ${!user.is_admin ? `
                    <button class="action-btn btn-warning" onclick="showResetPassword(${user.id}, '${escapeHtml(user.username)}')">重置密码</button>
                    <button class="action-btn btn-danger" onclick="deleteUser(${user.id}, '${escapeHtml(user.username)}')">删除</button>
                ` : '<span style="color:#999;">-</span>'}
            </td>
        </tr>
    `).join('');
}

function showResetPassword(userId, username) {
    document.getElementById('resetUsername').textContent = username;
    document.getElementById('newPassword').value = '';
    document.getElementById('resetPasswordModal').classList.add('active');
    document.getElementById('resetPasswordModal').dataset.userId = userId;
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

async function confirmResetPassword() {
    const userId = document.getElementById('resetPasswordModal').dataset.userId;
    const newPassword = document.getElementById('newPassword').value;
    
    if (!newPassword) {
        alert('请输入新密码');
        return;
    }
    
    try {
        const response = await fetch(`/admin/users/${userId}/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: newPassword })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ 密码已重置为: ${newPassword}`);
            closeModal('resetPasswordModal');
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        alert('❌ 网络错误');
    }
}

async function deleteUser(userId, username) {
    if (!confirm(`确定要删除用户 "${username}" 吗？\n该用户的所有日记也会被删除！`)) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/users/${userId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ 用户 "${username}" 已删除`);
            loadUsers();
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        alert('❌ 网络错误');
    }
}

// ============================================
// 日记管理
// ============================================
async function loadAllDiaries() {
    try {
        const response = await fetch('/admin/diaries');
        const data = await response.json();
        
        if (data.success) {
            displayDiaries(data.diaries);
        }
    } catch (error) {
        console.error('加载日记失败:', error);
    }
}

function displayDiaries(diaries) {
    const tbody = document.getElementById('diariesTableBody');
    
    if (!diaries || diaries.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#999;padding:40px;">暂无日记</td></tr>';
        return;
    }
    
    tbody.innerHTML = diaries.map(diary => {
        const fileCount = (diary.images?.length || 0) + (diary.videos?.length || 0) + (diary.files?.length || 0);
        const contentSummary = diary.content ? diary.content.substring(0, 30) + (diary.content.length > 30 ? '...' : '') : '无文字内容';
        
        return `
            <tr>
                <td>${diary.id}</td>
                <td>${escapeHtml(diary.username)}</td>
                <td><span class="badge ${diary.diary_type === 'public' ? 'badge-public' : 'badge-private'}">${diary.diary_type === 'public' ? '公共' : '私密'}</span></td>
                <td>${diary.date}</td>
                <td>${escapeHtml(contentSummary)}</td>
                <td>${fileCount}</td>
                <td>
                    <button class="action-btn btn-danger" onclick="deleteDiary(${diary.id})">删除</button>
                </td>
            </tr>
        `;
    }).join('');
}

async function deleteDiary(diaryId) {
    if (!confirm('确定要删除这篇日记吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/diaries/${diaryId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ 日记已删除');
            loadAllDiaries();
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        alert('❌ 网络错误');
    }
}

// ============================================
// 文件管理
// ============================================
async function loadFiles() {
    try {
        const response = await fetch('/admin/files');
        const data = await response.json();
        
        if (data.success) {
            displayFiles(data.files);
        }
    } catch (error) {
        console.error('加载文件失败:', error);
    }
}

function displayFiles(files) {
    const tbody = document.getElementById('filesTableBody');
    
    if (!files || files.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#999;padding:40px;">暂无文件</td></tr>';
        return;
    }
    
    const typeIcons = {
        'images': '🖼️',
        'videos': '🎥',
        'documents': '📄'
    };
    
    tbody.innerHTML = files.map(file => {
        const fileUrl = `/diary/uploads/${file.path}`;
        const isImage = file.type === 'images';
        const isVideo = file.type === 'videos';
        
        return `
            <tr>
                <td>${typeIcons[file.type] || '📄'} ${escapeHtml(file.name)}</td>
                <td><span class="badge badge-${file.type === 'images' ? 'public' : file.type === 'videos' ? 'private' : 'user'}">${file.type}</span></td>
                <td>${file.size_human}</td>
                <td style="font-size:12px;color:#999;">${escapeHtml(file.path)}</td>
                <td class="admin-file-actions">
                    <a href="${fileUrl}" target="_blank" class="action-btn btn-primary" title="${isImage ? '查看图片' : isVideo ? '播放视频' : '下载文件'}">
                        ${isImage ? '👁️ 查看' : isVideo ? '▶️ 播放' : '⬇️ 下载'}
                    </a>
                    <button class="action-btn btn-danger btn-delete-file" data-file-path="${escapeHtml(file.path)}">删除</button>
                </td>
            </tr>
        `;
    }).join('');

    // 绑定删除事件（避免 onclick 中的 URL 编码问题）
    document.querySelectorAll('.btn-delete-file').forEach(btn => {
        btn.addEventListener('click', function() {
            deleteFile(this.dataset.filePath);
        });
    });
}

async function deleteFile(filePath) {
    if (!confirm('确定要删除这个文件吗？')) {
        return;
    }
    
    try {
        // 对路径中的每个部分进行编码，但保留 / 分隔符
        const encodedPath = filePath.split('/').map(encodeURIComponent).join('/');
        const response = await fetch(`/admin/files/${encodedPath}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ 文件已删除');
            loadFiles();
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        alert('❌ 网络错误');
    }
}

// ============================================
// 工具函数
// ============================================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}