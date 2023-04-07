import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="Home",
    page_icon="🚀",
    
)



#image_path = 'C:/Users/Lais/repos/ftc_programacao_python/'
image = Image.open("images/logo.png")
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregados e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gernecial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanaisde crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes.

    """ )