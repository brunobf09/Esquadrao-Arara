#Import
import streamlit as st
import func as f

st.set_page_config(page_title="Esquadrão Arara")

#Page desing
st.title('**Esquadrão Arara**')
st.text('por: Bruno Brasil')
st.image("arara.png")

#options box
options= st.selectbox('Selecione a função desejada:',["","Disponibilidade","Pau de Sebo", "Quadrinhos","Escala"])

calendario = {1:"JANEIRO", 2:"FEVEREIRO", 3:"MARÇO",4:"ABRIL",5:"MAIO",
                  6:"JUNHO",7:"JULHO",8:"AGOSTO",9:"SETEMBRO",10:"OUTUBRO",
                  11:"NOVEMBRO",12:"DEZEMBRO"}

if options == "Disponibilidade":
    inicio = st.date_input('Início da Disponibilidade')
    fim = st.date_input('Término da Disponibilidade')
    mes = calendario.get(inicio.month)

    if fim > inicio:
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
