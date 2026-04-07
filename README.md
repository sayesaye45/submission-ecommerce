Proyek Analisis Data: Brazilian E-Commerce Public Dataset

Tentang Proyek

Proyek ini merupakan analisis data dari Brazilian E-Commerce Public Dataset by Olist yang tersedia di Kaggle. Dataset berisi data transaksi pelanggan, order, produk, pembayaran, dan wilayah pelanggan. Analisis dilakukan untuk menjawab pertanyaan bisnis terkait tren penjualan, distribusi geografis pelanggan, dan segmentasi pelanggan menggunakan metode RFM Analysis.

Pertanyaan Bisnis



1. Bagaimana tren penjualan bulanan dan kategori produk apa yang paling banyak terjual selama periode 2016–2018?

2\. Bagaimana distribusi geografis pelanggan di seluruh Brasil, dan kota/negara bagian mana yang memiliki volume order terbanyak selama periode 2016–2018?

3\. Bagaimana segmentasi pelanggan berdasarkan perilaku pembelian mereka menggunakan metode RFM Analysis selama periode 2016–2018, dan strategi apa yang tepat untuk setiap segmen?



Setup Environment - Anaconda

conda create --name main-ds python=3.9

conda activate main-ds

pip install -r requirements.txt



Setup Environment - Shell/Terminal

mkdir proyek\_analisis\_data

cd proyek\_analisis\_data

pipenv install

pipenv shell

pip install -r requirements.txt

Run Streamlit App

streamlit run dashboard/dashboard.py



Link Dashboard

https://ecommerce-dashboard-sayesaye45.streamlit.app/



Identitas

Nama: Kurnia Irianti

Email: kurniairianti21@gmail.com

ID Dicoding: cdcc228d6x2404

