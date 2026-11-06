import random
import streamlit as st

# Configuración de página
st.set_page_config(page_title="Póker Valdivieso 🎰", page_icon="♠️", layout="centered")

# Estilos CSS con fondo de mesa de póker, fichas y avatares de la gente apostando
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle, #0d5c2f 0%, #031b0e 100%);
        color: #ffffff;
    }
    .card-container {
        background-color: #ffffff;
        color: #000000;
        border-radius: 8px;
        padding: 10px 0px;
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        border: 2px solid #d4af37;
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
    }
    .casino-table {
        background: rgba(0, 0, 0, 0.4);
        border: 4px dashed #d4af37;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    .avatar-box {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        border: 1px solid rgba(212, 175, 55, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

PALOS = {'Corazones': '❤️', 'Diamantes': '♦️', 'Tréboles': '♣️', 'Picas': '♠️'}
VALORES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}


class Carta:
    def __init__(self, valor, palo):
        self.valor = valor
        self.palo = palo
        self.peso = VALORES[valor]
        self.simbolo = PALOS[palo]

    def __str__(self):
        return f"{self.valor}{self.simbolo}"


class Mazo:
    def __init__(self):
        self.cartas = [Carta(v, p) for v in VALORES.keys() for p in PALOS.keys()]
        random.shuffle(self.cartas)

    def repartir(self, cantidad):
        return [self.cartas.pop() for _ in range(cantidad)]


def evaluar_mano(mano):
    mano = sorted(mano, key=lambda c: c.peso, reverse=True)
    valores = [c.peso for c in mano]
    palos = [c.palo for c in mano]

    conteo_valores = {v: valores.count(v) for v in set(valores)}
    frecuencias = sorted(conteo_valores.values(), reverse=True)
    es_flush = len(set(palos)) == 1

    es_straight = False
    if len(set(valores)) == 5:
        if valores[0] - valores[4] == 4:
            es_straight = True
        elif valores == [14, 5, 4, 3, 2]:
            es_straight = True
            valores = [5, 4, 3, 2, 1]

    if es_straight and es_flush:
        return (10, "Escalera Real" if valores[0] == 14 else "Escalera de Color", valores)
    if frecuencias == [4, 1]:
        val_cuad = [k for k, v in conteo_valores.items() if v == 4][0]
        val_simple = [k for k, v in conteo_valores.items() if v == 1][0]
        return (8, "Póker", [val_cuad, val_simple])
    if frecuencias == [3, 2]:
        val_tri = [k for k, v in conteo_valores.items() if v == 3][0]
        val_par = [k for k, v in conteo_valores.items() if v == 2][0]
        return (7, "Full House", [val_tri, val_par])
    if es_flush:
        return (6, "Color", valores)
    if es_straight:
        return (5, "Escalera", valores)
    if frecuencias == [3, 1, 1]:
        val_tri = [k for k, v in conteo_valores.items() if v == 3][0]
        kikers = sorted([k for k, v in conteo_valores.items() if v == 1], reverse=True)
        return (4, "Trío", [val_tri] + kikers)
    if frecuencias == [2, 2, 1]:
        pares = sorted([k for k, v in conteo_valores.items() if v == 2], reverse=True)
        kiker = [k for k, v in conteo_valores.items() if v == 1][0]
        return (3, "Doble Par", pares + [kiker])
    if frecuencias == [2, 1, 1, 1]:
        val_par = [k for k, v in conteo_valores.items() if v == 2][0]
        kikers = sorted([k for k, v in conteo_valores.items() if v == 1], reverse=True)
        return (2, "Par", [val_par] + kikers)

    return (1, "Carta Alta", valores)


# Inicialización de estado
if "fichas" not in st.session_state:
    st.session_state.fichas = 100
if "estado" not in st.session_state:
    st.session_state.estado = "INICIO"
if "apuesta" not in st.session_state:
    st.session_state.apuesta = 10

st.title("🎰 Póker Valdivieso - Mesa VIP")

st.sidebar.markdown("### 🏦 Caja del Casino")
st.sidebar.metric(label="Tus Fichas", value=f"🪙 ${st.session_state.fichas}")

if st.session_state.fichas <= 0:
    st.error("¡Te has quedado sin fichas!")
    if st.button("Reiniciar Fichas ($100)"):
        st.session_state.fichas = 100
        st.session_state.estado = "INICIO"
        st.rerun()

# FASE 1: Mesa de apuestas con la gente apostando y vista previa de cartas
if st.session_state.estado == "INICIO" and st.session_state.fichas > 0:
    st.markdown("""
        <div class="casino-table">
            <h2>🎲 Mesa de Apuestas Valdivieso</h2>
            <p>La gente está tomando asiento y haciendo sus apuestas alrededor de la mesa...</p>
        </div>
    """, unsafe_allow_html=True)

    # Mostrar la gente apostando alrededor de la mesa
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("""
            <div class="avatar-box">
                <span style="font-size: 30px;">🤵‍♂️ Carlos (Dealer)</span><br>
                <small>Repartiendo la mesa</small>
            </div>
        """, unsafe_allow_html=True)
    with col_p2:
        st.markdown("""
            <div class="avatar-box">
                <span style="font-size: 30px;">👩‍🦰 Sofía (Apuesta)</span><br>
                <small>🪙 Apostó $20</small>
            </div>
        """, unsafe_allow_html=True)
    with col_p3:
        st.markdown("""
            <div class="avatar-box">
                <span style="font-size: 30px;">🧔‍♂️ Juan (Apuesta)</span><br>
                <small>🪙 Apostó $50</small>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("### 🃏 Elige tus fichas y revisa las cartas sobre la mesa antes de jugar")

    # Vista previa de cartas decorativas para elegir la apuesta
    prev_col1, prev_col2, prev_col3, prev_col4, prev_col5 = st.columns(5)
    prev_col1.markdown('<div class="card-container">A♠️</div>', unsafe_allow_html=True)
    prev_col2.markdown('<div class="card-container">K♦️</div>', unsafe_allow_html=True)
    prev_col3.markdown('<div class="card-container">Q♣️</div>', unsafe_allow_html=True)
    prev_col4.markdown('<div class="card-container">J❤️</div>', unsafe_allow_html=True)
    prev_col5.markdown('<div class="card-container">10♠️</div>', unsafe_allow_html=True)

    st.write("")
    # Botones rápidos de selección de fichas
    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
    with c_b1:
        if st.button("🪙 Ficha $5"): st.session_state.apuesta = min(5, st.session_state.fichas)
    with c_b2:
        if st.button("🪙 Ficha $10"): st.session_state.apuesta = min(10, st.session_state.fichas)
    with c_b3:
        if st.button("🪙 Ficha $25"): st.session_state.apuesta = min(25, st.session_state.fichas)
    with c_b4:
        if st.button("🪙 Ficha $50"): st.session_state.apuesta = min(50, st.session_state.fichas)

    apuesta = st.number_input("Monto de tu apuesta actual:", min_value=5, max_value=st.session_state.fichas,
                              value=st.session_state.apuesta, step=5)
    st.session_state.apuesta = apuesta

    if st.button("🚀 ¡Sentarse y Repartir Cartas!", type="primary", use_container_width=True):
        st.session_state.mazo = Mazo()
        st.session_state.mano_jugador = st.session_state.mazo.repartir(5)
        st.session_state.mano_pc = st.session_state.mazo.repartir(5)
        st.session_state.estado = "CAMBIO"
        st.rerun()

# FASE 2: Selección de cartas a descartar
elif st.session_state.estado == "CAMBIO":
    st.markdown("""
        <div class="avatar-box" style="margin-bottom: 15px;">
            <h4 style="margin