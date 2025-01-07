# Import required libraries
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configure page settings
st.set_page_config(
    page_title="Sistem Evaluasi Kelayakan Kredit",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to improve appearance
st.markdown(
    """
    <style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    .stProgress .st-bo {
        background-color: #4CAF50;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Configuration for fuzzy rules
class FuzzyConfig:
    # Define acceptance rules
    ACCEPTANCE_RULES = [
        (3, 3, 3, 2, 3),
        (3, 3, 3, 2, 2),
        (3, 3, 2, 2, 3),
        (3, 2, 3, 2, 3),
        (3, 3, 2, 2, 2),
        (3, 2, 3, 2, 2),
        (3, 2, 2, 2, 3),
        (2, 3, 3, 2, 3),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 3),
        (2, 2, 3, 2, 2),
        (2, 3, 2, 2, 2),
        (3, 2, 2, 2, 2),
        (2, 2, 3, 2, 3),
        (2, 3, 2, 2, 3),
        (3, 2, 2, 2, 3),
        (2, 3, 3, 2, 2),
        (3, 2, 3, 2, 2),
        (3, 3, 2, 2, 2),
    ]

    # Define rejection rules
    REJECTION_RULES = [
        (1, 1, 1, 1, 1),
        (1, 1, 1, 1, 2),
        (1, 1, 2, 1, 1),
        (1, 2, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 2, 2, 1),
        (1, 2, 1, 2, 1),
        (2, 1, 1, 2, 1),
        (2, 2, 1, 1, 1),
        (2, 1, 2, 1, 1),
        (1, 2, 2, 1, 1),
        (2, 1, 1, 1, 2),
        (1, 2, 1, 1, 2),
        (1, 1, 2, 1, 2),
        (2, 2, 1, 1, 2),
        (2, 1, 2, 1, 2),
        (1, 2, 2, 1, 2),
        (1, 1, 1, 2, 1),
        (1, 1, 2, 2, 2),
        (2, 1, 1, 2, 2),
        (1, 2, 1, 2, 2),
        (2, 2, 1, 2, 1),
        (2, 1, 2, 2, 1),
        (1, 2, 2, 2, 1),
        (2, 2, 1, 2, 2),
        (2, 1, 2, 2, 2),
        (1, 2, 2, 2, 2),
        (1, 1, 1, 2, 2),
        (1, 1, 1, 1, 3),
    ]

    # Criteria data structure
    CRITERIA_DATA = {
        "Character": {
            "title": "Character",
            "description": "Penilaian karakter dan kepribadian nasabah",
            "components": {
                "Itikad": "Penilaian itikad dan tanggung jawab (1: Sangat Buruk - 5: Sangat Baik)",
                "Gaya Hidup": "Penilaian pola hidup (1: Sangat Boros - 5: Sangat Hemat)",
                "Komitmen": "Penilaian komitmen pembayaran (1: Tidak Ada - 5: Sangat Tinggi)",
            },
        },
        "Capital": {
            "title": "Capital",
            "description": "Penilaian modal dan aset nasabah",
            "components": {
                "Penghasilan Tetap": "Penghasilan bulanan (1: <2jt, 2: 2-3.5jt, 3: 3.5-5jt, 4: 5-7.5jt, 5: >7.5jt)",
                "Penghasilan Sampingan": "Penghasilan tambahan (1: Tidak ada, 2: <1jt, 3: 1-2jt, 4: 2-3jt, 5: >3jt)",
                "Tabungan": "Jumlah tabungan (1: <3jt, 2: 3-5jt, 3: 5-20jt, 4: 20-50jt, 5: >50jt)",
            },
        },
        "Capacity": {
            "title": "Capacity",
            "description": "Penilaian kemampuan membayar",
            "components": {
                "Rasio Angsuran": "Rasio angsuran/pendapatan (1: >70%, 2: 51-70%, 3: 31-50%, 4: 20-30%, 5: <20%)",
                "Dana Cadangan": "Dana cadangan (1: Tidak ada, 2: 1-2x, 3: 2-4x, 4: 4-6x, 5: >6x angsuran)",
            },
        },
        "Collateral": {
            "title": "Collateral",
            "description": "Penilaian jaminan yang diberikan",
            "components": {
                "Skor Kredit": "Riwayat kredit (1: Macet - 5: Sangat lancar)",
                "Jaminan": "Nilai jaminan (1: Tidak ada - 5: Fisik premium)",
                "Dokumen": "Kelengkapan dokumen (1: Tidak ada - 5: Sangat lengkap)",
            },
        },
        "Condition": {
            "title": "Condition",
            "description": "Penilaian kondisi ekonomi",
            "components": {
                "Stabilitas Usaha": "Stabilitas usaha (1: Tidak stabil - 5: Sangat stabil)",
                "Prospek Industri": "Prospek industri (1: Menurun - 5: Berkembang pesat)",
                "Faktor Eksternal": "Pengaruh eksternal (1: Sangat negatif - 5: Sangat positif)",
            },
        },
    }


class FuzzyEvaluator:
    @staticmethod
    def calculate_membership_strength(value, level, criteria):
        """Calculate membership strength based on specific fuzzy rules for each criteria"""
        if criteria == "Character":
            if level == 1:  # Buruk
                if value <= 25:
                    return 1.0
                elif 25 <= value <= 40:
                    return (40 - value) / 15
                elif value >= 40:
                    return 0.0
            elif level == 2:  # Sedang
                if value <= 35 or value >= 75:
                    return 0.0
                elif 35 <= value <= 55:
                    return (value - 35) / 20
                elif 55 <= value <= 75:
                    return (75 - value) / 20
            else:  # level 3: Baik
                if value <= 70:
                    return 0.0
                elif 70 <= value <= 85:
                    return (value - 70) / 15
                elif value >= 85:
                    return 1.0

        elif criteria == "Capital":
            if level == 1:  # Rendah
                if value <= 25:
                    return 1.0
                elif 25 <= value <= 40:
                    return (40 - value) / 15
                elif value >= 40:
                    return 0.0
            elif level == 2:  # Sedang
                if value <= 35 or value >= 75:
                    return 0.0
                elif 35 <= value <= 55:
                    return (value - 35) / 20
                elif 55 <= value <= 75:
                    return (75 - value) / 20
            else:  # level 3: Tinggi
                if value <= 70:
                    return 0.0
                elif 70 <= value <= 85:
                    return (value - 70) / 15
                elif value >= 85:
                    return 1.0

        elif criteria == "Capacity":
            if level == 1:  # TidakMampu
                if value <= 25:
                    return 1.0
                elif 25 <= value <= 40:
                    return (40 - value) / 15
                elif value >= 40:
                    return 0.0
            elif level == 2:  # CukupMampu
                if value <= 35 or value >= 75:
                    return 0.0
                elif 35 <= value <= 55:
                    return (value - 35) / 20
                elif 55 <= value <= 75:
                    return (75 - value) / 20
            else:  # level 3: Mampu
                if value <= 70:
                    return 0.0
                elif 70 <= value <= 85:
                    return (value - 70) / 15
                elif value >= 85:
                    return 1.0

        elif criteria == "Collateral":
            if level == 1:  # TidakAman
                if value <= 45:
                    return 1.0
                elif 45 <= value <= 55:
                    return (55 - value) / 10
                elif value >= 55:
                    return 0.0
            else:  # level 2: Aman
                if value <= 45:
                    return 0.0
                elif 45 <= value <= 55:
                    return (value - 45) / 10
                elif value >= 55:
                    return 1.0

        else:  # Condition
            if level == 1:  # TidakStabil
                if value <= 25:
                    return 1.0
                elif 25 <= value <= 40:
                    return (40 - value) / 15
                elif value >= 40:
                    return 0.0
            elif level == 2:  # CukupStabil
                if value <= 35 or value >= 75:
                    return 0.0
                elif 35 <= value <= 55:
                    return (value - 35) / 20
                elif 55 <= value <= 75:
                    return (75 - value) / 20
            else:  # level 3: Stabil
                if value <= 70:
                    return 0.0
                elif 70 <= value <= 85:
                    return (value - 70) / 15
                elif value >= 85:
                    return 1.0

    @staticmethod
    def evaluate_credit(inputs):
        """Evaluate credit worthiness based on fuzzy inputs"""
        criteria_order = ["Character", "Capital", "Capacity", "Collateral", "Condition"]

        # Initialize results containers
        results = {
            "accept": {"predicates": [], "rules": []},
            "reject": {"predicates": [], "rules": []},
        }

        # Evaluate acceptance rules
        for rule in FuzzyConfig.ACCEPTANCE_RULES:
            FuzzyEvaluator._evaluate_rule(
                rule, criteria_order, inputs, results["accept"]
            )

        # Evaluate rejection rules
        for rule in FuzzyConfig.REJECTION_RULES:
            FuzzyEvaluator._evaluate_rule(
                rule, criteria_order, inputs, results["reject"]
            )

        return results

    @staticmethod
    def _evaluate_rule(rule, criteria_order, inputs, result_container):
        """Helper method to evaluate a single rule"""
        strengths = []
        for level, criteria in zip(rule, criteria_order):
            strength = FuzzyEvaluator.calculate_membership_strength(
                inputs[criteria], level, criteria
            )
            if strength <= 0:
                return
            strengths.append(strength)

        alpha = min(strengths)
        result_container["predicates"].append(alpha)
        result_container["rules"].append((rule, strengths))


class CreditEvaluationUI:
    @staticmethod
    def create_input_form():
        """Create and display the input form"""
        st.sidebar.title("Input Data Nasabah")
        inputs = {}

        # Character section
        st.sidebar.subheader("Character")
        st.sidebar.markdown("*Penilaian karakter dan kepribadian nasabah*")
        character_values = []

        itikad = st.sidebar.slider(
            "Itikad",
            1,
            5,
            1,
            help="Penilaian itikad dan tanggung jawab (1: Sangat Buruk - 5: Sangat Baik)",
            key="char_itikad",
        )
        character_values.append(itikad)

        gaya_hidup = st.sidebar.slider(
            "Gaya Hidup",
            1,
            5,
            1,
            help="Penilaian pola hidup (1: Sangat Boros - 5: Sangat Hemat)",
            key="char_gaya_hidup",
        )
        character_values.append(gaya_hidup)

        komitmen = st.sidebar.slider(
            "Komitmen",
            1,
            5,
            1,
            help="Penilaian komitmen pembayaran (1: Tidak Ada - 5: Sangat Tinggi)",
            key="char_komitmen",
        )
        character_values.append(komitmen)

        # New calculation for Character
        char_avg = sum(character_values) / len(character_values)
        inputs["Character"] = (char_avg / 5) * 100
        st.sidebar.markdown(f"**Nilai Character: {inputs['Character']:.1f}**")
        st.sidebar.markdown("---")

        # Capital section
        st.sidebar.subheader("Capital")
        st.sidebar.markdown("*Penilaian modal dan aset nasabah*")
        capital_values = []

        penghasilan = st.sidebar.slider(
            "Penghasilan Tetap",
            1,
            5,
            1,
            help="Penghasilan bulanan (1: <2jt, 2: 2-3.5jt, 3: 3.5-5jt, 4: 5-7.5jt, 5: >7.5jt)",
            key="cap_penghasilan",
        )
        capital_values.append(penghasilan)

        sampingan = st.sidebar.slider(
            "Penghasilan Sampingan",
            1,
            5,
            1,
            help="Penghasilan tambahan (1: Tidak ada, 2: <1jt, 3: 1-2jt, 4: 2-3jt, 5: >3jt)",
            key="cap_sampingan",
        )
        capital_values.append(sampingan)

        tabungan = st.sidebar.slider(
            "Tabungan",
            1,
            5,
            1,
            help="Jumlah tabungan (1: <3jt, 2: 3-5jt, 3: 5-20jt, 4: 20-50jt, 5: >50jt)",
            key="cap_tabungan",
        )
        capital_values.append(tabungan)

        # New calculation for Capital
        cap_avg = sum(capital_values) / len(capital_values)
        inputs["Capital"] = (cap_avg / 5) * 100
        st.sidebar.markdown(f"**Nilai Capital: {inputs['Capital']:.1f}**")
        st.sidebar.markdown("---")

        # Capacity section
        st.sidebar.subheader("Capacity")
        st.sidebar.markdown("*Penilaian kemampuan membayar*")
        capacity_values = []

        rasio_angsuran = st.sidebar.slider(
            "Rasio Angsuran",
            1,
            5,
            1,
            help="Rasio angsuran/pendapatan (1: >70%, 2: 51-70%, 3: 31-50%, 4: 20-30%, 5: <20%)",
            key="capa_rasio",
        )
        capacity_values.append(rasio_angsuran)

        dana_cadangan = st.sidebar.slider(
            "Dana Cadangan",
            1,
            5,
            1,
            help="Dana cadangan (1: Tidak ada, 2: 1-2x, 3: 2-4x, 4: 4-6x, 5: >6x angsuran)",
            key="capa_dana",
        )
        capacity_values.append(dana_cadangan)

        # New calculation for Capacity
        capa_avg = sum(capacity_values) / len(capacity_values)
        inputs["Capacity"] = (capa_avg / 5) * 100
        st.sidebar.markdown(f"**Nilai Capacity: {inputs['Capacity']:.1f}**")
        st.sidebar.markdown("---")

        # Collateral section
        st.sidebar.subheader("Collateral")
        st.sidebar.markdown("*Penilaian jaminan yang diberikan*")
        collateral_values = []

        skor_kredit = st.sidebar.slider(
            "Skor Kredit",
            1,
            5,
            1,
            help="Riwayat kredit (1: Macet, 2: Dalam perhatian, 3: Kurang lancar, 4: Lancar dengan catatan, 5: Sangat lancar)",
            key="coll_skor",
        )
        collateral_values.append(skor_kredit)

        jaminan = st.sidebar.slider(
            "Jaminan",
            1,
            5,
            1,
            help="Nilai jaminan (1: Tidak ada, 2: Non-fisik, 3: Fisik cukup, 4: Fisik baik, 5: Fisik premium)",
            key="coll_jaminan",
        )
        collateral_values.append(jaminan)

        dokumen = st.sidebar.slider(
            "Dokumen",
            1,
            5,
            1,
            help="Kelengkapan dokumen (1: Tidak ada, 2: Kurang, 3: Cukup, 4: Lengkap, 5: Sangat lengkap)",
            key="coll_dokumen",
        )
        collateral_values.append(dokumen)

        # New calculation for Collateral
        coll_avg = sum(collateral_values) / len(collateral_values)
        inputs["Collateral"] = (coll_avg / 5) * 100
        st.sidebar.markdown(f"**Nilai Collateral: {inputs['Collateral']:.1f}**")
        st.sidebar.markdown("---")

        # Condition section
        st.sidebar.subheader("Condition")
        st.sidebar.markdown("*Penilaian kondisi ekonomi*")
        condition_values = []

        stabilitas = st.sidebar.slider(
            "Stabilitas Usaha",
            1,
            5,
            1,
            help="Stabilitas usaha (1: Tidak stabil - 5: Sangat stabil)",
            key="cond_stabilitas",
        )
        condition_values.append(stabilitas)

        prospek = st.sidebar.slider(
            "Prospek Industri",
            1,
            5,
            1,
            help="Prospek industri (1: Menurun - 5: Berkembang pesat)",
            key="cond_prospek",
        )
        condition_values.append(prospek)

        faktor_eksternal = st.sidebar.slider(
            "Faktor Eksternal",
            1,
            5,
            1,
            help="Pengaruh eksternal (1: Sangat negatif - 5: Sangat positif)",
            key="cond_eksternal",
        )
        condition_values.append(faktor_eksternal)

        # New calculation for Condition
        cond_avg = sum(condition_values) / len(condition_values)
        inputs["Condition"] = (cond_avg / 5) * 100
        st.sidebar.markdown(f"**Nilai Condition: {inputs['Condition']:.1f}**")
        st.sidebar.markdown("---")

        return inputs

    @staticmethod
    def display_fuzzification_calculation(inputs, rule_number=10):
        """Display detailed fuzzification calculation"""
        st.markdown("### Studi Kasus (Fuzzifikasi)")
        st.markdown(f"Menghitung derajat keanggotaan untuk setiap input:")

        # Character calculations
        st.markdown("### Character (x = {:.1f})".format(inputs["Character"]))

        # Character Buruk
        if inputs["Character"] <= 25:
            st.latex(
                r"\mu_{Character_{Buruk}}(" + f"{inputs['Character']:.1f}" + r") = 1"
            )
        elif 25 <= inputs["Character"] <= 40:
            char_buruk = (40 - inputs["Character"]) / 15
            st.latex(
                r"\mu_{Character_{Buruk}}("
                + f"{inputs['Character']:.1f}"
                + r") = \frac{40-"
                + f"{inputs['Character']:.1f}"
                + r"}{15} = "
                + f"{char_buruk:.2f}"
            )
        else:
            st.latex(
                r"\mu_{Character_{Buruk}}(" + f"{inputs['Character']:.1f}" + r") = 0"
            )

        # Character Sedang
        if inputs["Character"] <= 35 or inputs["Character"] >= 75:
            st.latex(
                r"\mu_{Character_{Sedang}}(" + f"{inputs['Character']:.1f}" + r") = 0"
            )
        elif 35 <= inputs["Character"] <= 55:
            char_sedang = (inputs["Character"] - 35) / 20
            st.latex(
                r"\mu_{Character_{Sedang}}("
                + f"{inputs['Character']:.1f}"
                + r") = \frac{"
                + f"{inputs['Character']:.1f}-35"
                + r"}{20} = "
                + f"{char_sedang:.2f}"
            )
        else:
            char_sedang = (75 - inputs["Character"]) / 20
            st.latex(
                r"\mu_{Character_{Sedang}}("
                + f"{inputs['Character']:.1f}"
                + r") = \frac{75-"
                + f"{inputs['Character']:.1f}"
                + r"}{20} = "
                + f"{char_sedang:.2f}"
            )

        # Character Baik
        if inputs["Character"] <= 70:
            st.latex(
                r"\mu_{Character_{Baik}}(" + f"{inputs['Character']:.1f}" + r") = 0"
            )
        elif 70 <= inputs["Character"] <= 85:
            char_baik = (inputs["Character"] - 70) / 15
            st.latex(
                r"\mu_{Character_{Baik}}("
                + f"{inputs['Character']:.1f}"
                + r") = \frac{"
                + f"{inputs['Character']:.1f}-70"
                + r"}{15} = "
                + f"{char_baik:.2f}"
            )
        else:
            st.latex(
                r"\mu_{Character_{Baik}}(" + f"{inputs['Character']:.1f}" + r") = 1"
            )

        # Capital calculations
        st.markdown("### Capital (x = {:.1f})".format(inputs["Capital"]))

        # Capital Rendah
        if inputs["Capital"] <= 25:
            st.latex(r"\mu_{Capital_{Rendah}}(" + f"{inputs['Capital']:.1f}" + r") = 1")
        elif 25 <= inputs["Capital"] <= 40:
            cap_rendah = (40 - inputs["Capital"]) / 15
            st.latex(
                r"\mu_{Capital_{Rendah}}("
                + f"{inputs['Capital']:.1f}"
                + r") = \frac{40-"
                + f"{inputs['Capital']:.1f}"
                + r"}{15} = "
                + f"{cap_rendah:.2f}"
            )
        else:
            st.latex(r"\mu_{Capital_{Rendah}}(" + f"{inputs['Capital']:.1f}" + r") = 0")

        # Capital Sedang
        if inputs["Capital"] <= 35 or inputs["Capital"] >= 75:
            st.latex(r"\mu_{Capital_{Sedang}}(" + f"{inputs['Capital']:.1f}" + r") = 0")
        elif 35 <= inputs["Capital"] <= 55:
            cap_sedang = (inputs["Capital"] - 35) / 20
            st.latex(
                r"\mu_{Capital_{Sedang}}("
                + f"{inputs['Capital']:.1f}"
                + r") = \frac{"
                + f"{inputs['Capital']:.1f}-35"
                + r"}{20} = "
                + f"{cap_sedang:.2f}"
            )
        else:
            cap_sedang = (75 - inputs["Capital"]) / 20
            st.latex(
                r"\mu_{Capital_{Sedang}}("
                + f"{inputs['Capital']:.1f}"
                + r") = \frac{75-"
                + f"{inputs['Capital']:.1f}"
                + r"}{20} = "
                + f"{cap_sedang:.2f}"
            )

        # Capital Tinggi
        if inputs["Capital"] <= 70:
            st.latex(r"\mu_{Capital_{Tinggi}}(" + f"{inputs['Capital']:.1f}" + r") = 0")
        elif 70 <= inputs["Capital"] <= 85:
            cap_tinggi = (inputs["Capital"] - 70) / 15
            st.latex(
                r"\mu_{Capital_{Tinggi}}("
                + f"{inputs['Capital']:.1f}"
                + r") = \frac{"
                + f"{inputs['Capital']:.1f}-70"
                + r"}{15} = "
                + f"{cap_tinggi:.2f}"
            )
        else:
            st.latex(r"\mu_{Capital_{Tinggi}}(" + f"{inputs['Capital']:.1f}" + r") = 1")

        # Capacity calculations
        st.markdown("### Capacity (x = {:.1f})".format(inputs["Capacity"]))

        # Capacity Tidak Mampu
        if inputs["Capacity"] <= 25:
            st.latex(
                r"\mu_{Capacity_{TidakMampu}}(" + f"{inputs['Capacity']:.1f}" + r") = 1"
            )
        elif 25 <= inputs["Capacity"] <= 40:
            cap_tidakmampu = (40 - inputs["Capacity"]) / 15
            st.latex(
                r"\mu_{Capacity_{TidakMampu}}("
                + f"{inputs['Capacity']:.1f}"
                + r") = \frac{40-"
                + f"{inputs['Capacity']:.1f}"
                + r"}{15} = "
                + f"{cap_tidakmampu:.2f}"
            )
        else:
            st.latex(
                r"\mu_{Capacity_{TidakMampu}}(" + f"{inputs['Capacity']:.1f}" + r") = 0"
            )

        # Capacity Cukup Mampu
        if inputs["Capacity"] <= 35 or inputs["Capacity"] >= 75:
            st.latex(
                r"\mu_{Capacity_{CukupMampu}}(" + f"{inputs['Capacity']:.1f}" + r") = 0"
            )
        elif 35 <= inputs["Capacity"] <= 55:
            cap_cukupmampu = (inputs["Capacity"] - 35) / 20
            st.latex(
                r"\mu_{Capacity_{CukupMampu}}("
                + f"{inputs['Capacity']:.1f}"
                + r") = \frac{"
                + f"{inputs['Capacity']:.1f}-35"
                + r"}{20} = "
                + f"{cap_cukupmampu:.2f}"
            )
        else:
            cap_cukupmampu = (75 - inputs["Capacity"]) / 20
            st.latex(
                r"\mu_{Capacity_{CukupMampu}}("
                + f"{inputs['Capacity']:.1f}"
                + r") = \frac{75-"
                + f"{inputs['Capacity']:.1f}"
                + r"}{20} = "
                + f"{cap_cukupmampu:.2f}"
            )

        # Capacity Mampu
        if inputs["Capacity"] <= 70:
            st.latex(
                r"\mu_{Capacity_{Mampu}}(" + f"{inputs['Capacity']:.1f}" + r") = 0"
            )
        elif 70 <= inputs["Capacity"] <= 85:
            cap_mampu = (inputs["Capacity"] - 70) / 15
            st.latex(
                r"\mu_{Capacity_{Mampu}}("
                + f"{inputs['Capacity']:.1f}"
                + r") = \frac{"
                + f"{inputs['Capacity']:.1f}-70"
                + r"}{15} = "
                + f"{cap_mampu:.2f}"
            )
        else:
            st.latex(
                r"\mu_{Capacity_{Mampu}}(" + f"{inputs['Capacity']:.1f}" + r") = 1"
            )

        # Collateral calculations
        st.markdown("### Collateral (x = {:.1f})".format(inputs["Collateral"]))

        # Collateral Tidak Aman
        if inputs["Collateral"] <= 45:
            st.latex(
                r"\mu_{Collateral_{TidakAman}}("
                + f"{inputs['Collateral']:.1f}"
                + r") = 1"
            )
        elif 45 <= inputs["Collateral"] <= 55:
            coll_tidakaman = (55 - inputs["Collateral"]) / 10
            st.latex(
                r"\mu_{Collateral_{TidakAman}}("
                + f"{inputs['Collateral']:.1f}"
                + r") = \frac{55-"
                + f"{inputs['Collateral']:.1f}"
                + r"}{10} = "
                + f"{coll_tidakaman:.2f}"
            )
        else:
            st.latex(
                r"\mu_{Collateral_{TidakAman}}("
                + f"{inputs['Collateral']:.1f}"
                + r") = 0"
            )

        # Collateral Aman
        if inputs["Collateral"] <= 45:
            st.latex(
                r"\mu_{Collateral_{Aman}}(" + f"{inputs['Collateral']:.1f}" + r") = 0"
            )
        elif 45 <= inputs["Collateral"] <= 55:
            coll_aman = (inputs["Collateral"] - 45) / 10
            st.latex(
                r"\mu_{Collateral_{Aman}}("
                + f"{inputs['Collateral']:.1f}"
                + r") = \frac{"
                + f"{inputs['Collateral']:.1f}-45"
                + r"}{10} = "
                + f"{coll_aman:.2f}"
            )
        else:
            st.latex(
                r"\mu_{Collateral_{Aman}}(" + f"{inputs['Collateral']:.1f}" + r") = 1"
            )

        # Condition calculations
        st.markdown("### Condition (x = {:.1f})".format(inputs["Condition"]))

        # Condition Tidak Stabil
        if inputs["Condition"] <= 25:
            st.latex(
                r"\mu_{Condition_{TidakStabil}}("
                + f"{inputs['Condition']:.1f}"
                + r") = 1"
            )
        elif 25 <= inputs["Condition"] <= 40:
            cond_tidakstabil = (40 - inputs["Condition"]) / 15
            st.latex(
                r"\mu_{Condition_{TidakStabil}}("
                + f"{inputs['Condition']:.1f}"
                + r") = \frac{40-"
                + f"{inputs['Condition']:.1f}"
                + r"}{15} = "
                + f"{cond_tidakstabil:.2f}"
            )
        else:
            st.latex(
                r"\mu_{Condition_{TidakStabil}}("
                + f"{inputs['Condition']:.1f}"
                + r") = 0"
            )

        # Condition Cukup Stabil
        if inputs["Condition"] <= 35 or inputs["Condition"] >= 75:
            st.latex(
                r"\mu_{Condition_{CukupStabil}}("
                + f"{inputs['Condition']:.1f}"
                + r") = 0"
            )
        elif 35 <= inputs["Condition"] <= 55:
            cond_cukupstabil = (inputs["Condition"] - 35) / 20
            st.latex(
                r"\mu_{Condition_{CukupStabil}}("
                + f"{inputs['Condition']:.1f}"
                + r") = \frac{"
                + f"{inputs['Condition']:.1f}-35"
                + r"}{20} = "
                + f"{cond_cukupstabil:.2f}"
            )
        else:
            cond_cukupstabil = (75 - inputs["Condition"]) / 20
            st.latex(
                r"\mu_{Condition_{CukupStabil}}("
                + f"{inputs['Condition']:.1f}"
                + r") = \frac{75-"
                + f"{inputs['Condition']:.1f}"
                + r"}{20} = "
                + f"{cond_cukupstabil:.2f}"
            )

        # Condition Stabil
        if inputs["Condition"] <= 70:
            st.latex(
                r"\mu_{Condition_{Stabil}}(" + f"{inputs['Condition']:.1f}" + r") = 0"
            )
        elif 70 <= inputs["Condition"] <= 85:
            cond_stabil = (inputs["Condition"] - 70) / 15
            st.latex(
                r"\mu_{Condition_{Stabil}}("
                + f"{inputs['Condition']:.1f}"
                + r") = \frac{"
                + f"{inputs['Condition']:.1f}-70"
                + r"}{15} = "
                + f"{cond_stabil:.2f}"
            )
        else:
            st.latex(
                r"\mu_{Condition_{Stabil}}(" + f"{inputs['Condition']:.1f}" + r") = 1"
            )

    @staticmethod
    def display_results(inputs, evaluation_results):
        """Display evaluation results with detailed calculation"""
        # Display fuzzification calculation first
        CreditEvaluationUI.display_fuzzification_calculation(inputs)

        st.markdown("---")  # Add separator

        # Display inference process
        st.markdown("### Proses Inferensi")
        accept_predicates = evaluation_results["accept"]["predicates"]
        reject_predicates = evaluation_results["reject"]["predicates"]

        if accept_predicates or reject_predicates:
            if evaluation_results["accept"]["rules"]:
                st.markdown("#### Rules Penerimaan yang Terpicu:")
                for i, (rule, strengths) in enumerate(
                    evaluation_results["accept"]["rules"], 1
                ):
                    alpha = min(strengths)
                    st.markdown(f"**Rule {i}:**")
                    st.write("IF:")
                    criteria_order = [
                        "Character",
                        "Capital",
                        "Capacity",
                        "Collateral",
                        "Condition",
                    ]
                    levels = {1: "Buruk", 2: "Sedang", 3: "Baik"}
                    for idx, (level, criteria) in enumerate(zip(rule, criteria_order)):
                        if criteria == "Collateral":
                            level_text = "TidakAman" if level == 1 else "Aman"
                        else:
                            if criteria == "Capital":
                                levels = {1: "Rendah", 2: "Sedang", 3: "Tinggi"}
                            elif criteria == "Capacity":
                                levels = {1: "TidakMampu", 2: "CukupMampu", 3: "Mampu"}
                            elif criteria == "Condition":
                                levels = {
                                    1: "TidakStabil",
                                    2: "CukupStabil",
                                    3: "Stabil",
                                }
                            level_text = levels[level]
                        st.write(
                            f"- {criteria} is {level_text} (μ = {strengths[idx]:.2f})"
                        )
                    st.write("THEN: Keputusan = Diterima")
                    st.write(
                        f"α-predikat = min({', '.join([f'{s:.2f}' for s in strengths])}) = {alpha:.2f}"
                    )
                    st.markdown("---")

            if evaluation_results["reject"]["rules"]:
                st.markdown("#### Rules Penolakan yang Terpicu:")
                for i, (rule, strengths) in enumerate(
                    evaluation_results["reject"]["rules"], 1
                ):
                    alpha = min(strengths)
                    st.markdown(f"**Rule {i}:**")
                    st.write("IF:")
                    criteria_order = [
                        "Character",
                        "Capital",
                        "Capacity",
                        "Collateral",
                        "Condition",
                    ]
                    levels = {1: "Buruk", 2: "Sedang", 3: "Baik"}
                    for idx, (level, criteria) in enumerate(zip(rule, criteria_order)):
                        if criteria == "Collateral":
                            level_text = "TidakAman" if level == 1 else "Aman"
                        else:
                            if criteria == "Capital":
                                levels = {1: "Rendah", 2: "Sedang", 3: "Tinggi"}
                            elif criteria == "Capacity":
                                levels = {1: "TidakMampu", 2: "CukupMampu", 3: "Mampu"}
                            elif criteria == "Condition":
                                levels = {
                                    1: "TidakStabil",
                                    2: "CukupStabil",
                                    3: "Stabil",
                                }
                            level_text = levels[level]
                        st.write(
                            f"- {criteria} is {level_text} (μ = {strengths[idx]:.2f})"
                        )
                    st.write("THEN: Keputusan = Ditolak")
                    st.write(
                        f"α-predikat = min({', '.join([f'{s:.2f}' for s in strengths])}) = {alpha:.2f}"
                    )
                    st.markdown("---")

            # Calculate weighted average
            accept_weight = sum(accept_predicates)
            reject_weight = sum(reject_predicates)
            total_weight = accept_weight + reject_weight
            numerator = accept_weight * 1  # z=1 for acceptance rules
            z = round(numerator / total_weight if total_weight > 0 else 0, 2)
            decision = "DITERIMA" if z > 0.5 else "DITOLAK"

            # Display defuzzification calculation
            st.markdown("### Proses Defuzzifikasi")
            st.markdown("Menggunakan metode weighted average dengan rumus:")
            st.latex(r"z = \frac{\sum \alpha_i * z_i}{\sum \alpha_i}")

            st.markdown("#### Kalkulasi Terperinci:")
            st.write("**Komponen Weighted Sum:**")
            st.write("Rules Penerimaan (z = 1):")

            numerator_terms = []
            denominator_terms = []

            if accept_predicates:
                for i, alpha in enumerate(accept_predicates, 1):
                    st.write(f"α{i} × 1 = {alpha:.2f}")
                    numerator_terms.append(f"{alpha:.2f}")
                    denominator_terms.append(f"{alpha:.2f}")
                st.write(f"∑(αi × 1) = {accept_weight:.2f}")
            else:
                st.write("Tidak ada rules penerimaan yang terpicu")

            st.write("\nRules Penolakan (z = 0):")
            if reject_predicates:
                for i, alpha in enumerate(reject_predicates, 1):
                    st.write(f"α{i} × 0 = 0")
                    denominator_terms.append(f"{alpha:.2f}")
                st.write(f"∑(αi × 0) = 0")
            else:
                st.write("Tidak ada rules penolakan yang terpicu")

            st.write(f"\nTotal α-predikat (∑αi) = {total_weight:.2f}")

            # Display final calculation with step-by-step process
            st.markdown("#### Kalkulasi Final:")
            if accept_predicates:
                if len(accept_predicates) > 1:
                    # Multiple acceptance rules
                    # First show the complete formula with all multiplications
                    numerator_terms = [
                        f"({alpha:.2f} \\times 1)" for alpha in accept_predicates
                    ]
                    denominator_terms = [
                        f"{alpha:.2f}"
                        for alpha in accept_predicates + reject_predicates
                    ]

                    # Show step 1: Complete formula with multiplications
                    numerator_step1 = " + ".join(numerator_terms)
                    denominator_step1 = " + ".join(denominator_terms)

                    # Show step 2: Resolved multiplications
                    numerator_step2 = " + ".join(
                        [f"{alpha:.2f}" for alpha in accept_predicates]
                    )

                    # Show step 3: Final summed values and result
                    st.latex(
                        f"z = \\frac{{{numerator_step1}}}{{{denominator_step1}}} = "
                        f"\\frac{{{numerator_step2}}}{{{denominator_step1}}} = "
                        f"\\frac{{{accept_weight:.2f}}}{{{total_weight:.2f}}} = "
                        f"{(accept_weight/total_weight):.2f}"
                    )
                else:
                    # Single acceptance rule
                    st.latex(
                        f"z = \\frac{{({accept_predicates[0]:.2f} \\times 1)}}{{{total_weight:.2f}}} = "
                        f"\\frac{{{accept_predicates[0]:.2f}}}{{{total_weight:.2f}}} = "
                        f"{(accept_weight/total_weight):.2f}"
                    )
            elif reject_predicates:
                # Only rejection rules
                numerator_terms = [
                    f"({alpha:.2f} \\times 0)" for alpha in reject_predicates
                ]
                denominator_terms = [f"{alpha:.2f}" for alpha in reject_predicates]

                numerator_step1 = " + ".join(numerator_terms)
                denominator_step1 = " + ".join(denominator_terms)

                st.latex(
                    f"z = \\frac{{{numerator_step1}}}{{{denominator_step1}}} = "
                    f"\\frac{{0}}{{{total_weight:.2f}}} = 0.00"
                )
            else:
                st.latex(r"z = \frac{0}{0} = 0")

            # Display interpretation
            st.markdown("#### Interpretasi:")
            st.write('- Jika nilai z > 0.5 maka keputusan "Diterima"')
            st.write('- Jika nilai z ≤ 0.5 maka keputusan "Ditolak"')
            st.write(
                f"Karena hasil defuzzifikasi menghasilkan z = {z:.2f} {'>' if z > 0.5 else '≤'} 0.5,"
            )
            st.write(f'maka pengajuan kredit "{decision}".')

        else:
            st.write(
                "Tidak ada rules yang terpicu - semua rules memiliki α-predicate = 0"
            )
            st.markdown("### Proses Defuzzifikasi")
            st.markdown("#### Kalkulasi:")
            st.write("Tidak ada rules yang terpicu, sehingga:")
            st.write("∑(αi × zi) = 0")
            st.write("∑αi = 0")
            st.latex(r"z = \frac{0}{0} = 0")
            st.write("Karena tidak ada rules yang terpicu, maka otomatis DITOLAK")
            decision = "DITOLAK"
            z = 0.00

        # Display final decision
        st.markdown("### Keputusan Final")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Keputusan", decision)
        with col2:
            st.metric("Nilai Defuzzifikasi", f"{z:.2f}")

        # Display input values and visualization in expanders
        with st.expander("Lihat Nilai Input 5C"):
            for criteria, value in inputs.items():
                st.write(f"{criteria}: {value:.2f}")

        with st.expander("Lihat Visualisasi"):
            CreditEvaluationUI._display_visualization(inputs)

    @staticmethod
    def _display_visualization(inputs):
        """Create and display radar chart visualization"""
        categories = list(inputs.keys())
        values = list(inputs.values())

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=values, theta=categories, fill="toself", name="Nilai Evaluasi"
            )
        )

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)


def main():
    """Main function to run the credit evaluation system"""
    st.title("Sistem Evaluasi Kelayakan Kredit")
    st.markdown(
        """
        Sistem ini menggunakan logika fuzzy Sugeno untuk mengevaluasi kelayakan kredit 
        berdasarkan prinsip 5C (Character, Capacity, Capital, Collateral, dan Condition).
        """
    )

    # Create input form
    inputs = CreditEvaluationUI.create_input_form()

    # Add evaluation button with unique key
    if st.sidebar.button("Evaluasi Kelayakan", type="primary", key="evaluate_button"):
        try:
            # Perform evaluation
            evaluation_results = FuzzyEvaluator.evaluate_credit(inputs)

            # Display results directly
            CreditEvaluationUI.display_results(inputs, evaluation_results)

        except Exception as e:
            st.error(f"Terjadi kesalahan dalam evaluasi: {str(e)}")
            st.write("Silakan periksa kembali input Anda dan coba lagi.")


if __name__ == "__main__":
    main()
