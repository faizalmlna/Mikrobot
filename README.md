mikrotik-bot adalah sebuah proyek yang dikembangkan untuk membantu memantau dan mengecek konektivitas jaringan pada infrastruktur yang tersebar di berbagai site. Proyek ini dikembangkan bersama tim untuk memastikan kestabilan koneksi antar endpoint di data center (DC) dan disaster recovery center (DRC), serta melakukan berbagai tugas pemantauan lainnya.
ada beberapa fitur yang kita buat pada mikrobot ini yang 
Fitur pengecekan koneksi antar site
1. mengecek koneksi antara aws, site lunox, site gatot kearah endpoint di DC/DRC
2. mengecek koneksi antara aws, site lunox, site gatot kearah server Nginx DC/DRC

Fitur pengecekan di DC dan DRC
1. pengecekan/pemantauan koneksi ke internet
2. block ip public yang tidak dikenal ke arah server Nginx DC/DRC
3. pemantauan BGP Interconnect seperti pengecekan established dan status uptime
4. pengecekan kearah database

saya menggunakan beberapa library Python berikut untuk mempermudah pengembangan:
1. python-telegram-bot untuk integrasi bot Telegram dan pengiriman notifikasi.
2. Paramiko untuk melakukan koneksi SSH ke MikroTik.
3. os untuk manajemen environment dan file system.
4. Requests untuk HTTP requests, seperti pengambilan data API.

Project ini dikemas menggunakan Docker Compose, sehingga dapat dengan mudah di-deploy di berbagai sistem operasi tanpa mengkhawatirkan ketergantungan library. dengan catatan telah menginstall docker dan docker compose.
