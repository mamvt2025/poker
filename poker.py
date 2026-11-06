import random
import streamlit as st

# Configuración de página
st.set_page_config(page_title="Póker Valdivies ", page_icon="♠️", layout="centered")

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

st.title("🎰 poker valdivieso")
st.sidebar.metric(label="Tus Fichas", value=f"${st.session_state.fichas}")

if st.session_state.fichas <= 0:
    st.error("¡Te has quedado sin fichas!")
    if st.button("Reiniciar Fichas"):
        st.session_state.fichas = 100
        st.session_state.estado = "INICIO"
        st.rerun()

# FASE 1: Apuesta e inicio de mano
if st.session_state.estado == "INICIO" and st.session_state.fichas > 0:
    apuesta = st.number_input("¿Cuánto deseas apostar?", min_value=5, max_value=st.session_state.fichas, value=10,
                              step=5)

    if st.button("Repartir Cartas", type="primary"):
        st.session_state.apuesta = apuesta
        st.session_state.mazo = Mazo()
        st.session_state.mano_jugador = st.session_state.mazo.repartir(5)
        st.session_state.mano_pc = st.session_state.mazo.repartir(5)
        st.session_state.estado = "CAMBIO"
        st.rerun()

# FASE 2: Selección de cartas a descartar
elif st.session_state.estado == "CAMBIO":
    st.subheader("Tus Cartas:")
    cols = st.columns(5)
    descartes = []

    for i, carta in enumerate(st.session_state.mano_jugador):
        with cols[i]:
            st.markdown(f"### {carta}")
            if st.checkbox(f"Cambiar", key=f"c_{i}"):
                descartes.append(i)

    if st.button("Procesar Cambio y Evaluar", type="primary"):
        # Reemplazar cartas seleccionadas del jugador
        if descartes:
            nuevas_cartas = st.session_state.mazo.repartir(len(descartes))
            for idx, nueva in zip(descartes, nuevas_cartas):
                st.session_state.mano_jugador[idx] = nueva

        # IA simple para la computadora
        eval_pc_inicial = evaluar_mano(st.session_state.mano_pc)
        if eval_pc_inicial[0] < 2:  # Cambia 2 cartas si solo tiene Carta Alta
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

    st.subheader("Mano Final del Jugador:")
    cols_j = st.columns(5)
    for i, carta in enumerate(st.session_state.mano_jugador):
        cols_j[i].markdown(f"### {carta}")
    st.info(f"Tu jugada: **{res_jugador[1]}**")

    st.divider()

    st.subheader("Mano de la Computadora:")
    cols_pc = st.columns(5)
    for i, carta in enumerate(st.session_state.mano_pc):
        cols_pc[i].markdown(f"### {carta}")
    st.info(f"Jugada de la PC: **{res_pc[1]}**")

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

    if empate:
        st.warning("🤝 ¡Empate! Se te devuelve la apuesta.")
    elif ganado:
        st.balloons()
        st.success(f"🎉 ¡Has ganado ${st.session_state.apuesta}! 🎉")
        st.session_state.fichas += st.session_state.apuesta
    else:
        st.error(f"💀 Has perdido ${st.session_state.apuesta}.")
        st.session_state.fichas -= st.session_state.apuesta

    if st.button("Jugar otra mano"):
        st.session_state.estado = "INICIO"
        st.rerun()