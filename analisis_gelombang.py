import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Pembersihan Data ---

# Masukkan nama/format file kamu
file_name = 'Lembar_Pengolahan_Data.csv'

try:
    # Baca file csv dan menghilangkan titik koma (;)
    df = pd.read_csv(file_name, delimiter=';', on_bad_lines='skip')

    # Memilah kolom yang mau di pakai
    df = df[['Time', 'Data']]
    df = df.rename(columns={'Time': 'time', 'Data': 'elevation'})

    # --- Pengolahan data waktu ---

    # merubah format waktunya ke detik
    def time_to_seconds(t):
        if isinstance(t, str):
            try:
                minutes, seconds = map(float, t.split(':'))
                return minutes * 60 + seconds
            except ValueError:
                return np.nan
        return np.nan

    # Penggunaan hasil konversi waktunya
    df['time_seconds'] = df['time'].apply(time_to_seconds)

    # Perubahan kolom elevasi
    df['elevation'] = pd.to_numeric(df['elevation'], errors='coerce')

    # Untuk menghapus baris yang kosong datanya
    df = df.dropna(subset=['time_seconds', 'elevation'])

    # Perhitungan rata-rata elevasi
    mean_elevation = df['elevation'].mean()
    df['elevation_centered'] = df['elevation'] - mean_elevation


    # --- Melakukan perhitungan zero-up crossing ---

    # MMencari index yang berhubungan dengan zero-up crossing
    zero_crossings = np.where(np.diff(np.sign(df['elevation_centered'])) > 0)[0]

    # Hasil disimpan
    wave_heights = []
    wave_periods = []

    # Loop tiap gelombang yang ada
    for i in range(len(zero_crossings) - 1):
        start_index = zero_crossings[i]
        end_index = zero_crossings[i+1]
        wave_data = df.iloc[start_index:end_index]

        if not wave_data.empty:
            # Menghitung H gelombang
            crest = wave_data['elevation_centered'].max()
            trough = wave_data['elevation_centered'].min()
            height = crest - trough
            wave_heights.append(height)

            # Menghitung T gelombang
            start_time = df['time_seconds'].iloc[start_index]
            end_time = df['time_seconds'].iloc[end_index]
            period = end_time - start_time
            wave_periods.append(period)

    # Dibuat dataframe untuk penyimpanan
    wave_analysis_df = pd.DataFrame({
        'Tinggi Gelombang (H)': wave_heights,
        'Periode Gelombang (T)': wave_periods
    })

    # --- Output untuk memperlihatkan hasilnya ---

    print("--- Ringkasan Statistik Hasil Analisis ---")
    print(wave_analysis_df.describe())

    # Menyimpan hasil di csv baru
    wave_analysis_df.to_csv('hasil_analisis_gelombang.csv', index=False)
    print("\nHasil analisis telah disimpan ke 'hasil_analisis_gelombang.csv'")


    # --- Plot elevasi ---

    plt.figure(figsize=(15, 6))
    plt.plot(df['time_seconds'], df['elevation_centered'], label='Elevasi Gelombang')
    plt.plot(df['time_seconds'].iloc[zero_crossings], df['elevation_centered'].iloc[zero_crossings], 'ro', label='Zero-Up-Crossings')
    plt.title('Analisis Gelombang dengan Metode Zero-Up-Crossing')
    plt.xlabel('Waktu (detik)')
    plt.ylabel('Elevasi (terpusat)')
    plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
    plt.legend()
    plt.grid(True)
    plt.savefig('plot_analisis_gelombang.png')
    print("Plot visualisasi telah disimpan ke 'plot_analisis_gelombang.png'")


except FileNotFoundError:
    print(f"Error: File '{file_name}' tidak ditemukan. Mohon pastikan file berada di direktori yang sama dengan skrip.")
except Exception as e:
    print(f"Terjadi error: {e}")