import random
import csv
import os

# Direktori untuk menyimpan data mentah
raw_data_dir = 'data/raw'
os.makedirs(raw_data_dir, exist_ok=True)  # Membuat direktori jika belum ada

def generate_donor_data(num_donors):
    """
    Fungsi untuk membuat data penyumbang.

    Args:
        num_donors (int): Jumlah penyumbang yang akan dibuat.

    Returns:
        list: Data penyumbang dalam bentuk list of lists.
    """
    donor_data = []

    for i in range(num_donors):
        donor_id = f"D{i+1}"
        jenis_makanan = random.choice(['makanan', 'minuman', 'makanan_minuman'])
        jumlah_disumbangkan = random.randint(1, 50)
        lokasi_lat_penyumbang = random.uniform(-5.405901634725342, -5.365442970161212) # Koordinat dibatasi pada area Kota Bandar Lampung
        lokasi_lon_penyumbang = random.uniform(105.22551998740258, 105.29009985878861)
        kondisi_makanan = random.choice(['layak_konsumsi', 'hampir_kadaluarsa', 'tidak_layak_konsumsi'])

        # Menentukan properti tambahan berdasarkan kondisi makanan
        if kondisi_makanan == 'tidak_layak_konsumsi':
            is_halal_donor = False
            is_for_child_donor = False
            is_for_elderly_donor = False
            is_alergan = True
        else:
            is_halal_donor = random.choice([True, False])
            is_for_child_donor = random.choice([True, False])
            is_for_elderly_donor = random.choice([True, False])
            is_alergan = random.choice([True, False])

        donor_data.append([
            donor_id,
            jenis_makanan,
            jumlah_disumbangkan,
            lokasi_lat_penyumbang,
            lokasi_lon_penyumbang,
            kondisi_makanan,
            is_halal_donor,
            is_for_child_donor,
            is_for_elderly_donor,
            is_alergan
        ])

    return donor_data

def generate_receiver_data(num_receivers):
    """
    Fungsi untuk membuat data penerima.

    Args:
        num_receivers (int): Jumlah penerima yang akan dibuat.

    Returns:
        list: Data penerima dalam bentuk list of lists.
    """
    receiver_data = []

    for i in range(num_receivers):
        receiver_id = f"T{i+1}"
        makanan_dibutuhkan = random.choice(['makanan', 'minuman', 'makanan_minuman'])
        jumlah_dibutuhkan = random.randint(1, 50)
        lokasi_lat_penerima = random.uniform(-5.405901634725342, -5.365442970161212)
        lokasi_lon_penerima = random.uniform(105.22551998740258, 105.29009985878861)
        frekuensi_menerima = random.randint(1, 10)
        kondisi_makanan_diterima = random.choice([
            'layak_konsumsi',
            'hampir_kadaluarsa',
            'tidak_layak_konsumsi',
            'layak_konsumsi_hampir_kadaluarsa'
        ])

        # Menentukan properti tambahan berdasarkan kondisi makanan yang diterima
        if 'tidak_layak_konsumsi' in kondisi_makanan_diterima:
            is_halal_receiver = False
            is_for_child_receiver = False
            is_for_elderly_receiver = False
            is_alergan_free = False
        else:
            is_halal_receiver = random.choice([True, False])
            is_for_child_receiver = random.choice([True, False])
            is_for_elderly_receiver = random.choice([True, False])
            is_alergan_free = random.choice([True, False])

        status_penerima = random.choice(['mendesak', 'normal', 'tidak_mendesak'])

        receiver_data.append([
            receiver_id,
            makanan_dibutuhkan,
            jumlah_dibutuhkan,
            lokasi_lat_penerima,
            lokasi_lon_penerima,
            frekuensi_menerima,
            kondisi_makanan_diterima,
            is_halal_receiver,
            is_for_child_receiver,
            is_for_elderly_receiver,
            is_alergan_free,
            status_penerima
        ])

    return receiver_data

# Membuat data penyumbang dan penerima
num_donors = 100
num_receivers = 100

donor_data = generate_donor_data(num_donors)
receiver_data = generate_receiver_data(num_receivers)

# Menyimpan data penyumbang ke file CSV
with open(os.path.join(raw_data_dir, 'data_donor.csv'), 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'id_penyumbang', 'makanan_disumbangkan', 'jumlah_disumbangkan', 
        'lokasi_lat_penyumbang', 'lokasi_lon_penyumbang', 'kondisi_makanan', 
        'is_halal_donor', 'is_for_child_donor', 'is_for_elderly_donor', 'is_alergan'
    ])
    writer.writerows(donor_data)

# Menyimpan data penerima ke file CSV
with open(os.path.join(raw_data_dir, 'data_penerima.csv'), 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'id_penerima', 'makanan_dibutuhkan', 'jumlah_dibutuhkan', 
        'lokasi_lat_penerima', 'lokasi_lon_penerima', 'frekuensi_menerima', 
        'kondisi_makanan_diterima', 'is_halal_receiver', 'is_for_child_receiver', 'is_for_elderly_receiver', 
        'is_alergan_free', 'status_penerima'
    ])
    writer.writerows(receiver_data)

print("Dataset berhasil digenerate dan disimpan di folder 'data/raw'!")
