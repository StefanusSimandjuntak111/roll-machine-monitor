
# 🧵 Alur Sistem Logging Produk Roll Kain (Berbasis Length Counter)

## ⚙️ Konsep Dasar
- Sistem digunakan untuk mencatat proses rolling kain per produk.
- Panjang kain dihitung menggunakan **length counter**.
- Produk disimpan ke log saat **user klik tombol "Print"**.
- **Cycle Time** dihitung berdasarkan **selisih waktu antara `start_time` produk ini dan produk berikutnya (yang dimulai ketika length = 1)**.
- **Reset Counter** digunakan untuk mengakhiri satu produk dan memulai produk berikutnya.
- **Close Cycle** digunakan untuk mengakhiri produk terakhir dan menghitung `cycle_time` terakhir.

---

## 🔄 Alur Per Produk

### 1. Produk 1 Dimulai
- User mulai roll kain, **length counter = 1**
- Sistem menyimpan waktu ini sebagai `start_time` Produk 1
- Produk 1 belum punya `cycle_time`

### 2. Roll Selesai → User Klik Print
- Sistem menyimpan data produk ke log:
  ```json
  {
    "product_name": "Baby Doll-1",
    "product_code": "BD-1",
    "product_length": 1.18,
    "batch": "1",
    "cycle_time": null,
    "roll_time": 166.380827,
    "timestamp": "2025-07-18T15:56:49.148656"
  }
````

### 3. User Klik Reset Counter

* Counter kembali ke `0`
* Siap memulai produk berikutnya

### 4. Produk 2 Dimulai

* User mulai roll baru, **length counter = 1**
* Sistem simpan `start_time` Produk 2
* Sistem **hitung `cycle_time` Produk 1**:

  ```python
  cycle_time_produk_1 = start_time_produk_2 - start_time_produk_1
  ```
* Sistem update record Produk 1 dengan nilai `cycle_time` tersebut

### 5. User Klik Print untuk Produk 2

* Sistem simpan Produk 2:

  ```json
  {
    "product_name": "Baby Doll-2", 
    "product_code": "BD-2", 
    "product_length": 1.18,
    "batch": "1",
    "cycle_time": null,
    "roll_time": 166.380827,
    "timestamp": "2025-07-18T16:00:12.123456"
  }
  ```

### 6. Ulangi Langkah 3–5

* Untuk Produk 3, 4, dst sampai produk ke-49

---

## 🛑 Produk Terakhir (Contoh: Produk ke-50)

### 7. Produk 50 Dimulai

* Sama seperti sebelumnya: length = 1 → simpan `start_time` Produk 50

### 8. Roll selesai → User Klik Print

* Sistem simpan Produk 50 dengan `cycle_time = null`

### 9. User Klik Close Cycle

* Sistem ambil waktu sekarang sebagai `end_time`
* Hitung `cycle_time` Produk 50:

  ```python
  cycle_time_produk_50 = end_time - start_time_produk_50
  ```
* Update Produk 50 dengan nilai `cycle_time` tersebut

---

## 📋 Ringkasan Alur

| Langkah | Aksi User               | Sistem Melakukan                                                         |
| ------- | ----------------------- | ------------------------------------------------------------------------ |
| 1       | Mulai roll (length = 1) | Simpan `start_time`                                                      |
| 2       | Klik Print              | Simpan data produk dengan `cycle_time = null`                            |
| 3       | Klik Reset Counter      | Length reset ke 0                                                        |
| 4       | Mulai produk baru       | Simpan `start_time` baru, hitung `cycle_time` produk sebelumnya          |
| 5       | Klik Print lagi         | Simpan produk baru (`cycle_time` tetap null)                             |
| ...     | ...                     | Ulangi proses hingga produk terakhir                                     |
| n       | Klik Close Cycle        | Hitung dan update `cycle_time` produk terakhir (`end_time - start_time`) |

---

## ✅ Catatan Penting

* Perhitungan `cycle_time` tidak terjadi saat Print, tapi saat **produk baru dimulai** atau **Close Cycle diklik**.
* Awal siklus ditentukan saat **length == 1**.
* Semua proses harus berjalan **otomatis**, tanpa input manual untuk cycle\_time.

```
