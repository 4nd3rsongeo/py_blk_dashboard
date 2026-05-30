import streamlit as st
import polars as pl
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os

st.set_page_config(page_title="BLK Dashboarding", layout="wide")

def load_csv(file):
    if file is not None:
        # Polars can read CSVs very efficiently
        return pl.read_csv(file)
    return None

def format_number(val):
    try:
        return f"{int(round(val)):,}".replace(",", " ")
    except:
        return val

def get_table_download_link(df, filename="report.csv"):
    # Convert Polars to CSV for download
    csv = df.write_csv()
    return st.download_button(
        label=f"Download {filename}",
        data=csv,
        file_name=filename,
        mime="text/csv",
    )

# State management
if 'df_blocks' not in st.session_state:
    st.session_state.df_blocks = None
if 'df_db' not in st.session_state:
    st.session_state.df_db = None
if 'mapping' not in st.session_state:
    st.session_state.mapping = {}
if 'color_dict' not in st.session_state:
    st.session_state.color_dict = {}

st.title("📊 BLK Dashboarding (Polars 10GB Optimized)")
st.warning("⚠️ Suporte a arquivos de até 10GB ativado. Certifique-se de que seu sistema possui RAM suficiente (recomenda-se 32GB+ para processamento fluido local).")

# Sidebar for Uploads and Config
with st.sidebar:
    st.header("📁 Upload de Dados")
    uploaded_blocks = st.file_uploader("Subir Modelo de Blocos (CSV)", type="csv")
    uploaded_db = st.file_uploader("Subir Banco de Dados (Opcional) (CSV)", type="csv")
    
    if st.button("Carregar Dataframes"):
        if uploaded_blocks:
            st.session_state.df_blocks = load_csv(uploaded_blocks)
            st.success("Modelo de blocos carregado!")
        if uploaded_db:
            st.session_state.df_db = load_csv(uploaded_db)
            st.success("Banco de dados carregado!")

    if st.session_state.df_blocks is not None:
        df = st.session_state.df_blocks
        st.header("⚙️ Mapeamento de Variáveis")
        cols = df.columns
        num_cols = [c for c, t in zip(df.columns, df.dtypes) if t in [pl.Int64, pl.Float64, pl.Int32, pl.Float32]]
        
        st.session_state.mapping['tonnage_vol'] = st.selectbox("Variável de Tonelagem/Volume", num_cols)
        st.session_state.mapping['is_tonnage'] = st.radio("Tipo", ["Tonelagem", "Volume"])
        
        st.session_state.mapping['grades'] = st.multiselect("Variáveis de Teores", [c for c in num_cols if c != st.session_state.mapping['tonnage_vol']])
        
        grade_units = {}
        for g in st.session_state.mapping['grades']:
            grade_units[g] = st.text_input(f"Unidade para {g}", "pct", key=f"unit_{g}")
        st.session_state.mapping['grade_units'] = grade_units

        st.session_state.mapping['categories'] = st.multiselect("Variáveis de Categoria (Lito/Recurso)", cols, key="cat_sel")
        
        st.session_state.mapping['fractions'] = st.multiselect("Variáveis de Fracionamento (g1, g2...)", num_cols)
        
        st.session_state.mapping['density'] = st.selectbox("Variável de Densidade (Opcional)", ["Nenhuma"] + num_cols)

        st.header("🎨 Cores")
        color_json = st.text_area("Dicionário de Cores (JSON)", "{}")
        try:
            st.session_state.color_dict = json.loads(color_json)
        except:
            st.error("JSON de cores inválido")

# Main Page Tabs
tab_relatorio, tab_dashboard = st.tabs(["📋 Relatórios", "📈 Dashboards"])

if st.session_state.df_blocks is not None:
    df = st.session_state.df_blocks
    mapping = st.session_state.mapping
    
    with tab_relatorio:
        st.header("Relatório do Dataframe")
        
        if mapping.get('categories'):
            st.subheader("Quantidade de Blocos por Categoria")
            counts = df.group_by(mapping['categories']).count().rename({"count": "Contagem"})
            st.table(counts.to_pandas())
            get_table_download_link(counts, "contagem_blocos.csv")
            
            # Contagem de valores não nulos dos teores
            if mapping.get('grades'):
                st.subheader("Contagem de Teores Não Nulos")
                for grade in mapping['grades']:
                    unit = mapping['grade_units'].get(grade, "")
                    st.write(f"**Teor: {grade} ({unit})**")
                    grade_counts = df.group_by(mapping['categories']).agg(
                        pl.col(grade).count().alias("Não Nulos")
                    )
                    col1, col2 = st.columns(2)
                    col1.table(grade_counts.to_pandas())
                    fig = px.bar(grade_counts.to_pandas(), x=mapping['categories'][0], y='Não Nulos', title=f"Contagem de {grade}")
                    col2.plotly_chart(fig, use_container_width=True)
                    get_table_download_link(grade_counts, f"contagem_{grade}.csv")

            # Fracionamento
            if mapping.get('fractions'):
                st.subheader("Análise de Fracionamento")
                for frac in mapping['fractions']:
                    st.write(f"**Fração: {frac}**")
                    f_stats = df.group_by(mapping['categories']).agg([
                        pl.col(frac).count().alias("numeric_count"),
                        pl.col(frac).filter(pl.col(frac) == 0).count().alias("zeros_count")
                    ])
                    st.table(f_stats.to_pandas())
                    get_table_download_link(f_stats, f"fracionamento_{frac}.csv")

            # Tabela de Percentuais
            if mapping.get('grades'):
                st.subheader("Percentual de Blocos com Valor por Categoria")
                total_counts = df.group_by(mapping['categories']).count().rename({"count": "total"})
                
                final_pct = total_counts
                for grade in mapping['grades']:
                    grade_count = df.group_by(mapping['categories']).agg(pl.col(grade).count().alias(grade))
                    final_pct = final_pct.join(grade_count, on=mapping['categories'], how="left")
                    final_pct = final_pct.with_columns((pl.col(grade) / pl.col("total") * 100).alias(grade))
                
                final_pct = final_pct.drop("total")
                st.table(final_pct.to_pandas())
                get_table_download_link(final_pct, "percentuais_teores.csv")

            # Totais de Tonelagem/Volume
            st.subheader(f"Totais de {mapping['tonnage_vol']}")
            ton_totals = df.group_by(mapping['categories']).agg(
                pl.col(mapping['tonnage_vol']).sum().alias(mapping['tonnage_vol'])
            )
            # Formatting for display
            display_ton = ton_totals.to_pandas()
            display_ton[mapping['tonnage_vol']] = display_ton[mapping['tonnage_vol']].apply(format_number)
            st.table(display_ton)
            get_table_download_link(ton_totals, f"totais_{mapping['tonnage_vol']}.csv")

            # Extrapolação (se DB carregado)
            if st.session_state.df_db is not None and mapping.get('grades'):
                st.subheader("Validação de Extrapolação (Modelo vs DB)")
                df_db = st.session_state.df_db
                anomalies = []
                anomaly_blocks = []
                
                for grade in mapping['grades']:
                    db_grade_col = next((c for c in df_db.columns if c.lower() == grade.lower()), None)
                    if db_grade_col:
                        # Find common categories between model and DB
                        common_cats = [c for c in mapping['categories'] if any(dc.lower() == c.lower() for dc in df_db.columns)]
                        
                        if common_cats:
                            # Group DB and Model to compare min/max
                            db_stats = df_db.group_by(common_cats).agg([
                                pl.col(db_grade_col).min().alias("db_min"),
                                pl.col(db_grade_col).max().alias("db_max")
                            ])
                            
                            mod_stats = df.group_by(mapping['categories']).agg([
                                pl.col(grade).min().alias("mod_min"),
                                pl.col(grade).max().alias("mod_max"),
                                pl.col(grade).count().alias("mod_count")
                            ])
                            
                            # Join and find anomalies
                            joined = mod_stats.join(db_stats, on=common_cats, how="left")
                            bad = joined.filter((pl.col("mod_min") < pl.col("db_min")) | (pl.col("mod_max") > pl.col("db_max")))
                            
                            if not bad.is_empty():
                                st.write(f"**Alertas de Extrapolação para {grade}:**")
                                st.table(bad.to_pandas())
                                # Logic to get actual blocks is expensive on 5GB, maybe just export the stats
                                get_table_download_link(bad, f"anomalias_{grade}.csv")

            # Teores Negativos
            if mapping.get('grades'):
                st.subheader("Teores Negativos")
                neg_data = []
                for grade in mapping['grades']:
                    neg_counts = df.filter(pl.col(grade) < 0).group_by(mapping['categories']).count().rename({"count": f"{grade}_negativos"})
                    if not neg_counts.is_empty():
                        neg_data.append(neg_counts)
                if neg_data:
                    # Join negative data
                    res_neg = neg_data[0]
                    for d in neg_data[1:]:
                        res_neg = res_neg.join(d, on=mapping['categories'], how="outer")
                    st.table(res_neg.to_pandas())
                    get_table_download_link(res_neg, "teores_negativos.csv")
                else:
                    st.info("Nenhum teor negativo encontrado.")

            # Estatística Descritiva
            st.subheader("Estatística Descritiva dos Teores")
            for grade in mapping['grades']:
                st.write(f"**{grade}**")
                desc = df.group_by(mapping['categories']).agg([
                    pl.col(grade).count().alias("count"),
                    pl.col(grade).mean().alias("mean"),
                    pl.col(grade).std().alias("std"),
                    pl.col(grade).min().alias("min"),
                    pl.col(grade).quantile(0.25).alias("25%"),
                    pl.col(grade).quantile(0.5).alias("50%"),
                    pl.col(grade).quantile(0.75).alias("75%"),
                    pl.col(grade).max().alias("max")
                ])
                st.table(desc.to_pandas())
                get_table_download_link(desc, f"descritiva_{grade}.csv")

    with tab_dashboard:
        st.header("Dashboards Interativos")
        
        # Note: Plotly needs pandas, so we convert only the necessary summary data
        if mapping.get('categories'):
            # Treemap
            st.subheader("Totais por Categoria (Treemap)")
            tree_data = df.group_by(mapping['categories']).agg(pl.col(mapping['tonnage_vol']).sum()).to_pandas()
            try:
                fig_tree = px.treemap(tree_data, path=mapping['categories'], values=mapping['tonnage_vol'], 
                                     color_discrete_map=st.session_state.color_dict)
                st.plotly_chart(fig_tree, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar Treemap: {e}")
            
            # Gráfico de Colunas por Recurso
            recurso_col = next((c for c in mapping['categories'] if 'recurso' in c.lower()), None)
            if recurso_col:
                st.subheader(f"Totais por {recurso_col}")
                res_totals = df.group_by(recurso_col).agg(pl.col(mapping['tonnage_vol']).sum()).to_pandas()
                fig_col = px.bar(res_totals, x=recurso_col, y=mapping['tonnage_vol'], 
                                color=recurso_col, color_discrete_map=st.session_state.color_dict)
                st.plotly_chart(fig_col, use_container_width=True)

            # Curva Teor-Tonelagem
            if mapping.get('grades'):
                st.subheader("Curva Teor-Tonelagem")
                selected_grade = st.selectbox("Selecionar Teor para Curva", mapping['grades'])
                
                lito_col = mapping['categories'][0] 
                litos = df[lito_col].unique().to_list()
                
                # Sample the dataset if it's too large for the curve calculation in real-time
                # Or calculate in a more optimized way
                cutoffs = np.linspace(df[selected_grade].min(), df[selected_grade].max(), 20)
                curve_data = []
                
                for lito in litos:
                    lito_df = df.filter(pl.col(lito_col) == lito)
                    for cut in cutoffs:
                        filtered = lito_df.filter(pl.col(selected_grade) >= cut)
                        if not filtered.is_empty():
                            ton = filtered[mapping['tonnage_vol']].sum()
                            # Weighted average
                            avg_grade = (filtered[selected_grade] * filtered[mapping['tonnage_vol']]).sum() / ton
                            curve_data.append({'Lito': lito, 'Cutoff': cut, 'Tonnage': ton, 'Avg Grade': avg_grade})
                
                df_curve = pd.DataFrame(curve_data) if curve_data else pd.DataFrame()
                if not df_curve.empty:
                    fig_curve = go.Figure()
                    for lito in df_curve['Lito'].unique():
                        l_df = df_curve[df_curve['Lito'] == lito]
                        fig_curve.add_trace(go.Scatter(x=l_df['Cutoff'], y=l_df['Tonnage'], name=f"{lito} - Ton", mode='lines'))
                        fig_curve.add_trace(go.Scatter(x=l_df['Cutoff'], y=l_df['Avg Grade'], name=f"{lito} - Grade", mode='lines', yaxis='y2'))
                    
                    fig_curve.update_layout(
                        yaxis=dict(title="Tonelagem"),
                        yaxis2=dict(title="Teor Médio", overlaying='y', side='right'),
                        title=f"Curva Teor-Tonelagem para {selected_grade}"
                    )
                    st.plotly_chart(fig_curve, use_container_width=True)

            # Histograma
            st.subheader("Histograma Interativo")
            hist_grade = st.selectbox("Teor para Histograma", mapping['grades'], key="hist_grade")
            lito_options = df[mapping['categories'][0]].unique().to_list()
            lito_filter = st.multiselect("Filtrar Categoria", lito_options, default=lito_options)
            
            # For histogram of 5GB, we MUST sample or bin first.
            # Let's take a sample of 100k blocks for the visual histogram if it's too big
            if df.height > 100000:
                st.warning("Dataset muito grande. Exibindo histograma baseado em amostra de 100.000 blocos.")
                filtered_hist = df.filter(pl.col(mapping['categories'][0]).is_in(lito_filter)).sample(n=100000, seed=42).to_pandas()
            else:
                filtered_hist = df.filter(pl.col(mapping['categories'][0]).is_in(lito_filter)).to_pandas()
                
            fig_hist = px.histogram(filtered_hist, x=hist_grade, color=mapping['categories'][0], 
                                   marginal="box", color_discrete_map=st.session_state.color_dict)
            st.plotly_chart(fig_hist, use_container_width=True)

else:
    st.info("Por favor, carregue um arquivo CSV de modelo de blocos para começar.")
