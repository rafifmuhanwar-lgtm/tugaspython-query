# Valorant Matchmaking Simulator

Aplikasi web fullstack untuk mensimulasikan sistem matchmaking game online (seperti Valorant) menggunakan struktur data **Queue (FIFO)**.

## Fitur Utama
1. **Login & Register** dengan Firestore.
2. **Dashboard** dengan statistik aplikasi.
3. **Queue System**: Implementasi Queue First-In-First-Out (FIFO). Jika queue mencapai 10 orang, sistem otomatis membaginya menjadi Tim Attacker dan Defender.
4. **Realtime Updates**: Antrian update secara realtime menggunakan Firebase Firestore OnSnapshot.
5. **Match History**: Riwayat pertandingan yang telah dibuat.
6. **UI/UX Valorant Style**: Dark mode, glassmorphism, accent neon red.

---

## Prasyarat
- Python 3.8 atau lebih baru
- Akun Firebase (Google)

## Langkah Instalasi

1. **Clone / Buka Folder Project**
   Pastikan Anda berada di direktori `ValorantMatchmaking`.

2. **Buat Virtual Environment (Opsional tapi disarankan)**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependensi**
   Buka terminal, jalankan perintah ini:
   ```bash
   pip install flask firebase-admin werkzeug
   ```

## Konfigurasi Firebase (PENTING!)

Aplikasi ini menggunakan Firebase di dua sisi: Backend (Python) dan Frontend (JavaScript). Keduanya wajib di-setup.

### A. Setup Firebase Project & Database
1. Buka [Firebase Console](https://console.firebase.google.com/).
2. Buat project baru (misal: `valorant-queue-sim`).
3. Di menu kiri, pilih **Firestore Database** -> klik **Create database**.
4. Pilih lokasi terdekat, lalu klik Next.
5. Masuk ke tab **Rules** (Aturan) di Firestore. Ganti `false` menjadi `true` untuk testing (Hati-hati untuk production):
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /{document=**} {
         allow read, write: if true;
       }
     }
   }
   ```
   *Klik Publish*.

### B. Konfigurasi Backend (Python)
1. Di Firebase Console, klik icon **Gear** (Project settings) di pojok kiri atas.
2. Pindah ke tab **Service accounts**.
3. Di bagian Firebase Admin SDK, pilih **Python**.
4. Klik **Generate new private key**. File `.json` akan terdownload.
5. **GANTI NAMA** file yang didownload menjadi `serviceAccountKey.json`.
6. **PINDAHKAN** file tersebut ke dalam folder `backend/` pada project ini. 
   *(Path: `ValorantMatchmaking/backend/serviceAccountKey.json`)*

### C. Konfigurasi Frontend (JavaScript)
1. Kembali ke Project settings (Icon Gear).
2. Di tab **General**, scroll ke bawah ke bagian **Your apps**.
3. Klik icon **Web** (`</>`) untuk menambahkan aplikasi web. Beri nama aplikasi, klik **Register app**.
4. Akan muncul `firebaseConfig`. Copy blok kode konfigurasi tersebut.
5. Buka file `ValorantMatchmaking/static/js/app.js`.
6. Cari variabel `firebaseConfig` di baris atas, dan GANTI isinya dengan config milik Anda yang baru dicopy.

---

## Cara Menjalankan Aplikasi

1. Buka terminal, pastikan berada di dalam folder `ValorantMatchmaking`.
2. Jalankan aplikasi Flask:
   ```bash
   python backend/app.py
   ```
3. Buka browser dan akses alamat:
   ```
   http://127.0.0.1:5000
   ```
4. Selesai! Anda bisa mendaftar akun dan mulai bergabung ke dalam Queue.

---

## Logika Queue (FIFO)
Terdapat pada file `backend/matchmaking.py`. 
Setiap kali ada user yang Join Queue:
1. Data masuk ke Firestore collection `queue`.
2. Backend menarik data queue berstatus `waiting` diurutkan dari `join_time` terlama ke terbaru (FIFO), di-limit 10.
3. Jika jumlah mencapai 10, sistem membagi array menjadi index 0-4 (Attacker) dan 5-9 (Defender).
4. Menyimpan data ke collection `matches` dan menghapus ke-10 player dari `queue`.
