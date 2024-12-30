import streamlit as st
import pandas as pd
import tensorflow as tf
import numpy as np

# Memuat model Keras yang telah disimpan
model = tf.keras.models.load_model('../models/safe_food_model.keras')

# Fungsi untuk memprediksi skor pencocokan berdasarkan input data
def predict_matching_score(input_data):
    input_data = np.array(input_data)  # Konversi input menjadi array numpy
    prediction = model.predict(input_data)  # Lakukan prediksi dengan model
    return prediction

# Fungsi untuk menghitung jarak antara dua koordinat menggunakan rumus Haversine
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])  # Mengubah derajat ke radian
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))  # Menyelesaikan rumus Haversine
    r = 6371  # Radius bumi dalam kilometer
    return c * r  # Mengembalikan jarak dalam kilometer

# Membaca data penerima dari file CSV
data_penerima = pd.read_csv('../data/raw/data_penerima.csv')

# Judul aplikasi Streamlit
st.title('Evaluasi Pencocokan Makanan Donasi')

# Header inputan untuk jenis makanan yang disumbangkan
st.header('Masukkan Makanan yang Disumbangkan')

# Inputan dari pengguna mengenai informasi penyumbang
id_penyumbang = st.text_input('ID Penyumbang')
makanan_disumbangkan = st.selectbox('Jenis Makanan Disumbangkan?', ['Makanan', 'Minuman', 'Makanan dan Minuman'])
jumlah_disumbangkan = st.number_input('Jumlah Makanan yang Disumbangkan', step=1)
lokasi_lat_penyumbang = st.number_input('Latitude Lokasi Penyumbang', format="%.16f", step=0.0000000000000001)
lokasi_lon_penyumbang = st.number_input('Longitude Lokasi Penyumbang', format="%.14f", step=0.00000000000001)
kondisi_makanan = st.selectbox('Kondisi Makanan yang Disumbangkan?', ['Layak Konsumsi', 'Hampir Kadaluarsa', 'Tidak Layak Konsumsi'])
is_halal_donor = st.selectbox('Makanan Halal?', ['Ya', 'Tidak'])
is_for_child_donor = st.selectbox('Untuk Anak?', ['Ya', 'Tidak']) 
is_for_elderly_donor = st.selectbox('Untuk Lansia?', ['Ya', 'Tidak'])
is_alergan = st.selectbox('Mengandung Alergen?', ['Ya', 'Tidak'])

# Tombol untuk memulai prediksi
if st.button('Prediksi Matching Score'):
    input_for_model = []  # Menyimpan input untuk model
    id_penerima_list = []  # Menyimpan ID penerima

    # Iterasi melalui setiap baris data penerima untuk mempersiapkan input model
    for _, row in data_penerima.iterrows():
        id_penerima_list.append(row['id_penerima'])
        # Menyusun data input untuk model berdasarkan input penyumbang dan data penerima
        data_row = [
            jumlah_disumbangkan,
            0 if is_halal_donor == 'Tidak' else 1,
            0 if is_for_child_donor == 'Tidak' else 1,
            0 if is_for_elderly_donor == 'Tidak' else 1,
            0 if is_alergan == 'Tidak' else 1,
            row['jumlah_dibutuhkan'],
            row['frekuensi_menerima'],
            1 if row['is_halal_receiver'] else 0,
            1 if row['is_for_child_receiver'] else 0,
            1 if row['is_for_elderly_receiver'] else 0,
            1 if row['is_alergan_free'] else 0,
            1 if makanan_disumbangkan == 'Makanan' else 0,
            1 if makanan_disumbangkan == 'Makanan dan Minuman' else 0,
            1 if makanan_disumbangkan == 'Minuman' else 0,
            1 if kondisi_makanan == 'Hampir Kadaluarsa' else 0,
            1 if kondisi_makanan == 'Layak Konsumsi' else 0,
            1 if kondisi_makanan == 'Tidak Layak Konsumsi' else 0,
            1 if row['makanan_dibutuhkan'] == 'makanan' else 0,
            1 if row['makanan_dibutuhkan'] == 'makanan_minuman' else 0,
            1 if row['makanan_dibutuhkan'] == 'minuman' else 0,
            1 if row['kondisi_makanan_diterima'] == 'hampir_kadaluarsa' else 0,
            1 if row['kondisi_makanan_diterima'] == 'layak_konsumsi' else 0,
            1 if row['kondisi_makanan_diterima'] == 'layak_konsumsi_hampir_kadaluarsa' else 0,
            1 if row['kondisi_makanan_diterima'] == 'tidak_layak konsumsi' else 0,
            1 if row['status_penerima'] == 'mendesak' else 0,
            1 if row['status_penerima'] == 'normal' else 0,
            1 if row['status_penerima'] == 'tidak mendesak' else 0,
            haversine(lokasi_lat_penyumbang, lokasi_lon_penyumbang, row['lokasi_lat_penerima'], row['lokasi_lon_penerima']),
        ]
        input_for_model.append(data_row)

    # Prediksi menggunakan model yang telah dilatih
    predictions = predict_matching_score(input_for_model)

    # Membuat dataframe hasil prediksi
    result_df = pd.DataFrame({
        'id_penerima': id_penerima_list,
        'predicted_matching_score': predictions.flatten()
    })

    # Mengurutkan berdasarkan predicted_matching_score dan mengambil 15 penerima teratas
    result_df = result_df.sort_values(by='predicted_matching_score', ascending=False).head(15)

    # Menyusun tabel lengkap dengan informasi penerima dan prediksi matching score
    detailed_results = []
    for _, row in result_df.iterrows():
        penerima_detail = data_penerima[data_penerima['id_penerima'] == row['id_penerima']].iloc[0]
        detailed_results.append({
            'id_penerima': row['id_penerima'],
            'predicted_matching_score': row['predicted_matching_score'],
            'jumlah_dibutuhkan': penerima_detail['jumlah_dibutuhkan'],
            'frekuensi_menerima': penerima_detail['frekuensi_menerima'],
            'makanan_dibutuhkan': penerima_detail['makanan_dibutuhkan'],
            'kondisi_makanan_diterima': penerima_detail['kondisi_makanan_diterima'],
            'status_penerima': penerima_detail['status_penerima'],
        })

    # Membuat DataFrame dengan hasil yang lebih lengkap
    detailed_df = pd.DataFrame(detailed_results)

    # Menampilkan tabel lengkap
    st.write("15 Penerima dengan Matching Score Tertinggi dan Detail Lengkap:")
    st.dataframe(detailed_df)
