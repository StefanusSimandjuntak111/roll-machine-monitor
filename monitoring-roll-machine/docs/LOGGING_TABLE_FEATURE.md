# Logging Table Feature

## Overview
Fitur logging table telah ditambahkan ke aplikasi Roll Machine Monitor untuk mencatat dan menampilkan data produksi dalam bentuk tabel. Fitur ini menyimpan data produksi dalam format JSON per hari dan menampilkan 50 data terakhir dalam tabel yang mudah dibaca.

## Fitur Utama

### 1. Penyimpanan Data Otomatis
- Data produksi disimpan secara otomatis dalam file JSON per hari
- Format file: `logs/production_log_YYYY-MM-DD.json`
- Maksimal 50 data terakhir disimpan per hari

### 2. Tabel Logging
- Menampilkan 50 data produksi terakhir
- Kolom yang ditampilkan:
  - **Waktu**: Timestamp produksi (HH:MM:SS)
  - **Nama Produk**: Nama produk yang diproduksi
  - **Kode Produk**: Kode produk
  - **Panjang (m)**: Panjang produk dalam meter
  - **Batch**: Nomor batch produksi
  - **Waktu ke Print (s)**: Waktu dari mesin tidak menggulung sampai ke print
  - **Waktu ke Gulung (s)**: Waktu dari print ke gulung lagi

### 3. Auto-Refresh
- Tabel diperbarui otomatis setiap 30 detik
- Tombol refresh manual tersedia
- Data terbaru ditandai dengan highlight kuning

## Implementasi Teknis

### File yang Ditambahkan
1. `monitoring/logging_table.py` - Core logging functionality
2. `monitoring/ui/logging_table_widget.py` - UI widget untuk tabel
3. `test_logging_table.py` - Script test untuk menambah data contoh

### Modifikasi File Existing
1. `monitoring/ui/main_window.py` - Integrasi logging table widget
2. `monitoring/ui/product_form.py` - Property untuk akses data produk

### Struktur Data JSON
```json
{
  "product_name": "Kain Cotton Premium",
  "product_code": "CTN-001", 
  "product_length": 150.5,
  "batch": "BATCH-2024-001",
  "time_to_print": 45.2,
  "time_to_roll": 12.8,
  "timestamp": "2024-01-15T10:30:15.123456"
}
```

## Cara Penggunaan

### 1. Menjalankan Aplikasi
```bash
python run_app.py
```

### 2. Menambah Data Contoh (Testing)
```bash
python test_logging_table.py
```

### 3. Melihat Data Log
- Data tersimpan di folder `logs/`
- Format file: `production_log_YYYY-MM-DD.json`
- Bisa dibuka dengan text editor atau JSON viewer

## Deteksi Produksi Otomatis

Sistem secara otomatis mendeteksi siklus produksi berdasarkan:
- Perubahan panjang produk yang signifikan (> 0.1 meter)
- Data produk dari form (nama, kode, batch)
- Perhitungan waktu otomatis

## Konfigurasi

### Pengaturan Logging
- Direktori log: `logs/` (bisa diubah di `LoggingTable.__init__()`)
- Maksimal entri: 50 (bisa diubah di `LoggingTable.max_entries`)
- Auto-refresh interval: 30 detik (bisa diubah di `LoggingTableWidget.setup_timer()`)

### Pengaturan Deteksi Produksi
- Threshold perubahan panjang: 0.1 meter (bisa diubah di `handle_production_logging()`)

## Troubleshooting

### Masalah Umum
1. **Tabel tidak muncul**: Pastikan PySide6 terinstall dengan benar
2. **Data tidak tersimpan**: Cek permission folder `logs/`
3. **Auto-refresh tidak bekerja**: Restart aplikasi

### Debug
- Log aplikasi akan menampilkan error jika ada masalah
- File JSON bisa dicek manual untuk validasi data

## Pengembangan Selanjutnya

### Fitur yang Bisa Ditambahkan
1. Export data ke Excel/CSV
2. Filter data berdasarkan tanggal/produk
3. Grafik trend produksi
4. Backup data otomatis
5. Notifikasi ketika ada data baru

### Optimisasi
1. Database SQLite untuk data besar
2. Kompresi data lama
3. Cache untuk performa lebih baik 