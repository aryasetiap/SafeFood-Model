import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# Fungsi untuk menghitung jarak menggunakan formula Haversine
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    r = 6371  # Radius bumi dalam kilometer
    return r * c

# Fungsi untuk menghitung skor kecocokan antara donor dan penerima
def calculate_matching_score(donor, receiver):
    score = 0

    # Bobot untuk masing-masing kriteria
    weights = {
        'makanan_disumbangkan': 0.2,
        'kondisi_makanan': 0.15,
        'jumlah_disumbangkan': 0.1,
        'is_halal': 0.1,
        'is_for_child_and_elderly': 0.1,
        'is_alergan': 0.1,
        'status_penerima': 0.1,
        'frekuensi_menerima': 0.075,
        'lokasi': 0.075
    }

    # Penilaian jenis makanan yang disumbangkan
    if donor['makanan_disumbangkan'] == receiver['makanan_dibutuhkan']:
        score += 1 * weights['makanan_disumbangkan']
    elif (donor['makanan_disumbangkan'] == 'makanan' and receiver['makanan_dibutuhkan'] == 'makanan_minuman') or \
         (donor['makanan_disumbangkan'] == 'minuman' and receiver['makanan_dibutuhkan'] == 'makanan_minuman'):
        score += 1 * weights['makanan_disumbangkan']
    elif donor['makanan_disumbangkan'] == 'makanan_minuman' and receiver['makanan_dibutuhkan'] in ['makanan', 'minuman']:
        score += 0.5 * weights['makanan_disumbangkan']

    # Penilaian kondisi makanan
    if donor['kondisi_makanan'] == receiver['kondisi_makanan_diterima']:
        score += 1 * weights['kondisi_makanan']
    elif (donor['kondisi_makanan'] == 'layak_konsumsi' and receiver['kondisi_makanan_diterima'] in ['hampir_kadaluarsa', 'layak_konsumsi_hampir_kadaluarsa']) or \
         (donor['kondisi_makanan'] == 'hampir_kadaluarsa' and receiver['kondisi_makanan_diterima'] in ['layak_konsumsi', 'layak_konsumsi_hampir_kadaluarsa']):
        score += 0.5 * weights['kondisi_makanan']
    elif donor['kondisi_makanan'] == 'tidak_layak_konsumsi' and receiver['kondisi_makanan_diterima'] == 'tidak_layak_konsumsi':
        score += 1 * weights['kondisi_makanan']

    # Penilaian jumlah makanan yang disumbangkan
    if donor['jumlah_disumbangkan'] >= receiver['jumlah_dibutuhkan']:
        score += 1 * weights['jumlah_disumbangkan']
    else:
        score += (donor['jumlah_disumbangkan'] / receiver['jumlah_dibutuhkan']) * weights['jumlah_disumbangkan']

    # Penilaian status halal
    if donor['is_halal_donor'] == receiver['is_halal_receiver']:
        score += 1 * weights['is_halal']
    elif donor['is_halal_donor'] == 1 and receiver['is_halal_receiver'] == 0:
        score += 1 * weights['is_halal']

    # Penilaian penerima berdasarkan kategori usia
    if donor['is_for_child_donor'] == receiver['is_for_child_receiver'] and donor['is_for_elderly_donor'] == receiver['is_for_elderly_receiver']:
        score += 1 * weights['is_for_child_and_elderly']

    # Penilaian alergi makanan
    if donor['is_alergan'] == 0 or receiver['is_alergan_free'] == 1:
        score += 1 * weights['is_alergan']

    # Penilaian status penerima
    if receiver['status_penerima'] == 'mendesak':
        score += 1 * weights['status_penerima']
    elif receiver['status_penerima'] == 'normal':
        score += 0.5 * weights['status_penerima']

    # Penilaian frekuensi penerimaan bantuan
    score += (1 / (receiver['frekuensi_menerima'] + 1)) * weights['frekuensi_menerima']

    # Penilaian jarak antara donor dan penerima
    distance = haversine(donor['lokasi_lat_penyumbang'], donor['lokasi_lon_penyumbang'], receiver['lokasi_lat_penerima'], receiver['lokasi_lon_penerima'])
    if distance <= 3.5:
        score += 1 * weights['lokasi']

    return score

# Fungsi untuk menggabungkan data donor dan penerima serta menghitung skor kecocokan
def merge_and_calculate_scores(donor_df, receiver_df):
    combined_data = []

    # Iterasi melalui setiap pasangan donor dan penerima
    for _, donor in donor_df.iterrows():
        for _, receiver in receiver_df.iterrows():
            score = calculate_matching_score(donor, receiver)

            # Gabungkan data donor, penerima, dan skor kecocokan
            combined_entry = {
                **donor.to_dict(),
                **receiver.to_dict(),
                'matching_score': score,
            }
            combined_data.append(combined_entry)

    return combined_data

# Membaca data donor dan penerima dari file CSV
donor_df = pd.read_csv('data/raw/data_donor.csv')
receiver_df = pd.read_csv('data/raw/data_penerima.csv')

# Menghitung data matching dan mengacak urutan data
matching_data = merge_and_calculate_scores(donor_df, receiver_df)
matching_df = pd.DataFrame(matching_data)
matching_df = matching_df.sample(frac=1).reset_index(drop=True)

# Menyimpan hasil matching ke file CSV
matching_df.to_csv('data/raw/data_donor_recipient_matching.csv', index=False)
