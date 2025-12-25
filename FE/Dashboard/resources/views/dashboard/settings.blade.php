<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>Pengaturan - YO-vehicle</title>

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">

    <style>
        /* ========== COPY DARI HISTORY.BLADE UNTUK SIDEBAR ========== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ffffff 0%, #764ba2 100%);
            min-height: 100vh;
            transition: background 0.4s, color 0.4s;
        }
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 280px;
            height: 100vh;
            background: white;
            box-shadow: 4px 0 10px rgba(0,0,0,0.1);
            padding: 30px 0;
            z-index: 1000;
            transition: background 0.4s;
        }
        .sidebar-brand {
            padding: 0 30px 30px;
            border-bottom: 2px solid #f0f0f0;
            margin-bottom: 30px;
        }
        .sidebar-brand h3 {
            color: #667eea;
            font-weight: bold;
            font-size: 24px;
        }
        .sidebar-menu {
            list-style: none;
            padding: 0 15px;
        }
        .sidebar-menu li {
            margin-bottom: 5px;
        }
        .sidebar-menu a {
            display: flex;
            align-items: center;
            padding: 15px 20px;
            color: #666;
            text-decoration: none;
            border-radius: 10px;
            transition: all 0.3s;
        }
        .sidebar-menu a:hover,
        .sidebar-menu a.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .sidebar-menu i {
            margin-right: 15px;
            width: 20px;
            text-align: center;
        }
        .sidebar-user {
            position: absolute;
            bottom: 30px;
            left: 30px;
            right: 30px;
            display: flex;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .sidebar-user-info h6 {
            margin: 0;
            font-size: 14px;
            font-weight: 600;
        }
        .sidebar-user-info p {
            margin: 0;
            font-size: 12px;
            color: #999;
        }

        /* ========== MAIN CONTENT ========== */
        .main-content {
            margin-left: 280px;
            padding: 30px;
            transition: background 0.4s, color 0.4s;
        }

        .top-header {
            background: white;
            padding: 20px 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .settings-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }

        /* DARK MODE STYLE */
        body.dark-mode {
            background: linear-gradient(135deg, #1e1e2f 0%, #3a3a59 100%);
            color: #eaeaea;
        }
        body.dark-mode .sidebar {
            background: #2c2c3c;
        }
        body.dark-mode .sidebar-menu a {
            color: #aaa;
        }
        body.dark-mode .sidebar-menu a:hover,
        body.dark-mode .sidebar-menu a.active {
            color: white;
        }
        body.dark-mode .main-content,
        body.dark-mode .settings-card,
        body.dark-mode .top-header {
            background: #2f2f48;
            color: #eaeaea;
        }

        /* RESPONSIVE */
        @media (max-width: 768px) {
            .sidebar { transform: translateX(-100%); }
            .main-content { margin-left: 0; }
        }
    </style>
</head>

<body>
    <!-- SIDEBAR (SAMA PERSIS DARI HISTORY.BLADE) -->
    <div class="sidebar">
        <div class="sidebar-brand">
            <h3><i class="fas fa-traffic-light"></i> YO-vehicle</h3>
            <small style="color: #999;">Admin</small>
        </div>

        <ul class="sidebar-menu">
            <li><a href="/"><i class="fas fa-home"></i><span>Dashboard</span></a></li>
            <li><a href="/dashboard/history"><i class="fas fa-history"></i><span>Riwayat Kendaraan</span></a></li>
            <li><a href="/dashboard/settings" class="active"><i class="fas fa-cog"></i><span>Pengaturan</span></a></li>
        </ul>

        <div class="sidebar-user">
            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">A</div>
            <div class="sidebar-user-info">
                <h6>Rizqo SP</h6>
                <p>Administrator</p>
            </div>
        </div>
    </div>

    <!-- MAIN CONTENT -->
    <div class="main-content">
        <div class="top-header">
            <div>
                <h4><i class="fas fa-cog"></i> Pengaturan Sistem</h4>
                <p>Atur tampilan dan bahasa aplikasi</p>
            </div>
            <a href="/" class="btn btn-outline-primary">
                <i class="fas fa-arrow-left"></i> Kembali ke Dashboard
            </a>
        </div>

        <div class="settings-card">
            <h5><i class="fas fa-adjust"></i> Tema Tampilan</h5>
            <div class="form-check form-switch mt-2 mb-4">
                <input class="form-check-input" type="checkbox" id="themeToggle">
                <label class="form-check-label" for="themeToggle">Aktifkan Mode Gelap</label>
            </div>

            <hr>

            <h5><i class="fas fa-language"></i> Bahasa</h5>
            <select id="languageSelect" class="form-select mt-2" style="max-width: 250px;">
                <option value="id">Bahasa Indonesia</option>
                <option value="en">English</option>
            </select>

            <p id="previewText" class="mt-4 text-muted">Teks contoh: <strong>Selamat datang di YO-vehicle!</strong></p>
        </div>
    </div>

    <script>
        const themeToggle = document.getElementById('themeToggle');
        const languageSelect = document.getElementById('languageSelect');
        const previewText = document.getElementById('previewText');

        // Load from localStorage
        if (localStorage.getItem('theme') === 'dark') {
            document.body.classList.add('dark-mode');
            themeToggle.checked = true;
        }

        if (localStorage.getItem('language')) {
            languageSelect.value = localStorage.getItem('language');
            updateLanguagePreview();
        }

        // Theme toggle
        themeToggle.addEventListener('change', () => {
            if (themeToggle.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
            }
        });

        // Language change
        languageSelect.addEventListener('change', () => {
            localStorage.setItem('language', languageSelect.value);
            updateLanguagePreview();
        });

        function updateLanguagePreview() {
            if (languageSelect.value === 'id') {
                previewText.innerHTML = 'Teks contoh: <strong>Selamat datang di YO-vehicle!</strong>';
            } else {
                previewText.innerHTML = 'Sample text: <strong>Welcome to YO-vehicle!</strong>';
            }
        }
    </script>
</body>
</html>
