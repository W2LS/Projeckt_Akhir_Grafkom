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
- Atur ketebalan garis dengan tombol + dan -

### 🛠️ Transformasi Geometri
- Translasi: tekan T  
- Rotasi: tekan Y  
- Skala: tekan U  
🔁 Gunakan **arrow keys, Z/X, atau N/M** untuk mengubah posisi, rotasi, dan ukuran.

### 🪟 Windowing & Clipping
- Tekan Q untuk atur window dengan klik 2 titik (sebagai batas)
- Geser window: tombol W, A, S, D
- Objek:
  - Di dalam window akan berubah warna menjadi **hijau**
  - Di luar window akan **terklip otomatis** menggunakan algoritma **Cohen-Sutherland**

### 🔄 Fitur Tambahan
- Hapus semua objek: Delete  
- Batalkan transformasi: C  
- Keluar dari aplikasi: Esc

---

## 📄 Modul B – Grafika 3D Interaktif dengan PyOpenGL

### 📌 Deskripsi
Program ini menampilkan objek **3D (Kubus)** dengan pencahayaan, rotasi, serta interaksi kamera.  
Modul ini menunjukkan implementasi dasar 3D menggunakan **gluPerspective**, **gluLookAt**, dan pencahayaan.

---

## 🎯 Fitur-Fitur Utama

### 🧊 Objek 3D
- Menampilkan **Kubus 3D** secara interaktif

### 💡 Pencahayaan
- Implementasi 3 jenis pencahayaan:
  - **Ambient Light** – Cahaya menyeluruh
  - **Diffuse Light** – Cahaya menyebar dari sumber tertentu
  - **Specular Light** – Cahaya pantulan (kilau/glossy)

### 🎥 Kamera & Perspektif
- Kamera diatur menggunakan gluLookAt untuk melihat objek dari sudut menyerong
- Proyeksi menggunakan gluPerspective untuk menciptakan efek kedalaman (depth)

### 🎮 Interaksi 3D
- Rotasi objek: tombol Arrow  
- Zoom: tombol + dan -  
- Reset kamera: tekan R  
- Keluar dari aplikasi: Esc

---

## 🚀 Cara Menjalankan

```bash
pip install PyOpenGL PyOpenGL_accelerate pygame
pip install numpy pandas scikit-learn
pip install seaborn
python 2d.py
python 3d.py
