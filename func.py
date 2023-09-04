# Libs
import gspread as gs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from haversine import haversine, Unit
import base64
from io import BytesIO
import streamlit as st
from openpyxl import load_workbook

#Conexão
gc = gs.service_account(filename='escavoo-23f562d56bf3.json')
sheet_url = 'https://docs.google.com/spreadsheets/d/1oLBpmUsttn0DmOAHnYi0cuaqQNCwCHF2mvE0k1m2fz0/edit?usp=sharing'
sh = gc.open_by_url(sheet_url)

#image as base
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def landpage():
    img = get_img_as_base64("Pic/arara.png")
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
    background-image: url("data:image/png;base64,{img}");
    background-size: cover;
    }}
    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
    }}
    </style>
    """
    return page_bg_img

def indisp(inicio, fim, mes):
    ws = sh.worksheet(mes)
    df = pd.DataFrame(ws.get_all_values()[1:])
    df[0] = df[0] + " "
    frame = df.iloc[:, inicio:fim + 1]
    na = frame.replace('', np.nan).isnull().all(axis=1)
    naidx = na[na == True].index
    df = df.iloc[naidx].groupby(by=[32, 33], sort=False).sum()[0]
    df.name = "Disponíveis"
    return df

# Coloração da aba pau de sebo
def desadapt(v):
    if v > 30 and v < 45:
        return f"background-color: {'yellow'}"
    elif v > 45:
        return f"background-color: {'red'}"

# Aba pau de sebo
def sebo():
    ws = sh.worksheet("HORAS DE VOO")
    df = pd.DataFrame(ws.get_all_values()).iloc[18:53, :4]
    df.columns = ["Piloto", "Horas Voadas","Data",'Último Voo']
    df = df.drop("Data",axis=1)
    df["hora"] = pd.to_timedelta(df["Horas Voadas"]) / timedelta(hours=1)
    df = df.sort_values(by='hora', ascending=False).drop('hora',axis=1)
    df.set_index("Piloto", inplace=True)
    df['Último Voo'] = df['Último Voo'].astype('int')
    return df

# Labels quadrinhos
def label_quad():
    ws = sh.worksheet("GERAL")
    df = pd.DataFrame(ws.get_all_values()).iloc[988:]
    return sorted(df[6].unique())

#Quadrinhos
def quad(quadrinho, funcao, op):
    ws = sh.worksheet("GERAL")
    df = pd.DataFrame(ws.get_all_values()).iloc[1:]
    df = df[[0, 1, 5, 6, 9]].replace("", np.nan)
    df.dropna(inplace=True)
    df[5] = df[5].apply(lambda x: x.replace(',', "."))
    df[5] = pd.to_numeric(df[5]).astype('float')
    df = df.groupby(by=[6, 0, 1, 9]).sum()
    df = df.loc[quadrinho].sort_values(by=[5])
    df = df.loc[(funcao, slice(None), op), :]
    df.columns = ["Quadrinhos"]
    df['Quadrinhos'] = pd.to_numeric(df.Quadrinhos).astype('int')

    return df

#Filtro indisp
def indisp_quad(inicio, fim, mes):
    ws = sh.worksheet(mes)
    df = pd.DataFrame(ws.get_all_values()[1:])
    frame = df.iloc[:, inicio:fim + 1]
    na = frame.replace('', np.nan).isnull().all(axis=1)
    naidx = na[na == True].index
    df = df.iloc[naidx].groupby(by=[0], sort=False).sum()
    df.name = "Disponíveis"
    return df.index

#Tabela de planejamento de horas
def plan(mes):
    ws = sh.worksheet("PLANEJAMENTO")
    meta = pd.DataFrame(ws.get_all_values()[1:]).set_index(0)
    time = [pd.to_timedelta(meta.iloc[:, i]) for i in range(int(mes))]
    meta = pd.DataFrame(time).T
    meta = meta.sum(axis=1) / timedelta(hours=1)

    ws = sh.worksheet("HORAS DE VOO")
    voado = pd.DataFrame(ws.get_all_values()).iloc[18:53, :3]
    voado.columns = ["Piloto", "Horas Voadas", 'Último Voo']
    voado = pd.to_timedelta(voado['Horas Voadas']) / timedelta(hours=1)
    voado.index = meta.index
    diff = meta - voado
    diff = pd.DataFrame(diff)
    diff.columns = ['Meta']
    diff = diff.sort_values(by='Meta', ascending=False)

    return diff

#Arrendodamento
def mround(number, multiple):
    return multiple * round(number / multiple)

#Conversor de hora
def convert_time(number,string=True):
  h = str(number).split('.')[0]
  m = int(float('0'+'.'+str(number).split('.')[1])*60)
  m = mround(m,5)
  if string==True:
      if m<10:
        return str(f'{h}'+':'+f'0{m}')
      else:
        return str(f'{h}'+':'+f'{m}')
  else:
    return int(h), m

def serie_to_timedelta(serie, sum=False):
    ajust_serie = serie.apply(lambda x: f'{x}:00')
    timedelta_serie = pd.to_timedelta(ajust_serie)
    if sum == False:
        return timedelta_serie
    else:
        days = timedelta_serie.sum().days
        hours = timedelta_serie.sum().seconds / 3600
        result = convert_time(hours +  days*24)
        return result

#Combustível em rota
def fuel_trip(ete_route, ete_altn):
    fuel_trip = int(700*(ete_route+ete_altn+0.75))
    return fuel_trip

@st.cache_data
def data_icao():
    icao = pd.read_excel("Plan/ICAO.xlsx").set_index("DESIG")
    return icao

@st.cache_data
def data_icao_label():
    icao = data_icao()
    labels = icao.index.to_list()
    labels.extend(icao.index)
    labels.extend(icao.index)
    labels.extend(icao.index)
    return labels
    
#função planejamento
def braplan(data,hora,rota,alternativa):
    icao = data_icao()
    plans = []
    for i in range(len(alternativa)):
        #Ajuste da data para Datetime
        dep_dt = datetime.combine(data, hora)
        data_format = data.strftime('%d/%m/%y')

        #Campo Hora(Z)
        if i ==0:
            hora_z = hora.strftime("%H:%M")
        else:
            dep_dt = eta + timedelta(hours=+1, minutes=+30)
            hora_z = dep_dt.strftime("%H:%M")

        #Campo DEP, ARR e ALT
        dep = rota[i]
        arr = rota[i+1]
        alt = alternativa[i]

        #trip
        trip = rota[i:i+2] + [alt]

        #Campo TEV
        coo=[]
        for j in trip:
            coo.append(((icao.loc[j].LAT, icao.loc[j].LON)))

        ete_route = haversine(coo[0], coo[1], unit=Unit.NAUTICAL_MILES)/215
        tev_route = convert_time(ete_route)

        #Campo ETA
        h,m = convert_time(ete_route, string=False)
        eta = dep_dt + timedelta(hours=+h, minutes=+m)
        eta_str = eta.strftime("%H:%M")

        #Campo TEV ALT
        ete_alt = haversine(coo[1], coo[2], unit=Unit.NAUTICAL_MILES)/215
        tev_alt = convert_time(ete_alt)

        #Campo COMB
        trip_fuel = fuel_trip(ete_route, ete_alt)
        comb = mround(trip_fuel,50)
        comb_route = fuel_trip(ete_route,-0.75)
        comb_route = mround(comb_route,50)

        #Linha do planejamento
        plan = {"DATA": data_format,
            "HORA(Z)":hora_z,
            "DEP":dep,
            "TEV":tev_route,
            "ARR":arr,
            "ETA(Z)":eta_str,
            "ALT":alt,
            "TEV ALT":tev_alt,
            "COMB":comb,
            "COMB_ROUTE": comb_route
           }
        plans.append(plan)
    return pd.DataFrame(plans)

#Não abastece
def disp(df, noabast, PBO):
    for i in range(len(df)):
        if df.loc[i, "ARR"] in noabast:
            df.loc[i, "COMB"] = df.loc[i + 1, "COMB"] + df.loc[i, "COMB_ROUTE"]
    try:
        # Disponibilidade
        df["DISP"] = 21000 - df.COMB - PBO
        df.DISP = df.DISP.clip(0,5000)
        df = df.drop('COMB_ROUTE', axis=1)
    except:
        pass
    return df

@st.cache_data
def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

@st.cache_data
def workload():
    wb = load_workbook('OM/OM.xlsx')
    return wb

def excel_to_bytes(wb):
            bytes_io = BytesIO()
            wb.save(bytes_io)
            bytes_data = bytes_io.getvalue()
            bytes_io.close()
            return bytes_data

@st.cache_data
def efetivo():
    efetivo = pd.read_excel('OM/efetivo.xlsx').set_index("trigrama")
    return efetivo

def trigname(df, lista_trig):
  comp_name = [df.loc[trig].nome for trig in lista_trig]
  return comp_name
