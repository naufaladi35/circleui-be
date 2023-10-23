# PPL Hub - Circle.UI - Backend

- Production server: [https://circleui-api.herokuapp.com/docs](https://circleui-api.herokuapp.com/docs)
- Staging server: [https://circleui-api-dev.herokuapp.com/docs](https://circleui-api-dev.herokuapp.com/docs)

| Production (prod) | Staging (dev) |
| :---         | :---    |
|[![pipeline status](https://gitlab.cs.ui.ac.id/ppl-fasilkom-ui/2022/Kelas-B/PPL-hub/circleui-be/badges/prod/pipeline.svg)](https://gitlab.cs.ui.ac.id/ppl-fasilkom-ui/2022/Kelas-B/PPL-hub/circleui-be/-/commits/prod)|[![pipeline status](https://gitlab.cs.ui.ac.id/ppl-fasilkom-ui/2022/Kelas-B/PPL-hub/circleui-be/badges/dev/pipeline.svg)](https://gitlab.cs.ui.ac.id/ppl-fasilkom-ui/2022/Kelas-B/PPL-hub/circleui-be/-/commits/dev) |
|[![coverage report](https://gitlab.cs.ui.ac.id/ppl-fasilkom-ui/2022/Kelas-B/PPL-hub/circleui-be/badges/prod/coverage.svg)](https://gitlab.cs.ui.ac.id/ppl-fasilkom-ui/2022/Kelas-B/PPL-hub/circleui-be/-/commits/prod)|[![coverage report](https://gitlab.cs.ui.ac.id/ppl-fasilkom-ui/2022/Kelas-B/PPL-hub/circleui-be/badges/dev/coverage.svg)](https://gitlab.cs.ui.ac.id/ppl-fasilkom-ui/2022/Kelas-B/PPL-hub/circleui-be/-/commits/dev)

### Kontributor
* 1906400103 - Muhammad Hazim Al Farouq
* 1906293184 - Muhammad Faisal Adi Soesatyo
* 1906398540 - Ahmadar Rafi Moreno
* 1906305871 - Naufal Adi Wijanarko
* 1906400293 - Faris Sayidinarechan Ardhafa
* 1906400135 - Haidar Labib Bangsawijaya
* 1906400223 - Faris Muzhaffar

### Kebutuhan
* Python
* Python venv
* pip
* Semua package yang ada di requirements.txt

### Deskripsi App
Circle.UI adalah aplikasi sosial media yang eksklusif hanya untuk mahasiswa UI dimana user 
dapat membuat community di dalam platform tersebut, join ke suatu community, berinteraksi dengan 
user lain pada community yang dia ikuti, mempromosikan event, dan menyimpan event yang dia minati.

### Instalasi
Untuk istalasi proyek ini, jalankan command berikut:
```
git clone https://gitlab.cs.ui.ac.id/ppl-fasilkom-ui/2022/Kelas-B/PPL-hub/circleui-be.git
```
Ganti working directory ke repository yang baru saja di clone dengan command:
```
cd circleui-be
```
Buat sebuah folder environment dan jalankan environment untuk mengisolate instalasi kebutuhan dengan command:
```
python -m venv env
env\Scripts\activate
```
Lalu, install semua kebutuhan yang ada di dalam requirements.txt:
```
pip install -r requirements.txt
```

### Cara menjalankan
Setelah selesai instalasi, jalankan perintah untuk mulai menjalankan server di local komputer anda
```
uvicorn app:app --reload
```
