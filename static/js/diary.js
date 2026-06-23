// 家庭日记系统 - 前端JavaScript

// currentUserId 由 dashboard.html 中的 <script> 标签设置
// const currentUserId = {{ user_id }};

// ============================================
// 工具函数
// ============================================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ============================================
// 文件选择显示功能（支持累积选择 + 删除单个文件）
// ============================================
// 存储每个文件输入框的累积文件列表
const accumulatedFiles = {};

function setupFileInputDisplay(inputId, listId, areaId, icon) {
    const input = document.getElementById(inputId);
    const list = document.getElementById(listId);
    const area = document.getElementById(areaId);
    const label = area ? area.querySelector('.file-label') : null;
    
    if (!input || !list || !area) return;
    
    // 初始化累积文件列表
    accumulatedFiles[inputId] = new DataTransfer();
    
    input.addEventListener('change', function() {
        const newFiles = Array.from(this.files);
        
        if (newFiles.length === 0) return;
        
        // 将新文件添加到累积列表（不覆盖）
        const dt = accumulatedFiles[inputId];
        newFiles.forEach(file => {
            dt.items.add(file);
        });
        
        // 更新 input.files（用于表单提交）
        this.files = dt.files;
        
        // 刷新显示
        refreshFileDisplay(inputId, listId, areaId, icon, label);
        
        // 清空 input 的 value，允许重复选择同一文件
        this.value = '';
    });
    
    // 点击 label 区域也可以触发文件选择
    if (label) {
        label.addEventListener('click', function(e) {
            e.preventDefault();
            input.click();
        });
    }
}

function refreshFileDisplay(inputId, listId, areaId, icon, label) {
    const list = document.getElementById(listId);
    const area = document.getElementById(areaId);
    const dt = accumulatedFiles[inputId];
    const files = Array.from(dt.files);
    
    if (files.length === 0) {
        list.innerHTML = '';
        list.classList.remove('active');
        area.classList.remove('has-files');
        if (label) label.textContent = '点击选择';
        return;
    }
    
    // 更新标签文字
    if (label) label.textContent = '继续选择';
    
    // 显示文件数量徽章
    let html = `<span class="file-count-badge">已选择 ${files.length} 个文件</span>`;
    
    // 显示每个文件（带删除按钮）
    files.forEach((file, index) => {
        const size = formatFileSize(file.size);
        html += `
            <div class="file-item" data-file-index="${index}">
                <span class="file-icon">${icon}</span>
                <span class="file-name">${escapeHtml(file.name)}</span>
                <span class="file-size">${size}</span>
                <button type="button" class="file-remove-btn" title="删除此文件">删除</button>
            </div>
        `;
    });
    
    list.innerHTML = html;
    list.classList.add('active');
    area.classList.add('has-files');
    
    // 绑定删除按钮事件
    list.querySelectorAll('.file-remove-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            e.preventDefault();
            const fileItem = this.closest('.file-item');
            const fileIndex = parseInt(fileItem.dataset.fileIndex);
            removeFile(inputId, fileIndex, listId, areaId, icon, label);
        });
    });
}

function removeFile(inputId, removeIndex, listId, areaId, icon, label) {
    const dt = accumulatedFiles[inputId];
    const input = document.getElementById(inputId);
    
    // 创建新的 DataTransfer，排除要删除的文件
    const newDt = new DataTransfer();
    const files = Array.from(dt.files);
    files.forEach((file, index) => {
        if (index !== removeIndex) {
            newDt.items.add(file);
        }
    });
    
    accumulatedFiles[inputId] = newDt;
    input.files = newDt.files;
    
    // 刷新显示
    refreshFileDisplay(inputId, listId, areaId, icon, label);
}

// 初始化文件输入显示
document.addEventListener('DOMContentLoaded', function() {
    // 公共日记
    setupFileInputDisplay('publicImages', 'publicImagesList', 'publicImagesArea', '🖼️');
    setupFileInputDisplay('publicVideos', 'publicVideosList', 'publicVideosArea', '🎥');
    setupFileInputDisplay('publicFiles', 'publicFilesList', 'publicFilesArea', '📎');
    
    // 私密日记
    setupFileInputDisplay('privateImages', 'privateImagesList', 'privateImagesArea', '🖼️');
    setupFileInputDisplay('privateVideos', 'privateVideosList', 'privateVideosArea', '🎥');
    setupFileInputDisplay('privateFiles', 'privateFilesList', 'privateFilesArea', '📎');
    
    // 侧边栏导航点击事件
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', function() {
            switchPage(this.dataset.page);
        });
    });

    // 初始化日期为今天
    initDates();

    // 加载公共日记
    loadPublicDiaries();
});

// 切换页面
function switchPage(pageId) {
    // 移除所有active
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    
    // 添加active到当前项
    document.querySelector(`[data-page="${pageId}"]`).classList.add('active');
    document.getElementById(pageId).classList.add('active');
    
    // 加载对应内容
    if (pageId === 'public-view') {
        loadPublicDiaries();
    } else if (pageId === 'private-view') {
        loadPrivateDiaries();
    }
}

// ============================================
// 日期处理
// ============================================
function initDates() {
    const today = new Date().toISOString().split('T')[0];
    
    // 公共日记
    document.getElementById('publicDate').value = today;
    document.getElementById('publicDateCustom').value = today;
    
    // 私密日记
    document.getElementById('privateDate').value = today;
    document.getElementById('privateDateCustom').value = today;
}

function setTodayDate(type) {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById(`${type}Date`).value = today;
    document.getElementById(`${type}DateCustom`).value = today;
}

// 日期输入同步
document.addEventListener('input', function(e) {
    if (e.target.classList.contains('input-date-custom')) {
        const value = e.target.value;
        const type = e.target.id.includes('public') ? 'public' : 'private';
        const dateInput = document.getElementById(`${type}Date`);
        
        if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
            dateInput.value = value;
        }
    }
});

document.addEventListener('change', function(e) {
    if (e.target.classList.contains('input-date')) {
        const type = e.target.id.includes('public') ? 'public' : 'private';
        const customInput = document.getElementById(`${type}DateCustom`);
        customInput.value = e.target.value;
    }
});

// ============================================
// 日记加载与显示
// ============================================
// 存储当前页面加载的日记数据
let currentDiaries = [];

async function loadPublicDiaries() {
    try {
        const response = await fetch('/diary/public');
        const data = await response.json();
        
        if (data.success) {
            currentDiaries = data.diaries;
            displayDiaries(data.diaries, 'publicDiaries');
        }
    } catch (error) {
        console.error('加载公共日记失败:', error);
        document.getElementById('publicDiaries').innerHTML = 
            '<div class="empty-message">加载失败，请刷新重试</div>';
    }
}

async function loadPrivateDiaries() {
    try {
        const response = await fetch('/diary/private');
        const data = await response.json();
        
        if (data.success) {
            currentDiaries = data.diaries;
            displayDiaries(data.diaries, 'privateDiaries');
        }
    } catch (error) {
        console.error('加载个人日记失败:', error);
        document.getElementById('privateDiaries').innerHTML = 
            '<div class="empty-message">加载失败，请刷新重试</div>';
    }
}

function displayDiaries(diaries, containerId) {
    const container = document.getElementById(containerId);
    
    if (!diaries || diaries.length === 0) {
        container.innerHTML = '<div class="empty-message">暂无日记，快去写一篇吧！</div>';
        return;
    }
    
    console.log(`displayDiaries(${containerId}): 共 ${diaries.length} 篇日记`, diaries);
    
    container.innerHTML = diaries.map(diary => `
        <div class="diary-card" data-diary-id="${diary.id}">
            <div class="diary-card-header">
                <span class="diary-author">${escapeHtml(diary.username)}</span>
                <span class="diary-date">${escapeHtml(diary.date)}</span>
            </div>
            <div class="diary-content">${escapeHtml(diary.content || '无文字记录')}</div>
            ${renderMedia(diary)}
            ${(diary.user_id === currentUserId || isCurrentUserAdmin) ? `
                <div class="diary-actions">
                    <button class="btn-delete-diary" onclick="deleteMyDiary(${diary.id})">🗑️ 删除</button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

function renderMedia(diary) {
    let html = '';
    let hasMedia = false;
    
    const images = Array.isArray(diary.images) ? diary.images : [];
    const videos = Array.isArray(diary.videos) ? diary.videos : [];
    const files = Array.isArray(diary.files) ? diary.files : [];
    
    // 图片缩略图
    if (images.length > 0) {
        hasMedia = true;
        html += '<div class="diary-media-section"><div class="diary-media-label">🖼️ 图片</div><div class="diary-media">';
        images.forEach((img, i) => {
            html += `<div class="media-thumb" onclick="openMediaPreview('/diary/${img}', 'image')">
                <img src="/diary/${img}" alt="图片${i+1}" loading="lazy" onerror="this.parentElement.style.display='none'">
            </div>`;
        });
        html += '</div></div>';
    }
    
    // 视频播放器
    if (videos.length > 0) {
        hasMedia = true;
        html += '<div class="diary-media-section"><div class="diary-media-label">🎥 视频</div><div class="diary-media">';
        videos.forEach((video, i) => {
            html += `<div class="media-video">
                <video controls preload="metadata" onerror="this.style.display='none'">
                    <source src="/diary/${video}">
                    您的浏览器不支持视频播放
                </video>
            </div>`;
        });
        html += '</div></div>';
    }
    
    // 文件下载链接
    if (files.length > 0) {
        hasMedia = true;
        html += '<div class="diary-media-section"><div class="diary-media-label">📎 附件</div><div class="diary-media">';
        files.forEach(file => {
            const filename = file.split('/').pop();
            html += `<a href="/diary/${file}" class="diary-file-link" target="_blank" download>
                📎 ${escapeHtml(filename)}
            </a>`;
        });
        html += '</div></div>';
    }
    
    if (hasMedia) {
        html += `<div class="diary-media-actions">
            <button class="btn-preview-all" onclick="event.stopPropagation(); openFullPreview(${JSON.stringify(images.map(i => '/diary/' + i))}, ${JSON.stringify(videos.map(v => '/diary/' + v))}, ${JSON.stringify(files.map(f => '/diary/' + f))})">🔍 全览</button>
        </div>`;
    }
    
    return html;
}

// ============================================
// 全页全览 - 汇总当前页面所有日记的所有附件
// ============================================
function openPageFullPreview() {
    let allImages = [];
    let allVideos = [];
    let allFiles = [];
    
    (currentDiaries || []).forEach(diary => {
        const images = Array.isArray(diary.images) ? diary.images : [];
        const videos = Array.isArray(diary.videos) ? diary.videos : [];
        const files = Array.isArray(diary.files) ? diary.files : [];
        
        allImages.push(...images.map(i => '/diary/' + i));
        allVideos.push(...videos.map(v => '/diary/' + v));
        allFiles.push(...files.map(f => '/diary/' + f));
    });
    
    if (allImages.length === 0 && allVideos.length === 0 && allFiles.length === 0) {
        alert('当前页面没有任何附件');
        return;
    }
    
    openFullPreview(allImages, allVideos, allFiles);
}

// ============================================
// 全览弹窗
// ============================================
function openFullPreview(imageUrls, videoUrls, fileUrls) {
    let modal = document.getElementById('fullPreviewModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'fullPreviewModal';
        modal.className = 'full-preview-modal';
        modal.innerHTML = `
            <div class="full-preview-overlay" onclick="closeFullPreview()"></div>
            <div class="full-preview-content">
                <div class="full-preview-header">
                    <h2>📂 全部附件</h2>
                    <button class="full-preview-close" onclick="closeFullPreview()">✕</button>
                </div>
                <div class="full-preview-body" id="fullPreviewBody"></div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    const body = document.getElementById('fullPreviewBody');
    let html = '';
    
    if (imageUrls.length > 0) {
        html += '<div class="fp-section"><h3>🖼️ 图片 (' + imageUrls.length + ')</h3><div class="fp-grid">';
        imageUrls.forEach(url => {
            html += `<div class="fp-item"><img src="${url}" loading="lazy" onclick="openMediaPreview('${url}','image')" onerror="this.style.display='none'"></div>`;
        });
        html += '</div></div>';
    }
    
    if (videoUrls.length > 0) {
        html += '<div class="fp-section"><h3>🎥 视频 (' + videoUrls.length + ')</h3><div class="fp-grid">';
        videoUrls.forEach(url => {
            html += `<div class="fp-item"><video controls preload="metadata"><source src="${url}"></video></div>`;
        });
        html += '</div></div>';
    }
    
    if (fileUrls.length > 0) {
        html += '<div class="fp-section"><h3>📎 文件 (' + fileUrls.length + ')</h3><div class="fp-grid">';
        fileUrls.forEach(url => {
            const name = url.split('/').pop();
            html += `<a href="${url}" class="fp-file-link" target="_blank" download>📎 ${name}</a>`;
        });
        html += '</div></div>';
    }
    
    body.innerHTML = html;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeFullPreview() {
    const modal = document.getElementById('fullPreviewModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function openMediaPreview(url, type) {
    const win = window.open(url, '_blank');
    if (!win) {
        alert('请允许弹窗以查看完整内容');
    }
}

// ============================================
// 表单提交
// ============================================
document.addEventListener('submit', function(e) {
    if (e.target.id === 'publicDiaryForm') {
        e.preventDefault();
        submitDiaryForm(e.target, '公共日记');
    } else if (e.target.id === 'privateDiaryForm') {
        e.preventDefault();
        submitDiaryForm(e.target, '私密日记');
    }
});

async function submitDiaryForm(form, type) {
    const formData = new FormData();
    
    // 添加隐藏字段
    const diaryType = form.querySelector('input[name="diary_type"]').value;
    formData.append('diary_type', diaryType);
    
    // 获取日期
    const customDate = form.querySelector('.input-date-custom').value;
    const dateInput = form.querySelector('.input-date').value;
    formData.append('date', customDate || dateInput);
    
    // 添加文字内容
    const content = form.querySelector('textarea[name="content"]').value;
    formData.append('content', content);
    
    // 手动添加累积的文件（绕过 input.files 兼容性问题）
    const prefix = diaryType === 'public' ? 'public' : 'private';
    const imageInputId = `${prefix}Images`;
    const videoInputId = `${prefix}Videos`;
    const fileInputId = `${prefix}Files`;
    
    const imageDt = accumulatedFiles[imageInputId];
    const videoDt = accumulatedFiles[videoInputId];
    const fileDt = accumulatedFiles[fileInputId];
    
    let totalFiles = 0;
    
    if (imageDt) {
        const files = Array.from(imageDt.files);
        files.forEach(f => { formData.append('images', f); totalFiles++; });
    }
    if (videoDt) {
        const files = Array.from(videoDt.files);
        files.forEach(f => { formData.append('videos', f); totalFiles++; });
    }
    if (fileDt) {
        const files = Array.from(fileDt.files);
        files.forEach(f => { formData.append('files', f); totalFiles++; });
    }
    
    console.log(`提交日记: type=${diaryType}, date=${customDate || dateInput}, files=${totalFiles}, content=${(content||'').length}字`);
    
    // 显示加载提示
    const submitBtn = form.querySelector('.btn-submit');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = totalFiles > 0 ? `⏳ 上传中 (${totalFiles}个文件)...` : '⏳ 保存中...';
    
    try {
        const response = await fetch('/diary/create', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        console.log('服务器响应:', data);
        
        if (data.success) {
            alert(`✅ ${type}保存成功！`);
            form.reset();
            initDates();
            clearAllAccumulatedFiles(form);
            // 刷新列表
            if (diaryType === 'public') {
                loadPublicDiaries();
            } else {
                loadPrivateDiaries();
            }
        } else {
            alert(`❌ ${data.message || '保存失败'}`);
        }
    } catch (error) {
        console.error('提交错误:', error);
        alert('❌ 网络错误，请稍后重试');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// ============================================
// 退出登录
// ============================================
document.addEventListener('click', function(e) {
    if (e.target.id === 'logoutBtn') {
        logout();
    }
});

async function logout() {
    if (!confirm('确定要退出登录吗？')) return;
    
    try {
        await fetch('/auth/logout', { method: 'POST' });
        window.location.href = '/auth/login';
    } catch (error) {
        alert('退出失败，请重试');
    }
}

// ============================================
// 删除日记功能
// ============================================
async function deleteMyDiary(diaryId) {
    if (!confirm('确定要删除这篇日记吗？\n删除后无法恢复！')) {
        return;
    }
    
    try {
        const response = await fetch(`/diary/delete/${diaryId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ 日记已删除');
            // 重新加载当前页面
            const activePage = document.querySelector('.page.active');
            if (activePage.id === 'public-view') {
                loadPublicDiaries();
            } else if (activePage.id === 'private-view') {
                loadPrivateDiaries();
            }
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        console.error('删除失败:', error);
        alert('❌ 网络错误，请稍后重试');
    }
}

// ============================================
// 清除累积文件（表单提交成功后调用）
// ============================================
function clearAllAccumulatedFiles(form) {
    const type = form.id.includes('public') ? 'public' : 'private';
    const inputIds = [
        `${type}Images`, `${type}Videos`, `${type}Files`
    ];
    
    inputIds.forEach(inputId => {
        if (accumulatedFiles[inputId]) {
            accumulatedFiles[inputId] = new DataTransfer();
        }
        const input = document.getElementById(inputId);
        if (input) input.files = new DataTransfer().files;
        
        // 清除显示
        const listId = inputId.replace(type, `${type}`) + 'List';
        const areaId = inputId.replace(type, `${type}`) + 'Area';
        const list = document.getElementById(listId);
        const area = document.getElementById(areaId);
        if (list) {
            list.innerHTML = '';
            list.classList.remove('active');
        }
        if (area) {
            area.classList.remove('has-files');
            const label = area.querySelector('.file-label');
            if (label) label.textContent = '点击选择';
        }
    });
}