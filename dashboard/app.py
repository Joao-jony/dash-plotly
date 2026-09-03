from dash import Dash, html, Input, Output, dcc
import plotly.express as px
import pandas as pd
import os

df_vendas = pd.read_csv("../csv_arq/sales.csv")
df_vendas["Data da Encomenda"] = pd.to_datetime(df_vendas["Data da Encomenda"], format="%d/%m/%Y")
df_vendas["Data de Expedição"] = pd.to_datetime(df_vendas["Data de Expedição"], format="%d/%m/%Y")
df_vendas["Dias"] = (df_vendas["Data de Expedição"] - df_vendas["Data da Encomenda"]).dt.days

df_receitas_total = df_vendas.groupby("Região", as_index=False)["Receita Total"].sum().sort_values("Receita Total", ascending=False)
df_receita_total_itens = df_vendas.groupby("Tipo de Item", as_index=False)[["Receita Total", "Lucro Total"]].sum().sort_values("Receita Total", ascending=False)
df_receita_canal = df_vendas.groupby("Canal de Venda", as_index=False)["Receita Total"].sum()
df_receita_por_prioridade = df_vendas.groupby("Prioridade da Encomenda", as_index=False)["Receita Total"].sum()
df_vendas["Mes"] = df_vendas["Data da Encomenda"].dt.to_period("M").astype(str)
df_data = df_vendas.groupby("Mes", as_index=False)[["Receita Total", "Lucro Total", "Custo Total"]].sum().sort_values("Mes")
df_receita_pais = df_vendas.groupby("País", as_index=False)["Receita Total"].sum().sort_values("Receita Total", ascending=False).head(15)
df_receita_regiao_pais_item = df_vendas.groupby(["Região", "Tipo de Item"], as_index=False)["Receita Total"].sum()
df_receita_preco_custo_margem = df_vendas.drop(columns=["Região", "Canal de Venda", "Prioridade da Encomenda", "Mes", "ID da Encomenda", "Data da Encomenda", "Data de Expedição", "Lucro Total", "Custo Total"])
df_receita_lucro_custo_total = df_vendas.groupby("Região", as_index=False)[["Receita Total", "Lucro Total", "Custo Total"]].sum()
df_rcl = df_receita_lucro_custo_total.melt(id_vars='Região', var_name='Categoria', value_name='Valor')
df_rcl = df_rcl.groupby(["Região", "Categoria"], as_index=False)["Valor"].sum()
df_por_pais = df_vendas.groupby("País", as_index=False)[["Receita Total", "Lucro Total", "Custo Total"]].sum().sort_values("Receita Total", ascending=False).head(20)
df_rcl_por_pais = df_por_pais.melt(id_vars='País', var_name='Categoria', value_name='Valor')
df_rcl_por_pais = df_rcl_por_pais.groupby(["País", "Categoria"], as_index=False)["Valor"].sum()
df_sub_pizza = df_vendas

app = Dash(__name__)
server = app.server  

app.layout = html.Div([
    html.Nav(
        [
            html.H2("Dashboard"),

            html.A("Receitas", href="#receitas"),
            html.A("Receita, Lucros e Custos", href="#comp"),
            html.A("Região - País", href="#pais"),
            html.A("Preço, Custo e Unidades Vendidas", href="#pcuv"),
            html.A("Logistica", href="#log")
        ],
        className="sidebar"
    ),
    html.Main(
        [
            html.H1("Análise de Vendas á nivel global"),
            html.Section(
                [
                    html.H1("Receitas"),
                    dcc.Dropdown(
                        id="Receitas_filtros1",
                        options=[
                            {
                                "label": "Todas as Regiões",
                                "value": "Todas Regiões"
                            }
                        ] + [{
                            "label": reg,
                            "value": reg
                            } 
                            for reg in df_receitas_total['Região'].unique()],
                        value="Todas Regiões",
                        clearable=False,
                        multi=True,
                        style={"width": "50%", "margin": "auto"}
                    ),
                    dcc.Graph(id="grafico_receita1"),

                    dcc.Dropdown(
                        id="itemfiltro",
                        options=[
                            {
                                "label": "Todos os Itens",
                                "value": "Todos Itens"
                            }
                        ] + [{
                            "label": item,
                            "value": item
                        } for item in df_receita_total_itens['Tipo de Item'].unique()],
                        value="Todos Itens",
                        clearable=False,
                        multi=True,
                        style={"width": "50%", "margin": "auto"}
                    ),
                    dcc.Graph(id="grafico_receita_item"),

                    dcc.Graph(id="grafico_canal"),

                    dcc.Dropdown(
                        id="prioridade",
                        options=[
                            {
                                "label": "Todas as Prioridades",
                                "value": "Todas Prioridades"
                            }
                        ] + [{
                            "label": prio,
                            "value": prio
                            }
                            for prio in df_receita_por_prioridade['Prioridade da Encomenda'].unique()],
                        value="Todas Prioridades",
                        clearable=False,
                        style={"width": "50%", "margin": "auto"}
                    ),
                    dcc.Graph(id="grafico_prioridade")
                ],
                id="receitas"
            ),

            html.Section(
                [
                    html.H1("Comparação( Receita, Lucro e custos)"),
                    dcc.Dropdown(
                        id="comparacao",
                        options=[
                            {
                                "label": "Receita Total",
                                "value": "Receita Total"
                            },
                            {
                                "label": "Lucro Total",
                                "value": "Lucro Total"
                            },
                            {
                                "label": "Custo Total",
                                "value": "Custo Total"
                            }
                        ],
                        value=[
                            "Receita Total",
                            "Lucro Total",
                            "Custo Total"
                        ],
                        multi=True,
                        clearable=False,
                        style={"width": "50%",  "margin": "auto"}
                    ),
                    
                    dcc.DatePickerRange(
                        id="periodo_data",
                        min_date_allowed=df_vendas["Data da Encomenda"].min(),
                        max_date_allowed=df_vendas["Data da Encomenda"].max(),
                        start_date=df_vendas["Data da Encomenda"].min(),
                        end_date=df_vendas["Data da Encomenda"].max(),
                        display_format="DD/MM/YYYY",
                        style={ "margin": "20px auto", "display": "block", "width": "50%"
                        }
                    ),
                    dcc.Graph(id="grafico_comparacao"),

                    dcc.Dropdown(
                        id="receita_lucro_custo_bar",
                        options=[
                            {
                                "label": "Todas as Regiões",
                                "value": "Todas Regiões"
                            }
                        ] + [{
                            "label": rlc_total,
                            "value": rlc_total
                        } for rlc_total in df_rcl['Região'].unique()],
                        value="Todas Regiões",
                        multi=True,
                        clearable=False,
                        style={"width": "50%",  "margin": "auto"}
                    ),
                    dcc.Graph(id="receita_lucro_custo_graf")
                ],
                id="comp"
            ),

            html.Section(
                [
                    html.H1("Análise por Região-País"),
                    dcc.Dropdown(
                        id="pais_lucro",
                        options=[
                            {
                                "label": "Todas os Paises",
                                "value": "Todos Paises"
                            }
                        ] + [{
                            "label": pais,
                            "value": pais
                            }
                            for pais in df_receita_pais['País'].unique()],
                        value="Todos Paises",
                        multi=True,
                        clearable=False,
                        style={"width": "50%", "margin": "auto"}
                    ),
                    dcc.Graph(id="grafico_pais_receita"),
                    dcc.Dropdown(
                        id="receita_lucro_custo_bar_pais",
                        options=[
                            {
                                "label": "Todos os Paises",
                                "value": "Todos Paises"
                            }
                        ] + [{
                            "label": rlc_total_pais,
                            "value": rlc_total_pais
                        } for rlc_total_pais in df_rcl_por_pais['País'].unique()],
                        value="Todos Paises",
                        multi=True,
                        clearable=False,
                        style={"width": "50%",  "margin": "auto"}
                    ),
                    dcc.Graph(id="receita_lucro_custo_pais_graf"),

                    dcc.Dropdown(
                        id="map_região_itens",
                        options=[
                            {
                                "label": "Todas as Regiões",
                                "value": "Todas Regiões"
                            }
                        ] + [{
                            "label": treg,
                            "value": treg
                        } for treg in df_receita_regiao_pais_item['Região'].unique()],
                        value="Todas Regiões",
                        multi=True,
                        clearable=False,
                        style={"width": "50%", "margin": "auto"}
                    ),
                    dcc.Graph(id="map_região_itens_receita")
                ],
                id="pais"
            ),

            html.Section(
                [
                    html.H1("Logisticas"),
                    dcc.Graph(id="dia_entre_histo"),
                    dcc.RadioItems(
                        id="sel_canal",
                        options=[
                            {
                                "label": "Todos os Canais",
                                "value": "Todos Canais"
                            }
                        ] + [{
                            "label": canais_sel,
                            "value": canais_sel
                        }for canais_sel in df_vendas['Canal de Venda'].unique()],
                        value="Todos Canais",
                        labelStyle={'display': 'flex', 'margin': '0 15px', 'fontSize': '14px'}
                    ),
                    dcc.Graph(id="sel_canal_graf")
                ],
                id="log"
            )
        ],
        className="content"
    )
])

@app.callback(
    Output("grafico_receita1", "figure"),
    Input("Receitas_filtros1", "value"),
)

def act_grafico(Regiao):
    if not Regiao or "Todas Regiões" in Regiao:
        df_filtro = df_receitas_total
    else:
        df_filtro = df_receitas_total[df_receitas_total["Região"].isin(Regiao)]

    fig = px.bar(
        df_filtro,
        x="Região",
        y="Receita Total",
        color="Região",
        title=f"Vendas por Região - {Regiao}",
        template="plotly_white",
        text_auto=True
    )
    return fig

@app.callback(
    Output("grafico_receita_item", "figure"),
    Input("itemfiltro", "value")
)

def act_grafico_Item(Item):
    if not Item or "Todos Itens" in Item:
        df_filtro = df_receita_total_itens
    else:
        df_filtro = df_receita_total_itens[df_receita_total_itens["Tipo de Item"].isin(Item)]

    fig = px.bar(
        df_filtro,
        x="Receita Total",
        y="Tipo de Item",
        orientation="h",
        title=f"Receita e Lucro por Tipo de Item - {Item}",
        color="Lucro Total",
        color_continuous_scale="Tealgrn",
        template="plotly_white",
        text_auto=True
    )
        
    return fig

@app.callback(
    Output("grafico_canal", "figure"),
    Input("grafico_receita1", "figure")
)
def act_grafico_Canal(_):

    fig = px.pie(
        df_receita_canal,
        names="Canal de Venda",
        values="Receita Total",
        hole=0.5,
        title="Distribuição da Receita por Canal de Venda"
    )

    return fig


@app.callback(
    Output("grafico_prioridade", "figure"),
    Input("prioridade", "value"),
)

def act_grafico_prio(Canal):
    if not Canal or "Todas Prioridades" in Canal:
        df_filtro = df_receita_por_prioridade
    else:
        df_filtro = df_receita_por_prioridade[df_receita_por_prioridade['Prioridade da Encomenda'] == Canal]
    
    fig = px.bar(
        df_filtro,
        x="Prioridade da Encomenda",
        y="Receita Total",
        color="Prioridade da Encomenda",
        title=f"Receita por Prioridade da Encomenda - {Canal}",
        template="plotly_white",
        text_auto=True
    )
        
    return fig

@app.callback(
    Output("grafico_comparacao", "figure"),
    Input("comparacao", "value"),
    Input("periodo_data", "start_date"),
    Input("periodo_data", "end_date")
)

def act_grafico_comparacao(metricas, data_inicio, data_fim):

    df_filtro = df_vendas.copy()

    df_filtro = df_filtro[(df_filtro["Data da Encomenda"] >= pd.to_datetime(data_inicio)) & (df_filtro["Data da Encomenda"] <= pd.to_datetime(data_fim))]
    df_mensal = (df_filtro.assign(Mês=df_filtro["Data da Encomenda"].dt.to_period("M").astype(str)).groupby("Mês", as_index=False)[["Receita Total","Lucro Total","Custo Total"]].sum().sort_values("Mês"))

    fig_mensal = px.line(
        df_mensal,
        x="Mês",
        y=metricas if isinstance(metricas, list) else [metricas],
        title="Receita, Lucro e Custo por Mês",
        template="plotly_white",
        markers=True
    )
    
    fig_mensal.update_layout(
        xaxis_title="Mês",
        yaxis_title="",
        hovermode="x unified",
        legend_title="Métricas"
    )

    return fig_mensal

@app.callback(
    Output("grafico_pais_receita", "figure"),
    Input("pais_lucro", "value")
)

def act_grafico_Pais(receita_pais):
    if not receita_pais or "Todos Paises" in receita_pais:
        df_filtro = df_receita_pais
    else:
        df_filtro = df_receita_pais[df_receita_pais["País"].isin(receita_pais)]

    fig = px.bar(
        df_filtro,
        x="Receita Total",
        y="País",
        color="Receita Total",
        orientation="h",
        title=f"Receita por País - {receita_pais}",
        color_continuous_scale="Tealgrn",
        template="plotly_white",
        text_auto=True
    )
    fig.update_layout(
        yaxis=dict(categoryorder="total ascending")
    )
        
    return fig

@app.callback(
    Output("map_região_itens_receita", "figure"),
    Input("map_região_itens", "value")
)

def act_grafico_regiao_item_map(regiao_item):
    if not regiao_item or "Todas Regiões" in regiao_item:
        df_filtro = df_receita_regiao_pais_item
    else:
        df_filtro = df_receita_regiao_pais_item[df_receita_regiao_pais_item["Região"].isin(regiao_item)]
    
    fig = px.treemap(
        df_filtro,
        path=["Região", "Tipo de Item"],
        values="Receita Total",
        title=f"Receita por Região e Tipo de Item - {regiao_item}",
        color="Receita Total",
        color_continuous_scale="Tealgrn",
    )
    return fig

@app.callback(
    Output("receita_lucro_custo_graf", "figure"),
    Input("receita_lucro_custo_bar", "value")
)
def act_grafico_rcl_total(rcl_total):
    if not rcl_total or "Todas Regiões" in rcl_total:
        df_filtro = df_rcl
    else:
        df_filtro = df_rcl[df_rcl["Região"].isin(rcl_total)]
    
    fig = px.bar(
        df_filtro,
        x="Região",
        y="Valor",
        barmode="group",
        title=f"Receita, Lucro e Custo por Região - {rcl_total}",
        color="Categoria",
        template="plotly_white",
        text_auto=True
    )

    return fig

@app.callback(
    Output("receita_lucro_custo_pais_graf", "figure"),
    Input("receita_lucro_custo_bar_pais", "value")
)
def act_grafico_rcl_total_pais(rcl_total_pais):
    if not rcl_total_pais or "Todos Paises" in rcl_total_pais:
        df_filtro = df_rcl_por_pais
    else:
        df_filtro = df_rcl_por_pais[df_rcl_por_pais["País"].isin(rcl_total_pais)]
    
    fig = px.bar(
        df_filtro,
        x="País",
        y="Valor",
        barmode="group",
        title=f"Receita, Lucro e Custo por País - {rcl_total_pais}",
        color="Categoria",
        template="plotly_white",
        text_auto=True
    )

    return fig

@app.callback(
    Output("dia_entre_histo", "figure"),
    Input("sel_canal", "value")
)

def histgrafico(_):

    fig = px.histogram(
        df_vendas,
        x="Dias",
        nbins=20,
        title="Distribuição dos Dias de Envio",
        template="plotly_white",
        color="Dias"
    )
    return fig

@app.callback(
    Output("sel_canal_graf", "figure"),
    Input("sel_canal", "value")
)

def ac_graf_canal(todos_canal):
    if todos_canal == "Todos Canais":
        df_filtro = df_vendas
    else:
        df_filtro = df_vendas[df_vendas['Canal de Venda'] == todos_canal]

    fig = px.sunburst(
        df_filtro, 
        path=["Canal de Venda", "Prioridade da Encomenda", "Tipo de Item"],
        values="Receita Total", 
        title=f"Grafico: Canal -> Prioridade -> Tipo de Item - {todos_canal}",
        template="plotly_white",
        color="Canal de Venda"
    )
    return fig

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))