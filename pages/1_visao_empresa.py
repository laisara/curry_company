#libraries
from haversine import haversine
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

#bibliotecas necessárias
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import folium

st.set_page_config(page_title="Visão Empresa", page_icon="📊", layout="wide")

# ======================================
# Funções
# ======================================

def country_maps(df1):
    #agrupando lat/long central por cidade e tipo de trafego
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).median().reset_index()

    #criando mapa com os pontos centrais das localizações (lat / long)
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], 
                     location_info['Delivery_location_longitude']],
                     popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

    folium_static( map, width=1024, height=600)
            

def order_share_by_week(df1):

    #selecionnado colunas
    cols1 = ['ID', 'week_of_year']

    #(quantidade de pedidos por semana / numero unico de entragadores) por semana
    df_aux1 = df1.loc[:, cols1].groupby(['week_of_year']).count().reset_index()

    #selecionnado colunas do segundo agrupamento
    cols2 = ['Delivery_person_ID', 'week_of_year']
    df_aux2 = df1.loc[:, cols2].groupby(['week_of_year']).nunique().reset_index()

    #juntando dois datframes usando merge
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')
    df_aux['order_by_delivery'] = (df_aux['ID']/df_aux['Delivery_person_ID'])

    #criando grafico de linhas
    fig_lin = px.line(df_aux, x='week_of_year', y='order_by_delivery')

    return fig_lin
        

def order_by_week(df1):

    #criar coluna de semana
    #'%U' -> siginifica que quero domingo como primeiro dia da semana
    # .dt -> transforma minha lista em data para que eu possa aplicar a função de semana ('strftime')


    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    cols = ['ID', 'week_of_year']

    df_aux = df1.loc[:, cols].groupby(['week_of_year']).count().reset_index()

    #desenhar grafico de linhas
    fig_lin = px.line(df_aux, x='week_of_year', y='ID')

    return fig_lin


def traffic_order_city(df1):
    #selecionar as colunas
    cols = ['ID', 'City', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).count().reset_index()

    #gerando grafico de bolhas
    fig_bolha = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return fig_bolha


def traffic_order_share(df1):
    #selecionar as colunas
    cols = ['ID', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['Road_traffic_density']).count().reset_index()

    #calculo percentual -> somatorio ID por tipo de trafego / quantidade total ID
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    #criando o grafico de pizza
    fig_pizza = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig_pizza


def order_by_day(df1):
    cols = ['ID', 'Order_Date']

    #agrupar linhas por data
    df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()

    #desenhar o gráfico de barra
    fig = px.bar(df_aux, x='Order_Date', y='ID')

    return fig


def clean_code(df1):
    # Remover spaco da string
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    linhas_vazias = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias = (df1['City'] != 'NaN')
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias = (df1['Road_traffic_density'] != 'NaN')
    df1 = df1.loc[linhas_vazias, :]

    # Conversao de texto/categoria/string para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # Conversao de texto/categoria/strings para numeros decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    # Remove as linhas da culuna multiple_deliveries que tenham o 
    # conteudo igual a 'NaN '
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # # Comando para remover o texto de números
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1


#---------------------------------------------- Inicialização do Script ----------------------------------------------
# ======================================
# Limpeza do dataframe
# ======================================

#import dataset
df_raw = pd.read_csv('dataset/train.csv')

# Fazendo uma cópia do DataFrame Lido
df1 = clean_code(df_raw)

#Visão - Empresa
# ======================================
# Barra Lateral Streamlit
# ======================================

st.header('Marketplace - Visão Cliente')

#image_path = 'C:/Users/Lais/repos/ftc_programacao_python/logo.png'
image = Image.open("images/logo.png")
st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limete')
date_slider = st.sidebar.slider('Até qual valor', 
                  value=pd.datetime(2022, 4, 13),
                  min_value=pd.datetime(2022, 2, 11),
                  max_value=pd.datetime(2022, 4, 6), 
                  format='DD-MM-YYYY')

st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'Right', 'Jam'],
    default=['Low', 'Medium', 'Right', 'Jam'] )
st.sidebar.markdown("""___""")
st.sidebar.markdown("#### Powered by Comunidade DS")


# ======================================
# Filtros Streamlit
# ======================================

#filtros de data
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtros de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# ======================================
# Layout Streamlit
# ======================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    
    with st.container():
        
        st.markdown('# Orders by Day')
        fig = order_by_day(df1)

        st.plotly_chart(fig, use_container_width=True)  
    
    with st.container():
        
        #criando colunas para divisaõ da pagina
        col1, col2 = st.columns(2)

        with col1:
            
            st.markdown('# Traffic Order Share')
            fig_pizza = traffic_order_share(df1)

            st.plotly_chart(fig_pizza, use_container_width=True)  
            
        with col2:
            
            st.markdown('# Traffic Order City')
            fig_bolha = traffic_order_city(df1)
            
            st.plotly_chart(fig_bolha, use_container_width=True) 
    
with tab2:
    
    with st.container():
        
        st.markdown('# Order by Week')
        fig_lin = order_by_week(df1)
        
        st.plotly_chart(fig_lin, use_container_width=True) 
        
    with st.container():
        
        st.markdown('# Order Share by Week')        
        fig_lin = order_share_by_week(df1)
        
        st.plotly_chart(fig_lin, use_container_width=True) 
          
    
with tab3:
    
    with st.container():
        
        st.markdown('# Country Maps')
        country_maps(df1)
        

    