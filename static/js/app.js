import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-app.js";
import { getFirestore, collection, query, where, onSnapshot, orderBy } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-firestore.js";

// =========================================================================
// PENTING: GANTI KONFIGURASI INI DENGAN FIREBASE CONFIG MILIK ANDA
// =========================================================================
// Cara mendapatkan: 
// 1. Buka Firebase Console (console.firebase.google.com)
// 2. Pilih Project Anda -> Project Overview -> Project settings (Icon Gear)
// 3. Scroll ke bawah ke bagian "Your apps" (Web app)
// 4. Copy bagian firebaseConfig ke bawah ini.
const firebaseConfig = {
    apiKey: "AIzaSyBfI8bsfOsczfyGKr3Adn8rYKBVmUeveS8",
    authDomain: "valorant-queue-sim.firebaseapp.com",
    projectId: "valorant-queue-sim",
    storageBucket: "valorant-queue-sim.firebasestorage.app",
    messagingSenderId: "660558161945",
    appId: "1:660558161945:web:048aab356ebb3479506288"
};

let app;
let db;

try {
    // Validasi apakah user sudah mengganti config
    if (firebaseConfig.apiKey.includes("GANTI_DENGAN")) {
        console.warn("PERINGATAN: Anda belum mengganti Firebase Config di file static/js/app.js!");
    } else {
        app = initializeApp(firebaseConfig);
        db = getFirestore(app);
        console.log("Firebase Frontend Initialized Successfully");
    }
} catch (e) {
    console.error("Firebase Initialization Error:", e);
}

// =========================================================================
// LOGIC REALTIME UPDATE UNTUK QUEUE
// =========================================================================
document.addEventListener("DOMContentLoaded", () => {
    const queueTableBody = document.getElementById("queueTableBody");
    const queueCount = document.getElementById("queueCount");
    const queueProgressBar = document.getElementById("queueProgressBar");
    
    // Pastikan kita berada di halaman queue dan DB sudah inisialisasi
    if (queueTableBody && db) {
        // Query untuk mengambil player dengan status 'waiting' diurutkan berdasarkan join_time (FIFO)
        const q = query(
            collection(db, "queue"), 
            where("status", "==", "waiting"),
            orderBy("join_time", "asc")
        );

        // onSnapshot digunakan untuk Realtime Update dari Firestore
        onSnapshot(q, (snapshot) => {
            queueTableBody.innerHTML = "";
            let count = 0;
            
            snapshot.forEach((doc) => {
                count++;
                const data = doc.data();
                const row = `
                    <tr>
                        <td class="fw-bold text-muted">${count}</td>
                        <td class="fw-bold text-white"><i class="fas fa-user-circle me-2 text-primary-val"></i>${data.username}</td>
                        <td><span class="badge bg-secondary px-2 py-1">${data.rank}</span></td>
                        <td><span class="text-warning fw-bold small"><i class="fas fa-circle-notch fa-spin me-2"></i> ${data.status.toUpperCase()}</span></td>
                    </tr>
                `;
                queueTableBody.innerHTML += row;
            });

            if (count === 0) {
                queueTableBody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center text-muted py-5">
                            <i class="fas fa-ghost fa-2x mb-3 d-block"></i>
                            Tidak ada player di dalam antrian saat ini.
                        </td>
                    </tr>
                `;
            }

            // Update UI Counters
            queueCount.innerText = `${count}/10`;
            const percentage = (count / 10) * 100;
            queueProgressBar.style.width = `${percentage}%`;
            
            // Logika Visual saat Queue Penuh
            if(count >= 10) {
                queueProgressBar.classList.remove('bg-primary-val');
                queueProgressBar.classList.add('bg-success');
                queueCount.classList.remove('bg-danger');
                queueCount.classList.add('bg-success');
                
                // Animasi redirect saat match terbentuk
                queueTableBody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center text-success py-5 fw-bold">
                            <i class="fas fa-check-circle fa-2x mb-3 d-block"></i>
                            MATCH DITEMUKAN! MENGALIHKAN KE MATCH HISTORY...
                        </td>
                    </tr>
                `;

                // Redirect otomatis setelah 2 detik
                setTimeout(() => {
                    window.location.href = '/history';
                }, 2000);
            } else {
                queueProgressBar.classList.add('bg-primary-val');
                queueProgressBar.classList.remove('bg-success');
                queueCount.classList.add('bg-danger');
                queueCount.classList.remove('bg-success');
            }
        }, (error) => {
            console.error("Error fetching realtime data:", error);
            if(error.code === 'permission-denied') {
                queueTableBody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center text-danger py-5">
                            <i class="fas fa-lock fa-2x mb-3 d-block"></i>
                            <strong>Akses Ditolak (Permission Denied).</strong><br>
                            Pastikan Rules Firestore Anda mengizinkan operasi read/write.<br>
                            (Lihat README.md untuk konfigurasi Rules Firestore)
                        </td>
                    </tr>
                `;
            }
        });
    } else if (queueTableBody && !db) {
        queueTableBody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger py-5">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3 d-block"></i>
                    <strong>Firebase Belum Dikonfigurasi!</strong><br>
                    Silakan ganti firebaseConfig di file <code>static/js/app.js</code> dengan config milik Anda.
                </td>
            </tr>
        `;
    }
});
