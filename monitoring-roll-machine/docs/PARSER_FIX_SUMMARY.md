# Parser Fix Summary - JSK3588 Factor Correction

## 🔧 Masalah yang Diperbaiki

**Masalah:** Parser salah menginterpretasi factor, menyebabkan panjang meter menampilkan nilai yang salah (3.500 m instead of 0.35 m).

**Penyebab:** Parser menggunakan logika yang salah untuk menentukan factor berdasarkan bit 0 saja, padahal menurut dokumentasi JSK3588, factor ditentukan oleh lower 4 bits (01&0F).

## 📋 Perubahan yang Dilakukan

### 1. Perbaikan Logika Factor di `parser.py`

**Sebelum:**
```python
# Parse D6 flags
decimal_place = bool(d6 & 0x01)  # bit 0: decimal place
unit = "yard" if (d6 & 0x10) else "meter"  # bit 4: unit

# Determine factor based on decimal place
if decimal_place:
    factor = 0.1
    factor_text = "×0.1"
else:
    factor = 1.0
    factor_text = "×1.0"
```

**Sesudah:**
```python
# Parse D6 flags according to JSK3588 documentation
factor_code = d6 & 0x0F  # Lower 4 bits determine factor
unit = "yard" if (d6 & 0x10) else "meter"  # bit 4: unit

# Determine factor based on factor_code (01&0F)
if factor_code == 0x00:
    factor = 1.0
    factor_text = "×1.0"
elif factor_code == 0x01:
    factor = 0.1
    factor_text = "×0.1"
elif factor_code == 0x02:
    factor = 0.01
    factor_text = "×0.01"
else:
    # Default fallback
    factor = 0.01
    factor_text = f"×{factor_code:02X}"
```

### 2. Dokumentasi JSK3588 yang Benar

Menurut dokumentasi JSK3588:
```
01&0F系数（当值为00 长度速度*1
01 长度速度 *0.1
02 长度速度 *0.01）
```

- `00` = factor ×1.0
- `01` = factor ×0.1  
- `02` = factor ×0.01

## ✅ Hasil yang Diharapkan

Sekarang parser akan menampilkan:

**Contoh Data:** `55 AA 20 0C 02 00 00 03 00 00 01 31`
- **D6 = 02** → factor_code = 0x02 → factor = 0.01
- **Length Raw = 3** → 3 × 0.01 = **0.03 m** ✅
- **Speed Raw = 0** → 0 × 0.01 = **0.00 m/min** ✅

**Display yang Benar:**
```
Panjang    0.03 m
Kecepatan  0.00 m/s  
Faktor     ×0.01
```

## 🧪 Test Cases

### Test Case 1: Factor ×0.01 (02)
- **Input:** `55 AA 20 0C 02 00 00 03 00 00 01 31`
- **Expected:** Length = 0.030 m, Speed = 0.000 m/min
- **Factor:** ×0.01

### Test Case 2: Factor ×0.1 (01) 
- **Input:** `55 AA 20 0C 01 00 00 23 00 00 01 50`
- **Expected:** Length = 3.500 m, Speed = 0.000 m/min
- **Factor:** ×0.1

### Test Case 3: Factor ×1.0 (00)
- **Input:** `55 AA 20 0C 00 00 00 50 00 30 01 5D`
- **Expected:** Length = 80.000 m, Speed = 48.000 m/min
- **Factor:** ×1.0

## 🔄 Cara Test

1. **Jalankan aplikasi:**
   ```bash
   python -m monitoring.ui.main_window
   ```

2. **Hubungkan ke mesin JSK3588** atau gunakan mock serial

3. **Kirim command:** `55 AA 02 00 00 01`

4. **Verifikasi display cards** menampilkan nilai yang benar sesuai factor

## 📝 Catatan Teknis

- **Factor Code:** Diambil dari lower 4 bits D6 (01&0F)
- **Unit:** Diambil dari bit 4 D6 (0=meter, 1=yard)
- **Length:** 3 bytes (D5 D4 D3) × factor
- **Speed:** 2 bytes (D2 D1) × factor
- **Shift:** 1 byte (D0)

## 🎯 Manfaat

1. **Akurasi:** Nilai panjang dan kecepatan sekarang akurat sesuai protokol JSK3588
2. **Konsistensi:** Mengikuti dokumentasi resmi mesin
3. **Reliability:** Mendukung semua factor yang mungkin (×1.0, ×0.1, ×0.01)
4. **Debugging:** Informasi factor ditampilkan di UI untuk memudahkan troubleshooting

---

**Status:** ✅ **FIXED** - Parser sekarang mengikuti protokol JSK3588 yang benar 