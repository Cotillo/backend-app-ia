import pandas as pd
import plotly.express as px
import os
import tempfile

def generar_dash_por_variables(df: pd.DataFrame, definiciones: list):
    widgets = []

    for var in definiciones:
        nombre = var["nombre"]
        tipo = var["tipo_confirmado"]

        if tipo == "numérico":
            fig = px.histogram(df, x=nombre, title=f"Distribución de {nombre}")
            widgets.append({"tipo": "histograma", "titulo": fig.layout.title.text})

        elif tipo == "categórico":
            fig = px.pie(df, names=nombre, title=f"Distribución por {nombre}")
            widgets.append({"tipo": "pie_chart", "titulo": fig.layout.title.text})

        elif tipo == "fecha":
            for col in df.columns:
                if df[col].dtype in ["int64", "float64"]:
                    fig = px.line(df.sort_values(by=nombre), x=nombre, y=col, title=f"Evolución de {col} por {nombre}")
                    widgets.append({"tipo": "line_chart", "titulo": fig.layout.title.text})
                    break

    return widgets
