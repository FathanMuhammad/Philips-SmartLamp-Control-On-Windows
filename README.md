# Philips WiZ Control on Windows

<img width="462" height="722" alt="Image" src="https://github.com/user-attachments/assets/d6927dbd-afe9-4a4a-9d16-1b09f2fd88a0" />

## Deskripsi

Aplikasi ini memungkinkan pengguna mengontrol lampu Philips WiZ langsung dari PC atau laptop berbasis Windows.
Dibangun menggunakan Python dengan antarmuka grafis Tkinter, aplikasi ini dapat digunakan untuk:

- Menyalakan dan mematikan lampu.
- Mengatur tingkat kecerahan (brightness).
- Mengubah suhu warna (color temperature/Kelvin).
- Mengontrol warna RGB melalui slider interaktif.
- Menampilkan status lampu secara real-time.

Aplikasi ini berkomunikasi dengan lampu melalui UDP broadcast pada jaringan lokal.

## Features

- Deteksi otomatis perangkat Philips WiZ pada jaringan.
- Kontrol daya ON/OFF.
- Slider untuk mengatur brightness.
- Slider untuk mengubah suhu warna (2000K–6500K).
- Slider warna berbasis Hue untuk mengatur RGB.
- Tampilan status lampu (nyala/mati, brightness, suhu warna, RGB).

## Instalasi dan Cara Penggunaan

1. Pastikan PC/laptop terhubung ke jaringan Wi-Fi yang sama dengan lampu Philips WiZ

2. Clone repository ini:

    ```sh
    git clone https://github.com/FathanMuhammad/Philips-SmartLamp-Control-On-Windows.git
    cd philips-wiz-control

    ```

3. alankan aplikasi menggunakan Python 3:

    ```sh
    python wiz_control.py
    ```

4. GUI akan terbuka.

    - Gunakan tombol ON/OFF untuk menyalakan atau mematikan lampu.
    - Atur brightness menggunakan slider.
    - Ubah suhu warna dengan slider Kelvin.
    - Pilih warna RGB melalui slider Hue.
    
## License
Proyek ini dibuat untuk tujuan pembelajaran dan pengembangan pribadi.
