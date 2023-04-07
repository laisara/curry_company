#libraries
from haversine import haversine
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

#bibliotecas necessárias
import pandas as pd
import numpy as np
import streamlit as st
from streamlit_folium import folium_static
import folium

st.set_page_config(page_title="Visão Restaurantes", page_icon="🍽️", layout="wide")

# ======================================
# Funções
# ======================================


def avg_std_time_city_roadtraffic(df1):
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg( {'Time_taken(min)': ['mean', 'std']} )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                     color='std_time', color_continuous_scale='RdBu',
                     color_continuous_midpoint=np.average(df_aux['std_time']))

    return fig
            

def distancia_media_city(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

    avg_distance = df1.loc[:, [ 'City', 'distance' ]].groupby( 'City' ).mean().reset_index()
    fig = go.Figure(data=[go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])

    return fig
                         

def type_of_order_avg_std(df1):
    cols = ['City', 'Time_taken(min)', 'Type_of_order']
    df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg( {'Time_taken(min)': ['mean', 'std']} )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    return df_aux
            
            
def tempo_medio_entrega_cidade(df1):
                
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg( { 'Time_taken(min)': ['mean', 'std'] } )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar ( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time']) ) )
    fig.update_layout(barmode='group')

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


#Visão - Restaurantes
# =================================================================================================
# Barra Lateral Streamlit
# =================================================================================================

st.header('Marketplace - Visão Restaurantes')

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


city_options = st.sidebar.multiselect(
    'Quais as cidades?',
    ['Urban', 'Semi-Urban', 'Metropolitian'],
    default=['Urban', 'Semi-Urban', 'Metropolitian'] )
st.sidebar.markdown("""___""")

st.sidebar.markdown("#### Powered by Comunidade DS")



# =================================================================================================
# Filtros Streamlit
# =================================================================================================

#filtros de data
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtros de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#filtros de cidade
linhas_selecionadas = df1['City'].isin( city_options )
df1 = df1.loc[linhas_selecionadas, :]

# =================================================================================================
# Layout Streamlit
# =================================================================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )


with tab1:
    with st.container():
        st.title('Overall Metric')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            delivery_unique = df1.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric('Entregadores Únicos', delivery_unique)
            
            
        with col2:
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)  
                                                #axis=1 é condição para dizer ao lambda que tenho mais de uma coluna para acessar
            
            avg_distance = round(df1['distance'] .mean(), 2)
            col2.metric('A distância Média das Entregas', avg_distance)
            
            
        with col3:
            cols = ['Time_taken(min)', 'Festival']
            df_aux = df1.loc[:, cols].groupby(['Festival']).agg( {'Time_taken(min)': ['mean', 'std']} )
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            linhas_selecionadas = df_aux['Festival'] == 'Yes'
            df_aux = round(df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
            
            col3.metric('Tempo Médio de Entrega c/ Festival', df_aux)
            
            
        with col4:
            cols = ['Time_taken(min)', 'Festival']
            df_aux = df1.loc[:, cols].groupby(['Festival']).agg( {'Time_taken(min)': ['mean', 'std']} )
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            linhas_selecionadas = df_aux['Festival'] == 'Yes'
            df_aux = round(df_aux.loc[linhas_selecionadas, 'std_time'], 2)
            
            col4.metric('STD das Entregas c/ Festival', df_aux)
            
        with col5:
            cols = ['Time_taken(min)', 'Festival']
            df_aux = df1.loc[:, cols].groupby(['Festival']).agg( {'Time_taken(min)': ['mean', 'std']} )
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            linhas_selecionadas = df_aux['Festival'] == 'No'
            df_aux = round(df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
            
            col5.metric('Tempo Médio de Entrega s/ Festival', df_aux)
            
        with col6:
            cols = ['Time_taken(min)', 'Festival']
            df_aux = df1.loc[:, cols].groupby(['Festival']).agg( {'Time_taken(min)': ['mean', 'std']} )
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            linhas_selecionadas = df_aux['Festival'] == 'No'
            df_aux = round(df_aux.loc[linhas_selecionadas, 'std_time'], 2)
            
            col6.metric('STD das Entregas s/ Festival', df_aux)
    
    with st.container():        
        st.markdown("""___""")
        st.title('Tempo Médio de entrega por cidade')
        
    with st.container():
        
        col1, col2 = st.columns(2)
        with col1:

            fig = tempo_medio_entrega_cidade(df1)
            st.plotly_chart(fig, use_container_width=True)  
            
        with col2:
         
            df_aux = type_of_order_avg_std(df1)
            st.dataframe(df_aux, use_container_width=True)
            
    with st.container():
        st.markdown("""___""")
        st.title('Distribuição do Tempo')


        col1, col2 = st.columns(2)
            
        with col1:
            fig = distancia_media_city(df1)
                                     
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            fig = avg_std_time_city_roadtraffic(df1)
                                       
            st.plotly_chart(fig, use_container_width=True)
