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


st.set_page_config(page_title="Visão Entregadores", page_icon="🛵", layout="wide")


# ======================================
# Funções
# ======================================


def overall_metrics(col, param):

    if param == 'max':
        result = df1.loc[:, col].max()

    elif param == 'min':
        result = df1.loc[:, col].min()

    return result


def top_entregadores(df1, top_asc):
    #selecionando as colunas
    cols = ['Time_taken(min)', 'City', 'Delivery_person_ID']

    df_aux = ( df1.loc[:, cols]
              .groupby(['City', 'Delivery_person_ID'])
              .max().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index() )

    df_aux1 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_aux3 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)

    df_final = pd.concat([df_aux1, df_aux2, df_aux3])      

    return df_final


def avaliacao_media_entregue(df1):
    #selecionar as colunas
    cols = ['Delivery_person_ID', 'Delivery_person_Ratings']

    #agrupando por entregador
    df_avg_ratings_per_deliver = ( df1.loc[:, cols]
                                  .groupby(['Delivery_person_ID'])
                                  .mean()
                                  .reset_index() )

    return df_avg_ratings_per_deliver
            

def avaliacao_media_trânsito(df1):
    #selecionar colunas
    cols = ['Delivery_person_Ratings', 'Road_traffic_density']

    #agrupamento por tipo de trafego com media e desvio padrão da avaliação
    df_avg_std_rating_by_traffic = ( df1.loc[:, cols]
                                          .groupby(['Road_traffic_density'])
                                          .agg(['mean', 'std']) )

    #mudança do nome daas colunas
    df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

    #reset do index
    df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()

    st.dataframe( round(df_avg_std_rating_by_traffic, 2) )


    st.markdown('##### Avaliação média por clima')
    df_avg_std_rating_by_weather = avaliacao_media_clima(df1)

    return df_avg_std_rating_by_weather
            

def avaliacao_media_clima(df1):
    #selecionar colunas
    cols = ['Delivery_person_Ratings', 'Weatherconditions']

    #agrupamento por tipo de trafego com media e desvio padrão da avaliação
    df_avg_std_rating_by_weather = ( df1.loc[:, cols]
                                    .groupby(['Weatherconditions'])
                                    .agg(['mean', 'std']) )

    #mudança do nome daas colunas
    df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']

    #reset do index
    df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()

    return df_avg_std_rating_by_weather
  

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


#Visão - Entregadores
# =================================================================================================
# Barra Lateral Streamlit
# =================================================================================================

st.header('Marketplace - Visão Entregadores')

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
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'Right', 'Jam'],
    default=['Low', 'Medium', 'Right', 'Jam'] )
st.sidebar.markdown("""___""")


weather_options = st.sidebar.multiselect(
    'Quais as condições do clima?',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'] )
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

#filtros de clima
linhas_selecionadas = df1['Weatherconditions'].isin( weather_options )
df1 = df1.loc[linhas_selecionadas, :]


# =================================================================================================
# Layout Streamlit
# =================================================================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap = 'large') 
        
        
        with col1:
            
            #maior idade
            result = overall_metrics('Delivery_person_Age', param='max')
            col1.metric( 'Maior de idade', result)
            
            
        with col2:
            
            #menor idade
            result = overall_metrics('Delivery_person_Age', param='min')
            col2.metric( 'Menor de idade', result)

                            
        with col3:
            
            #MELHOR condição de veículos
            result = overall_metrics('Vehicle_condition', param='max')
            col3.metric( 'Melhor condição', result)
            
                
        with col4:
            
            #PIOR condição de veículos
            result = overall_metrics('Vehicle_condition', param='min')
            col4.metric( 'Pior condição', result)
                
            
    with st.container():
        
        st.markdown("""___""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2, gap = 'large')
        
        
        with col1:
            st.markdown('##### Avaliação média por entregador')
            df_avg_ratings_per_deliver = avaliacao_media_entregue(df1)
            
            st.dataframe( round(df_avg_ratings_per_deliver, 2) )
            
            
        with col2:
            st.markdown('##### Avaliação média por trânsito')
            df_avg_std_rating_by_weather = avaliacao_media_trânsito(df1)
            
            st.dataframe( round(df_avg_std_rating_by_weather, 2) )

            
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2, gap = 'large') 
        
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df_final = top_entregadores(df1, top_asc=True)
                
            st.dataframe( df_final )
            
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df_final = top_entregadores(df1,  top_asc=False)
            
            st.dataframe( df_final )
