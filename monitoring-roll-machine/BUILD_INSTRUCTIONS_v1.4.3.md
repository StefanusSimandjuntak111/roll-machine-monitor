# Instruksi Build Installer v1.4.3

## Persyaratan

Sebelum membangun installer, pastikan Anda telah menginstall:

1. **Python 3.9+** - Download dari [python.org](https://www.python.org/downloads/)
2. **PyInstaller** - Install dengan: `pip install pyinstaller`
3. **NSIS (Nullsoft Scriptable Install System)** - Download dari [nsis.sourceforge.io](https://nsis.sourceforge.io/Download)

## Langkah-langkah Build

### Opsi 1: Menggunakan Batch File (Paling Mudah)

1. Buka Command Prompt atau PowerShell
2. Navigate ke folder `monitoring-roll-machine`
3. Jalankan:
   ```batch
   build_installer_v1.4.3.bat
   ```

### Opsi 2: Menggunakan PowerShell Script

1. Buka PowerShell
2. Navigate ke folder `monitoring-roll-machine`
3. Jalankan:
   ```powershell
   .\build_installer_v1.4.3.ps1
   ```

### Opsi 3: Menggunakan Python Script Langsung

1. Buka Command Prompt atau PowerShell
2. Navigate ke folder `monitoring-roll-machine`
3. Jalankan:
   ```bash
   python build_v1.4.3.py
   ```

## Proses Build

Script build akan melakukan langkah-langkah berikut:

1. ✅ **Check Requirements** - Memverifikasi Python, PyInstaller, dan NSIS
2. ✅ **Clean Build Artifacts** - Membersihkan build sebelumnya
3. ✅ **Test Application** - Menguji import semua modul
4. ✅ **Build Executable** - Membuat .exe dengan PyInstaller
5. ✅ **Test Executable** - Menguji executable yang dibuat
6. ✅ **Create NSIS Installer** - Membuat installer NSIS
7. ✅ **Create Release Notes** - Membuat file release notes

## Output

Setelah build selesai, installer akan tersedia di:
```
releases/Monitoring-Roll-Machine-v1.4.3-Setup.exe
```

File release notes akan tersedia di:
```
releases/RELEASE_NOTES_v1.4.3.md
```

## Troubleshooting

### Error: PyInstaller not found
```bash
pip install pyinstaller
```

### Error: NSIS not found
- Download dan install NSIS dari https://nsis.sourceforge.io/Download
- Pastikan NSIS terinstall di:
  - `C:\Program Files\NSIS\` atau
  - `C:\Program Files (x86)\NSIS\`

### Error: Version mismatch
- Pastikan file `monitoring/version.py` memiliki `VERSION = "1.4.3"`

### Error: Import failed
- Pastikan semua dependencies terinstall: `pip install -r requirements.txt`
- Pastikan Anda berada di direktori yang benar

## Fitur Installer

Installer yang dibuat akan memiliki fitur:

- ✅ **Modern UI** dengan wizard installation
- ✅ **Auto-detect** instalasi sebelumnya
- ✅ **Update support** - dapat mengupdate dari versi sebelumnya
- ✅ **Component selection** - pilih komponen yang ingin diinstall
- ✅ **Windows Service** - opsi install sebagai service
- ✅ **Python Environment** - opsi setup virtual environment
- ✅ **Database Setup** - dokumentasi setup database
- ✅ **Uninstaller** - uninstall yang bersih

## Catatan

- Build process membutuhkan waktu beberapa menit
- Pastikan tidak ada aplikasi yang sedang berjalan saat build
- Installer akan otomatis menghentikan aplikasi yang sedang berjalan sebelum install/update
