import random
import streamlit as st

# Configuración de página
st.set_page_config(page_title="Póker Valdivieso 🎰", page_icon="♠️", layout="centered")

# Estilos CSS personalizados para simular una mesa de casino y cartas estilizadas
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0b4f26 0%, #052611 100%);
        color: #ffffff;
    }
    .card-container {
        background-color: #ffffff;
        color: #000000;
        border-radius: 10px;
        padding: 15px 5px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        margin: 5px;
        border: 2px solid #d4af37;
    }
    .avatar-box {
        background-color: rgba(0, 0, 0, 0.3);
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 15px;
        border: 1px solid rgba(212, 175, 55, 0.3);
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


# Inicialización de estado en Streamlit
if "fichas" not in st.session_state:
    st.session_state.fichas = 100
if "estado" not in st.session_state:
    st.session_state.estado = "INICIO"  # INICIO, CAMBIO, RESULTADO
if "apuesta" not in st.session_state:
    st.session_state.apuesta = 10

st.title("🎰 Póker Valdivieso")

# Barra lateral con estadísticas y fichas
st.sidebar.markdown("### 🏦 Caja del Casino")
st.sidebar.metric(label="Tus Fichas", value=f"🪙 ${st.session_state.fichas}")

if st.session_state.fichas <= 0:
    st.error("¡Te has quedado sin fichas!")
    if st.button("Reiniciar Fichas ($100)"):
        st.session_state.fichas = 100
        st.session_state.estado = "INICIO"
        st.rerun()

# FASE 1: Apuesta e inicio de mano
if st.session_state.estado == "INICIO" and st.session_state.fichas > 0:
    st.markdown("### 🎲 Realiza tu apuesta")

    # Botones rápidos de selección de fichas
    st.write("Selecciona fichas rápidas o usa el selector:")
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    with col_b1:
        if st.button("🪙 $5"): st.session_state.apuesta = min(5, st.session_state.fichas)
    with col_b2:
        if st.button("🪙 $10"): st.session_state.apuesta = min(10, st.session_state.fichas)
    with col_b3:
        if st.button("🪙 $25"): st.session_state.apuesta = min(25, st.session_state.fichas)
    with col_b4:
        if st.button("🪙 $50"): st.session_state.apuesta = min(50, st.session_state.fichas)

    apuesta = st.number_input("Monto de apuesta:", min_value=5, max_value=st.session_state.fichas,
                              value=st.session_state.apuesta, step=5)
    st.session_state.apuesta = apuesta

    if st.button("♠️ Repartir Cartas", type="primary", use_container_width=True):
        st.session_state.mazo = Mazo()
        st.session_state.mano_jugador = st.session_state.mazo.repartir(5)
        st.session_state.mano_pc = st.session_state.mazo.repartir(5)
        st.session_state.estado = "CAMBIO"
        st.rerun()

# FASE 2: Selección de cartas a descartar
elif st.session_state.estado == "CAMBIO":
    # Avatar de la Computadora en la parte superior
    st.markdown("""
        <div class="avatar-box" style="display: flex; align-items: center; gap: 15px;">
            <span style="font-size: 40px;">🤖</span>
            <div>
                <h4 style="margin: 0; color: #d4af37;">Dealer Bot (Computadora)</h4>
                <p style="margin: 0; font-size: 14px;">Analizando la mesa y esperando tu jugada...</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Avatar del Jugador y sus cartas
    st.markdown("""
        <div class="avatar-box" style="display: flex; align-items: center; gap: 15px;">
            <span style="font-size: 40px;">🤠</span>
            <div>
                <h4 style="margin: 0; color: #d4af37;">Tú (Jugador Valdivieso)</h4>
                <p style="margin: 0; font-size: 14px;">Selecciona las casillas de las cartas que deseas cambiar.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    cols = st.columns(5)
    descartes = []

    for i, carta in enumerate(st.session_state.mano_jugador):
        with cols[i]:
            # Renderizado visual de carta estilo casino
            color_cart = "#ff4b4b" if carta.palo in ['Corazones', 'Diamantes'] else "#111111"
            st.markdown(f"""
                <div style="background-color: white; color: {color_cart}; border-radius: 8px; padding: 12px 0px; text-align: center; font-size: 22px; font-weight: bold; border: 2px solid #ccc; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                    {carta.valor} <span style="font-size: 26px;">{carta.simbolo}</span>
                </div>
            """, unsafe_allow_html=True)
            if st.checkbox(f"Cambiar #{i + 1}", key=f"c_{i}"):
                descartes.append(i)

    st.write("")
    if st.button("🔄 Procesar Cambio y Evaluar", type="primary", use_container_width=True):
        if descartes:
            nuevas_cartas = st.session_state.mazo.repartir(len(descartes))
            for idx, nueva in zip(descartes, nuevas_cartas):
                st.session_state.mano_jugador[idx] = nueva

        # IA simple para la computadora
        eval_pc_inicial = evaluar_mano(st.session_state.mano_pc)
        if eval_pc_inicial[0] < 2:
            indices_pc = random.sample(range(5), 2)
            nuevas_pc = st.session_state.mazo.repartir(2)
            for idx, nueva in zip(indices_pc, nuevas_pc):
                st.session_state.mano_pc[idx] = nueva

        st.session_state.estado = "RESULTADO"
        st.rerun()

# FASE 3: Mostrar resultados
elif st.session_state.estado == "RESULTADO":
    res_jugador = evaluar_mano(st.session_state.mano_jugador)
    res_pc = evaluar_mano(st.session_state.mano_pc)

    # Mostrar Computadora con Avatar
    st.markdown("""
        <div class="avatar-box" style="display: flex; align-items: center; gap: 15px;">
            <span style="font-size: 40px;">🤖</span>
            <div>
                <h4 style="margin: 0; color: #d4af37;">Dealer Bot</h4>
                <p style="margin: 0; font-size: 14px;">Mano final: <b>{}</b></p>
            </div>
        </div>
    """.format(res_pc[1]), unsafe_allow_html=True)

    cols_pc = st.columns(5)
    for i, carta in enumerate(st.session_state.mano_pc):
        with cols_pc[i]:
            color_pc = "#ff4b4b" if carta.palo in ['Corazones', 'Diamantes'] else "#111111"
            st.markdown(f"""
                <div style="background-color: white; color: {color_pc}; border-radius: 8px; padding: 10px 0px; text-align: center; font-size: 20px; font-weight: bold; border: 2px solid #ccc;">
                    {carta.valor} {carta.simbolo}
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Mostrar Jugador con Avatar
    st.markdown("""
        <div class="avatar-box" style="display: flex; align-items: center; gap: 15px;">
            <span style="font-size: 40px;">🤠</span>
            <div>
                <h4 style="margin: 0; color: #d4af37;">Tus Cartas Finales</h4>
                <p style="margin: 0; font-size: 14px;">Tu jugada: <b>{}</b></p>
            </div>
        </div>
    """.format(res_jugador[1]), unsafe_allow_html=True)

    cols_j = st.columns(5)
    for i, carta in enumerate(st.session_state.mano_jugador):
        with cols_j[i]:
            color_j = "#ff4b4b" if carta.palo in ['Corazones', 'Diamantes'] else "#111111"
            st.markdown(f"""
                <div style="background-color: white; color: {color_j}; border-radius: 8px; padding: 10px 0px; text-align: center; font-size: 20px; font-weight: bold; border: 2px solid #ccc;">
                    {carta.valor} {carta.simbolo}
                </div>
            """, unsafe_allow_html=True)

    # Determinar ganador
    ganado = False
    empate = False
    if res_jugador[0] > res_pc[0]:
        ganado = True
    elif res_jugador[0] < res_pc[0]:
        ganado = False
    else:
        if res_jugador[2] > res_pc[2]:
            ganado = True
        elif res_jugador[2] < res_pc[2]:
            ganado = False
        else:
            empate = True

    st.markdown("### 🏆 Resultado de la Ronda")
    if empate:
        st.warning("🤝 ¡Empate! Se te devuelve la apuesta.")
    elif ganado:
        st.balloons()
        st.success(f"🎉 ¡Has ganado ${st.session_state.apuesta}! 🎉")
        st.session_state.fichas += st.session_state.apuesta
    else:
        st.error(f"💀 Has perdido ${st.session_state.apuesta}.")
        st.session_state.fichas -= st.session_state.apuesta

    st.write("")
    if st.button("🎮 Jugar Otra Mano", type="primary", use_container_width=True):
        st.session_state.estado = "INICIO"
        st.rerun()