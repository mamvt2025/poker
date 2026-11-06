import random
import streamlit as st

# Configuración de página
st.set_page_config(page_title="Póker Valdivieso 🎰", page_icon="♠️", layout="centered")

# Estilos CSS con fondo claro y distribución precisa en las 4 esquinas de la mesa
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, #2e7d32 0%, #144017 100%);
        color: #ffffff;
    }
    .card-container {
        background-color: #ffffff;
        color: #000000;
        border-radius: 8px;
        padding: 8px 0px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        border: 2px solid #d4af37;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    /* Contenedor principal de la mesa de póker */
    .poker-table-layout {
        background: radial-gradient(ellipse at center, #388e3c 0%, #2e7d32 60%, #1b5e20 100%);
        border: 12px solid #795548;
        border-radius: 140px;
        padding: 30px 20px;
        margin: 20px 0px;
        box-shadow: inset 0 0 35px rgba(0,0,0,0.5), 0 10px 25px rgba(0,0,0,0.5);
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: auto auto auto;
        gap: 20px;
        align-items: center;
        justify-items: center;
    }
    .player-corner {
        background-color: rgba(0, 0, 0, 0.6);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        border: 2px solid #ffd700;
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
        width: 100%;
        max-width: 180px;
    }
    .center-pot {
        grid-column: span 2;
        text-align: center;
        background: rgba(0, 0, 0, 0.25);
        padding: 15px;
        border-radius: 15px;
        width: 100%;
        border: 1px dashed rgba(255, 255, 255, 0.3);
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

# FASE 1: Mesa interactiva con jugadores en cada esquina
if st.session_state.estado == "INICIO" and st.session_state.fichas > 0:
    st.markdown("### 🎲 Mesa de Póker Abierta")

    # Estructura visual de la mesa con jugadores en las 4 esquinas reales
    st.markdown('<div class="poker-table-layout">', unsafe_allow_html=True)

    # 1. Esquina Superior Izquierda (Dealer Bot)
    st.markdown("""
        <div class="player-corner" style="grid-column: 1; grid-row: 1;">
            <span style="font-size: 26px;">🤖</span><br>
            <b>Dealer Bot</b><br>
            <small style="color: #ffd700;">🪙 Casa</small>
        </div>
    """, unsafe_allow_html=True)

    # 2. Esquina Superior Derecha (Sofía)
    st.markdown("""
        <div class="player-corner" style="grid-column: 2; grid-row: 1;">
            <span style="font-size: 26px;">👩‍🦰</span><br>
            <b>Sofía</b><br>
            <small style="color: #ffd700;">🪙 Apostó $20</small>
        </div>
    """, unsafe_allow_html=True)

    # Centro de la mesa (Cartas de referencia y paño)
    st.markdown("""
        <div class="center-pot">
            <h4 style='color: #fff59d; margin-bottom: 10px;'>♠️ Cartas de Referencia en la Mesa ♥️</h4>
        </div>
    """, unsafe_allow_html=True)

    # Fila de cartas en el centro
    c_rc1, c_rc2, c_rc3, c_rc4, c_rc5 = st.columns(5)
    with c_rc1:
        st.markdown('<div class="card-container">A♠️</div>', unsafe_allow_html=True)
    with c_rc2:
        st.markdown('<div class="card-container">K♦️</div>', unsafe_allow_html=True)
    with c_rc3:
        st.markdown('<div class="card-container">Q♣️</div>', unsafe_allow_html=True)
    with c_rc4:
        st.markdown('<div class="card-container">J❤️</div>', unsafe_allow_html=True)
    with c_rc5:
        st.markdown('<div class="card-container">10♠️</div>', unsafe_allow_html=True)

    # 3. Esquina Inferior Izquierda (Juan)
    st.markdown("""
        <div class="player-corner" style="grid-column: 1; grid-row: 3;">
            <span style="font-size: 26px;">🧔‍♂️</span><br>
            <b>Juan</b><br>
            <small style="color: #ffd700;">🪙 Apostó $50</small>
        </div>
    """, unsafe_allow_html=True)

    # 4. Esquina Inferior Derecha (Tú)
    st.markdown(f"""
        <div class="player-corner" style="grid-column: 2; grid-row: 3; border-color: #69f0ae;">
            <span style="font-size: 26px;">🤠</span><br>
            <b>Tú (Valdivieso)</b><br>
            <small style="color: #69f0ae;">🪙 Fichas: ${st.session_state.fichas}</small>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 🪙 Elige tu Apuesta")
    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
    with c_b1:
        if st.button