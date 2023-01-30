#Import
import streamlit as st
import func as f

st.set_page_config(page_title="Esquadrão Arara")

#Page desing
st.title('**Esquadrão Arara**')
st.text('por: Bruno Brasil')
st.image("img.png")

#Conexão
gc = gs.service_account(filename='escavoo-23f562d56bf3.json')
sheet_url = 'https://docs.google.com/spreadsheets/d/1oLBpmUsttn0DmOAHnYi0cuaqQNCwCHF2mvE0k1m2fz0/edit?usp=sharing'
sh = gc.open_by_url(sheet_url)

# aba disponibilidade
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
    df["Horas Voadas"] = pd.to_datetime(df["Horas Voadas"], format='%H:%M:%S').apply(lambda x: x.strftime("%H:%M:%S"))
    df = df.sort_values(by='Horas Voadas', ascending=False)
    df.set_index("Piloto", inplace=True)
    df['Último Voo'] = df['Último Voo'].astype('int')
    # df = df.style.applymap(desadapt, subset=['Último Voo'])
    return df

# Labels quadrinhos
def label_quad():
    ws = sh.worksheet("GERAL")
    df = pd.DataFrame(ws.get_all_values()).iloc[988:]
    return sorted(df[6].unique())

# Quadrinhos
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
    meta = meta.sum(axis=1) / datetime.timedelta(hours=1)

    ws = sh.worksheet("HORAS DE VOO")
    voado = pd.DataFrame(ws.get_all_values()).iloc[18:53, :3]
    voado.columns = ["Piloto", "Horas Voadas", 'Último Voo']
    voado = pd.to_timedelta(voado['Horas Voadas']) / datetime.timedelta(hours=1)
    voado.index = meta.index
    diff = meta - voado
    diff = pd.DataFrame(diff)
    diff.columns = ['Meta']
    diff = diff.sort_values(by='Meta', ascending=False)

    return diff
