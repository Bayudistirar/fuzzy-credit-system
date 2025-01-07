# Fuzzy Credit Analysis System

Implementasi sistem pendukung keputusan kelayakan kredit menggunakan Fuzzy Sugeno. Sistem ini mengevaluasi 5 kriteria (Character, Capital, Capacity, Collateral, Condition) dengan 48 rules untuk menghasilkan rekomendasi penerimaan kredit.

## ⭐ Features
- Evaluasi kelayakan kredit berbasis prinsip 5C:
  - Character (karakter nasabah)
  - Capital (modal)
  - Capacity (kemampuan membayar)
  - Collateral (jaminan)
  - Condition (kondisi ekonomi)
- Implementasi 48 fuzzy rules untuk analisis komprehensif
- Visualisasi hasil menggunakan radar chart
- Interface web interaktif menggunakan Streamlit
- Perhitungan detail proses fuzzy
- Defuzzifikasi menggunakan weighted average method

## 🛠️ Technologies Used
- Python 3.x
- Streamlit for web interface
- Pandas for data handling
- Plotly for interactive visualizations

## 📥 Installation

1. Clone repository ini:
```bash
git clone https://github.com/Bayudistrar/fuzzy-credit-analysis.git
```

2. Masuk ke direktori proyek:
```bash
cd fuzzy-credit-analysis
```

3. Install dependensi yang diperlukan:
```bash
pip install streamlit pandas plotly
```

## 💻 Usage

Jalankan aplikasi dengan perintah:
```bash
streamlit run data.py
```

Sistem akan berjalan pada browser default Anda dengan tampilan:
1. Input panel untuk memasukkan nilai 5C
2. Tombol evaluasi untuk memproses input
3. Hasil analisis dengan visualisasi
4. Perhitungan detail proses fuzzy

## 🔧 System Components

### Input Variables
- **Character**: Evaluasi kepribadian dan tanggung jawab
- **Capital**: Evaluasi kekuatan finansial
- **Capacity**: Evaluasi kemampuan membayar
- **Collateral**: Evaluasi jaminan
- **Condition**: Evaluasi kondisi ekonomi

### Output
- Keputusan: DITERIMA/DITOLAK
- Nilai defuzzifikasi (0-1)
- Visualisasi radar chart
- Detail perhitungan fuzzy

## 🤝 Contributing

Kontribusi selalu diterima. Untuk berkontribusi:

1. Fork repository
2. Buat branch baru (`git checkout -b feature/improvement`)
3. Commit perubahan (`git commit -m 'Add new feature'`)
4. Push ke branch (`git push origin feature/improvement`)
5. Buat Pull Request

## 👨‍💻 Author

[Bayu Yudistira Ramadhan](https://github.com/Bayudistrar)
