# 🖥️ Tugas Besar UAS Grafika Komputer – PyOpenGL

Repo ini merupakan hasil **Tugas Besar UAS Mata Kuliah Grafika Komputer** dengan tema:  
**“Pengembangan Aplikasi Grafika 2D dan 3D Interaktif Menggunakan PyOpenGL”**.

Aplikasi dibangun menggunakan **Python**, **PyOpenGL**, dan **Pygame**, serta mendemonstrasikan berbagai fitur dasar dan lanjutan dalam grafika komputer, baik untuk objek **2D** maupun **3D**.

---

## 📄 Modul A – Grafika 2D Interaktif dengan PyOpenGL

### 📌 Deskripsi
Program ini merupakan bagian dari tugas besar UAS mata kuliah Grafika Komputer.  
Aplikasi 2D ini memungkinkan pengguna untuk menggambar objek grafika dasar serta menerapkan transformasi dan teknik clipping secara interaktif.

---

## 🎯 Fitur-Fitur Utama

### ✅ Gambar Objek 2D
- Titik  
- Garis  
- Persegi  
- Ellipse  
📍 Input koordinat dilakukan dengan klik mouse.

### 🎨 Warna & Ketebalan
- Pilih warna objek: **Merah (R)**, **Hijau (G)**, **Biru (B)**
- Atur ketebalan garis dengan tombol `+` dan `-`

### 🛠️ Transformasi Geometri
- Translasi: tekan `T`  
- Rotasi: tekan `Y`  
- Skala: tekan `U`  
🔁 Gunakan **arrow keys, Z/X, atau N/M** untuk mengubah posisi, rotasi, dan ukuran.

### 🪟 Windowing & Clipping
- Tekan `Q` untuk atur window dengan klik 2 titik (sebagai batas)
- Geser window: tombol `W`, `A`, `S`, `D`
- Objek:
  - Di dalam window akan berubah warna menjadi **hijau**
  - Di luar window akan **terklip otomatis** menggunakan algoritma **Cohen-Sutherland**

### 🔄 Fitur Tambahan
- Hapus semua objek: `Delete`  
- Batalkan transformasi: `C`  
- Keluar dari aplikasi: `Esc`

---

## 🚀 Cara Menjalankan

```bash
pip install PyOpenGL PyOpenGL_accelerate pygame
python 2d.py
