Saya sedang membuat aplikasi desktop Python menggunakan virtual environment (`venv`), dan ingin Anda bantu saya membuat sistem build dan installer Windows yang lengkap dan profesional.

### Tujuan
Hasil akhir saya ingin:
- File installer: `installer.exe`
- Lokasi hasil: `D:\Apps\monitoring-roll-machine\monitoring-roll-machine\releases`
- Aplikasi ini GUI-based dan bernama: **Monitoring Roll Machine**
- Tidak perlu Python terpisah (standalone)
- Menginstall ke: `C:\Program Files\Monitoring Roll Machine`
- Membuat shortcut ke desktop
- Tidak ada console window saat aplikasi dijalankan
- Semua resource (config, icon, dll) disertakan
- Termasuk metadata versi: {{versi-sekarang}}

### Struktur Proyek Saya:
D:\Apps\monitoring-roll-machine\monitoring-roll-machine
│
├── monitoring
│   ├── __init__.py
│   ├── main.py         # Entry point of the GUI application
│   ├── ui
│   │   └── monitoring_view.py
│   └── version.py
│
├── requirements.txt
├── config.ini          # Resource file
├── icon.ico            # Application icon
├── venv\               # Virtual environment (should not be included in build)

### Yang Saya Butuhkan:

1. **Perintah PyInstaller lengkap**:
   - Use `venv`
   - Build from `monitoring/main.py`
   - Include: `config.ini` and `icon.ico`
   - No console window
   - Use application icon
   - Output to `dist/`

2. **(Opsional) File `.spec` jika perlu**

3. **Script NSIS lengkap (.nsi)**:
   - Output: `Monitoring-Roll-Machine-Setup-{{versi-sekarang}}.exe`
   - Lokasi output: `D:\Apps\monitoring-roll-machine\monitoring-roll-machine\releases`
   - Install ke `C:\Program Files\Monitoring Roll Machine`
   - Buat shortcut desktop
   - Sertakan uninstall support
   - Gunakan ikon `icon.ico`
   - Tambahkan `RequestExecutionLevel admin`
   - Versi di metadata: `{{versi-sekarang}}`
   - Versi juga muncul di judul window NSIS wizard

4. **Langkah Build Lengkap**:
   - Step-by-step dari aktifkan venv, build `.exe`, compile NSIS, hingga hasil installer
   - Gunakan path Windows valid (pakai double-backslash)
   - Pastikan tidak ada error path / permission

5. **Opsional:**
   - Jika bisa, tambahkan `__version__ = "{{versi-sekarang}}"` ke `main.py` dan pakai itu di shortcut / installer

