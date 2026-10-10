"""Dashboard Streamlit — Dengue no Brasil (2022–2025), dados no MongoDB Atlas.

Execução:  MONGO_URI="mongodb+srv://..." streamlit run app.py
(ou defina MONGO_URI em .streamlit/secrets.toml)
"""
import os
import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from pymongo import MongoClient
from streamlit_folium import st_folium

DB_NAME, COL_NAME = "dengue_br", "casos"

UF = {
    11: ("RO", "Norte"), 12: ("AC", "Norte"), 13: ("AM", "Norte"), 14: ("RR", "Norte"),
    15: ("PA", "Norte"), 16: ("AP", "Norte"), 17: ("TO", "Norte"),
    21: ("MA", "Nordeste"), 22: ("PI", "Nordeste"), 23: ("CE", "Nordeste"),
    24: ("RN", "Nordeste"), 25: ("PB", "Nordeste"), 26: ("PE", "Nordeste"),
    27: ("AL", "Nordeste"), 28: ("SE", "Nordeste"), 29: ("BA", "Nordeste"),
    31: ("MG", "Sudeste"), 32: ("ES", "Sudeste"), 33: ("RJ", "Sudeste"), 35: ("SP", "Sudeste"),
    41: ("PR", "Sul"), 42: ("SC", "Sul"), 43: ("RS", "Sul"),
    50: ("MS", "Centro-Oeste"), 51: ("MT", "Centro-Oeste"), 52: ("GO", "Centro-Oeste"),
    53: ("DF", "Centro-Oeste"),
}


CENTROS = {
    "Norte": (-3.9, -61.4), "Nordeste": (-9.6, -40.5), "Centro-Oeste": (-15.6, -54.3),
    "Sudeste": (-20.5, -45.0), "Sul": (-26.3, -51.5),
}

CIDADES_SUL = {
    410690: ("Curitiba", "PR", -25.4284, -49.2733),
    411370: ("Londrina", "PR", -23.3045, -51.1696),
    411520: ("Maringá", "PR", -23.4205, -51.9331),
    420540: ("Florianópolis", "SC", -27.5954, -48.5480),
    420910: ("Joinville", "SC", -26.3045, -48.8487),
    420240: ("Blumenau", "SC", -26.9194, -49.0661),
    431490: ("Porto Alegre", "RS", -30.0346, -51.2177),
    430510: ("Caxias do Sul", "RS", -29.1678, -51.1794),
    431440: ("Pelotas", "RS", -31.7654, -52.3376),
    430460: ("Canoas", "RS", -29.9178, -51.1839),
}


st.set_page_config(page_title="Dengue no Brasil", layout="wide")
st.title("Dengue no Brasil — casos 2022–2025")
st.caption("Fonte: Ministério da Saúde / SINAN (OpenDataSUS). Dados armazenados no MongoDB Atlas.")


@st.cache_resource
def get_col():
    uri = os.environ.get("MONGO_URI") or st.secrets.get("MONGO_URI")
    if not uri:
        st.error("Defina a variável de ambiente MONGO_URI.")
        st.stop()
    return MongoClient(uri)[DB_NAME][COL_NAME]


col = get_col()


@st.cache_data(ttl=600)
def consulta(pipeline_json: str):
    import json
    return list(col.aggregate(json.loads(pipeline_json)))


def agg(pipeline):
    import json
    return pd.DataFrame(consulta(json.dumps(pipeline)))


anos = sorted(col.distinct("ano"))
escolhidos = st.sidebar.multiselect("Anos", anos, default=anos)
if not escolhidos:
    st.warning("Selecione ao menos um ano.")
    st.stop()
filtro = {"$match": {"ano": {"$in": escolhidos}}}


total = agg([filtro, {"$group": {"_id": "$regiao", "total": {"$sum": "$casos"}}}]).rename(columns={"_id": "regiao"})
media = agg([
    filtro,
    {"$group": {"_id": {"regiao": "$regiao", "uf": "$uf"}, "t": {"$sum": "$casos"}}},
    {"$group": {"_id": "$_id.regiao", "media_por_estado": {"$avg": "$t"}}},
]).rename(columns={"_id": "regiao"})

c = st.columns(len(total))
for slot, (_, r) in zip(c, total.sort_values("total", ascending=False).iterrows()):
    slot.metric(r["regiao"], f"{int(r['total']):,}".replace(",", "."))

esq, dir_ = st.columns(2)
with esq:
    st.subheader("Soma de casos por região")
    m = folium.Map(location=[-14.5, -52], zoom_start=4, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", attr="Esri")
    mx = total["total"].max()
    for _, r in total.iterrows():
        lat, lon = CENTROS[r["regiao"]]
        folium.CircleMarker([lat, lon], radius=8 + 32 * (r["total"] / mx) ** 0.5, color="#b30000",
                            fill=True, fill_opacity=0.45,
                            tooltip=f"{r['regiao']}: {int(r['total']):,}".replace(",", ".")).add_to(m)
        folium.Marker([lat, lon], icon=folium.DivIcon(html=(
            f"<div style='font:700 12px sans-serif;text-align:center;width:120px;margin-left:-60px;"
            f"margin-top:-8px'>{r['regiao']}<br>{int(r['total']):,}</div>".replace(",", ".")))).add_to(m)
    st_folium(m, height=450, use_container_width=True, returned_objects=[])
with dir_:
    st.subheader("Média de casos por estado, por região")
    fig = px.bar(media.sort_values("media_por_estado", ascending=False), x="regiao", y="media_por_estado",
                 text_auto=",.0f", labels={"regiao": "Região", "media_por_estado": "Média por estado"})
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Soma-se cada estado e tira-se a média entre os estados da região.")

st.subheader("Região Sul — grandes cidades")
cid = agg([filtro, {"$match": {"regiao": "Sul", "id_municipio": {"$in": list(CIDADES_SUL)}}},
           {"$group": {"_id": "$id_municipio", "casos": {"$sum": "$casos"}}}]).rename(columns={"_id": "id_municipio"})
if cid.empty:
    st.info("Sem dados para as cidades selecionadas.")
else:
    cid["cidade"] = cid["id_municipio"].map(lambda k: f"{CIDADES_SUL[k][0]}/{CIDADES_SUL[k][1]}")
    a, b = st.columns([3, 2])
    with a:
        m2 = folium.Map(location=[-27.8, -51.0], zoom_start=6, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", attr="Esri")
        mx = max(cid["casos"].max(), 1)
        for _, r in cid.iterrows():
            nome, uf, lat, lon = CIDADES_SUL[r["id_municipio"]]
            folium.CircleMarker([lat, lon], radius=6 + 28 * (r["casos"] / mx) ** 0.5, color="#b30000",
                                fill=True, fill_opacity=0.5,
                                tooltip=f"{nome}/{uf}: {int(r['casos']):,}".replace(",", ".")).add_to(m2)
        st_folium(m2, height=450, use_container_width=True, returned_objects=[])
    with b:
        st.dataframe(cid.sort_values("casos", ascending=False)[["cidade", "casos"]], hide_index=True,
                     use_container_width=True)
