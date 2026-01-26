# Panduan Build Aplikasi Monitoring Roll Machine

## 📋 Persyaratan

Sebelum membangun aplikasi, pastikan Anda telah menginstall:

1. **Python 3.9 atau lebih baru**
   - Download dari [python.org](https://www.python.org/downloads/)
   - Pastikan Python ditambahkan ke PATH

2. **PyInstaller**
   ```bash
   pip install pyinstaller
   ```

3. **NSIS (Nullsoft Scriptable Install System)** - Hanya untuk membuat installer
   - Download dari [nsis.sourceforge.io](https://nsis.sourceforge.io/Download)
   - Install ke default location: `C:\Program Files (x86)\NSIS\` atau `C:\Program Files\NSIS\`

4. **Semua Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Cara Build (3 Metode)

### Metode 1: Menggunakan Batch File (Paling Mudah) ⭐

1. Buka **Command Prompt** atau **PowerShell**
2. Navigate ke folder `monitoring-roll-machine`:
   ```bash
   cd D:\htdocs\roll-machine-monitor\monitoring-roll-machine
   ```
3. Jalankan script build:
   ```bash
   build_installer_v1.4.3.bat
   ```

### Metode 2: Menggunakan PowerShell Script

1. Buka **PowerShell** (Run as Administrator jika diperlukan)
2. Navigate ke folder `monitoring-roll-machine`
3. Jalankan:
   ```powershell
   .\build_installer_v1.4.3.ps1
   ```

### Metode 3: Menggunakan Python Script Langsung

1. Buka **Command Prompt** atau **PowerShell**
2. Navigate ke folder `monitoring-roll-machine`
3. Jalankan:
   ```bash
   python build_v1.4.3.py
   ```

## 📦 Output Build

Setelah build selesai, file-file berikut akan tersedia:

### 1. Executable Standalone
```
dist/MonitoringRollMachine.exe
```
- File executable yang bisa langsung dijalankan
- Tidak perlu installer
- Cocok untuk testing atau distribusi sederhana

### 2. NSIS Installer (Jika menggunakan build script)
```
releases/Monitoring-Roll-Machine-v1.4.3-Setup.exe
```
- Installer lengkap dengan wizard
- Support update dari versi sebelumnya
- Auto-detect instalasi sebelumnya
- Uninstaller terintegrasi

### 3. Release Notes
```
releases/RELEASE_NOTES_v1.4.3.md
```
- Dokumentasi perubahan versi

## 🔧 Build Manual (Tanpa Installer)

Jika Anda hanya ingin membuat executable tanpa installer:

```bash
# 1. Install PyInstaller (jika belum)
pip install pyinstaller

# 2. Build executable
pyinstaller MonitoringRollMachine.spec

# 3. Executable akan ada di folder dist/
```

## 📝 Update Versi Sebelum Build

Jika ingin membuat build dengan versi baru:

1. Edit file `monitoring/version.py`:
   ```python
   VERSION = "1.4.4"  # Update versi baru
   BUILD_DATE = "2026-01-22"  # Update tanggal build
   ```

2. Buat build script baru (opsional):
   - Copy `build_v1.4.3.py` ke `build_v1.4.4.py`
   - Update versi di dalam script

3. Jalankan build seperti biasa

## ✅ Proses Build yang Akan Dilakukan

Script build akan melakukan langkah-langkah berikut secara otomatis:

1. ✅ **Check Requirements** - Memverifikasi Python, PyInstaller, dan NSIS
2. ✅ **Clean Build Artifacts** - Membersihkan build sebelumnya (folder `build/`, `dist/`)
3. ✅ **Test Application** - Menguji import semua modul penting
4. ✅ **Build Executable** - Membuat .exe dengan PyInstaller menggunakan `MonitoringRollMachine.spec`
5. ✅ **Test Executable** - Menguji executable yang dibuat
6. ✅ **Create NSIS Installer** - Membuat installer NSIS (jika menggunakan build script)
7. ✅ **Create Release Notes** - Membuat file release notes

## 🐛 Troubleshooting

### Error: PyInstaller not found
```bash
pip install pyinstaller
```

### Error: NSIS not found
- Download dan install NSIS dari https://nsis.sourceforge.io/Download
- Pastikan NSIS terinstall di:
  - `C:\Program Files\NSIS\` atau
  - `C:\Program Files (x86)\NSIS\`
- Atau skip pembuatan installer dan gunakan executable langsung

### Error: Version mismatch
- Pastikan file `monitoring/version.py` memiliki versi yang sesuai
- Check versi di `VERSION = "1.4.3"`

### Error: Import failed saat build
- Pastikan semua dependencies terinstall:
  ```bash
  pip install -r requirements.txt
  ```
- Pastikan Anda berada di direktori yang benar
- Coba jalankan aplikasi langsung dulu untuk memastikan tidak ada error:
  ```bash
  python run_app.py
  ```

### Error: Permission denied
- Pastikan tidak ada aplikasi yang sedang berjalan
- Tutup semua instance aplikasi sebelum build
- Run Command Prompt/PowerShell sebagai Administrator

### Build terlalu lama
- Normal, build bisa memakan waktu 2-5 menit
- Pastikan tidak ada antivirus yang memblokir
- Pastikan disk space cukup (minimal 500MB free space)

## 📋 Checklist Sebelum Build

- [ ] Semua perubahan kode sudah di-commit
- [ ] Versi sudah di-update di `monitoring/version.py`
- [ ] Semua dependencies terinstall (`pip install -r requirements.txt`)
- [ ] Aplikasi bisa dijalankan langsung (`python run_app.py`)
- [ ] Tidak ada aplikasi yang sedang berjalan
- [ ] NSIS sudah terinstall (jika ingin membuat installer)
- [ ] Disk space cukup

## 🎯 Fitur Installer (Jika menggunakan NSIS)

Installer yang dibuat akan memiliki fitur:

- ✅ **Modern UI** dengan wizard installation
- ✅ **Auto-detect** instalasi sebelumnya
- ✅ **Update support** - dapat mengupdate dari versi sebelumnya
- ✅ **Component selection** - pilih komponen yang ingin diinstall
- ✅ **Windows Service** - opsi install sebagai service
- ✅ **Python Environment** - opsi setup virtual environment
- ✅ **Database Setup** - dokumentasi setup database
- ✅ **Uninstaller** - uninstall yang bersih

## 📌 Catatan Penting

- ⏱️ Build process membutuhkan waktu **2-5 menit**
- 🚫 Pastikan **tidak ada aplikasi yang sedang berjalan** saat build
- 💾 Installer akan otomatis menghentikan aplikasi yang sedang berjalan sebelum install/update
- 📁 File executable akan berukuran sekitar **50-100 MB** (termasuk semua dependencies)
- 🔒 Antivirus mungkin mendeteksi executable sebagai false positive (normal untuk PyInstaller)

## 🆘 Bantuan Lebih Lanjut

Jika mengalami masalah, cek:
1. File `build_log.txt` untuk detail error
2. File `BUILD_INSTRUCTIONS_v1.4.3.md` untuk instruksi detail
3. Pastikan semua requirements terpenuhi

---

**Selamat Build! 🎉**
