#Import
import streamlit as st
import func as f
import pandas as pd
import datetime

st.set_page_config(page_title="Esquadrão Arara")

# Sidebar
with st.sidebar:
    #Style
    st.markdown("<h1 style='text-align: center; "
                "margin-top:-80px; color: "
                "black;'"
                ">Tudo Sob Nossas Asas!</h1>", unsafe_allow_html=True)
    st.markdown( """
        <style>
            [data-testid=stSidebar] [data-testid=stImage]{
                text-align: center;
                display: block;
                margin-top:-55px;
                margin-left: auto;
                margin-right: auto;
                width: 50%;
            }
        </style>
        """, unsafe_allow_html=True)
    #content
    st.image("Pic/bolacha.png")
    pages = st.selectbox('Selecione a página desejada', ['','Escala de Voo','Planejamento de Missão'])

#landpage
if pages == '':
    #Style
    st.markdown(f.landpage(), unsafe_allow_html=True)
    st.markdown("<h1 style= margin-top:-100px;>"
                "Bem-vindo ao Esquadrão Arara</h1>",unsafe_allow_html=True)
    st.markdown('<p style= margin-top:-45px;> Por: Bruno Brasil</p>',unsafe_allow_html=True)

#Page - Escala
if pages == "Escala de Voo":
    # Page desing
    st.title('**Escala de Voo**')

    #options box
    options= st.selectbox('Selecione a função desejada:',["","Disponibilidade","Pau de Sebo", "Quadrinhos","Escala"])

    calendario = {1:"JANEIRO", 2:"FEVEREIRO", 3:"MARÇO",4:"ABRIL",5:"MAIO",
                      6:"JUNHO",7:"JULHO",8:"AGOSTO",9:"SETEMBRO",10:"OUTUBRO",
                      11:"NOVEMBRO",12:"DEZEMBRO"}

    if options == "Disponibilidade":
        inicio = st.date_input('Início da Disponibilidade')
        fim = st.date_input('Término da Disponibilidade')
        mes = calendario.get(inicio.month)

        if fim >= inicio:
            try:
                st.table(f.indisp(inicio.day,fim.day,mes))
            except:
                pass

    if options == "Pau de Sebo":
        sebo = f.sebo()
        sebo = sebo.style.applymap(f.desadapt, subset=['Último Voo'])
        st.table(sebo)

    if options == "Quadrinhos":
        labels = f.label_quad()
        quadrinho = st.selectbox('Selecione o quadrinho desejado:', labels)

        #Filtro por operacionalidade
        if quadrinho!="":
            funcao = st.multiselect('Filtrar por função a bordo:',
                                ['PILOTO', 'MECÂNICO', 'LOADMASTER'],
                                ['PILOTO', 'MECÂNICO', 'LOADMASTER'])

            op = st.multiselect('Filtrar por operacionalidade:',
                                ['IN', 'OP', 'PB', 'AL'],
                                ['IN', 'OP', 'PB', 'AL'])

        #checkbox para verificar disponibilidade
        disp = st.checkbox('DISPONIBILIDADE')

        try:
            #Quadrinho + disponibilidade
            if disp == True:
                inicio = st.date_input('Início da Disponibilidade')
                fim = st.date_input('Término da Disponibilidade')
                mes = calendario.get(inicio.month)
                ind = f.indisp_quad(inicio.day, fim.day, mes)
                df = f.quad(quadrinho,funcao,op)
                st.table(df[df.index.isin(ind, level=1)])
            # Somente Quadrinho
            else:
                st.table(f.quad(quadrinho,funcao,op))
        except:
            pass

    if options == "Escala":
        #Quadrinhos
        labels = f.label_quad()
        quadrinho = st.selectbox('Selecione o quadrinho desejado:', labels)

        if quadrinho!="":
            #Datas
            inicio = st.date_input('Início da Disponibilidade')
            fim = st.date_input('Término da Disponibilidade')
            mes = calendario.get(inicio.month)
            mes_plan = inicio.month
            #Disponibilidades
            ind = f.indisp_quad(inicio.day, fim.day, mes)

            #Planejamento de horas de voo
            df = f.plan(mes_plan)
            quad = f.quad(quadrinho, 'PILOTO', ['IN', 'OP', 'PB', 'AL'])
            quad = quad.reset_index().set_index(1)
            df = quad.join(df).sort_values(by=['Meta','Quadrinhos'], ascending=[False,True]).drop(0,axis=1)
            sebo = f.sebo()
            df = df.join(sebo)
            prioridade = df[df.index.isin(ind, level=0)]
            prioridade = prioridade.reset_index().set_index(9) #rescrever depois
            prioridade.columns = ["Pilotos", "Quadrinhos", 'Meta', 'Horas Voadas','Último Voo']
            prioridade = prioridade[["Pilotos", "Meta", 'Quadrinhos', 'Horas Voadas','Último Voo']]
            prioridade.Meta = prioridade.Meta.astype('int')
            prioridade['Último Voo'] = prioridade['Último Voo'].astype('int')
            prioridade.drop('Horas Voadas', axis=1, inplace=True)


            try:
                st.subheader('Instrutores')
                IN = prioridade.loc['IN'].set_index("Pilotos")
                IN = IN.style.applymap(f.desadapt, subset=['Último Voo'])
                st.table(IN)
            except KeyError:
                st.write("Nenhum piloto disponível.")

            try:
                st.subheader('Operacionais')
                OP = prioridade.loc['OP'].set_index("Pilotos")
                OP = OP.style.applymap(f.desadapt, subset=['Último Voo'])
                st.table(OP)
            except KeyError as err:
                st.write("Nenhum piloto disponível.")

            try:
                st.subheader('Básicos')
                PB = prioridade.loc['PB'].set_index("Pilotos")
                PB = PB.style.applymap(f.desadapt, subset=['Último Voo'])
                st.table(PB)
            except KeyError as err:
                st.write("Nenhum piloto disponível.")

            try:
                st.subheader('Alunos')
                AL = prioridade.loc['AL'].set_index("Pilotos")
                AL = AL.style.applymap(f.desadapt, subset=['Último Voo'])
                st.table(AL)
            except KeyError as err:
                st.write("Nenhum piloto disponível.")

#Page - Plan
if pages == "Planejamento de Missão":
    #Título da página
    st.title('**Planejamento de Missão**')

    #sidebar
    with st.sidebar:
        n_days = st.number_input('Número de Dias', 1)
        tripul = st.number_input('Tripulantes',5)
        aeronave = st.selectbox("Selecione a Aeronave", ['FAB2802','FAB2805','FAB2809'])
        pb = {'FAB2800':12924,'FAB2802':12584,'FAB2803':12587,'FAB2805':12227,'FAB2809':12446}
        PBO = pb.get(aeronave) + 300 + (tripul*100)

    #Importando tabela icao (AJUSTAR ESSE DATAFRAME)
    icao = pd.read_excel("Plan/ICAO.xlsx").set_index("DESIG")
    labels = icao.index.to_list()
    labels.extend(icao.index)
    labels.extend(icao.index)
    labels.extend(icao.index)

    #inputs
    i = 0
    total_plan=[]
    while i < n_days:
        #inputs boxes
        data = st.date_input('Início da Missão', key=f'data_{i}')
        hora = st.time_input('Horário da Decolagem', datetime.time(12, 00), key=f'hora_{i}')
        rota = st.multiselect("Selecione a Rota",labels,["SBMN"], key=f'rota_{i}')
        alternativa = st.multiselect("Selecione as Alternativas",labels,max_selections=(len(rota)-1), key=f'alt_{i}')
        noabast = st.multiselect("Não Abastece",labels, key=f'abast_{i}')

        #plan fuction
        plan = f.braplan(data, hora, rota, alternativa)
        plan = f.disp(plan,noabast, PBO)
        total_plan.append(plan)

        #table check
        st.table(plan)
        check = st.checkbox('Check', key=f'check_{i}')

        if check==True:
            i+=1
            check=False
        else:
            check=False
            break

    #End Plan
    if i==n_days:
        st.title("Planejamento Completo")
        edit = st.checkbox('Editar', key=f'edit')
        end_plan = pd.concat(total_plan)
        if edit==True:
            edit_plan = end_plan.astype(str)
            st.data_editor(edit_plan, hide_index=True)
        else:
            st.table(end_plan)
            # Download button
            csv = f.convert_df(end_plan)
            st.download_button(
                label="Download Excel",
                data=csv,
                file_name='Araraplan.csv',
                mime='text/csv',
            )
