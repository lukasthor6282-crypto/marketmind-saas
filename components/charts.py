import streamlit as st
import plotly.express as px
import pandas as pd


def chart_container(titulo, subtitulo=""):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(15,23,42,0.82), rgba(8,12,24,0.98));
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 24px;
            padding: 20px 20px 12px 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.18);
            margin-bottom: 14px;
        ">
            <div style="
                font-size: 22px;
                font-weight: 800;
                color: #f8fafc;
                margin-bottom: 8px;
            ">
                {titulo}
            </div>
            <div style="
                color:#94a3b8;
                font-size:14px;
                margin-bottom: 10px;
                line-height:1.6;
            ">
                {subtitulo}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def donut_chart(
    labels,
    values,
    center_title="TOTAL",
    center_value="0",
    colors=None,
    height=360
):
    if colors is None:
        colors = ["#22d3ee", "#3b82f6", "#8b5cf6", "#ec4899", "#14b8a6"]

    fig = px.pie(
        names=labels,
        values=values,
        hole=0.74
    )

    fig.update_traces(
        textinfo="none",
        pull=[0.08 if i == 0 else 0.02 for i in range(len(labels))],
        marker=dict(
            colors=colors[:len(labels)],
            line=dict(color="#0f172a", width=6)
        ),
        hovertemplate="<b>%{label}</b><br>%{value}<br>%{percent}<extra></extra>",
        sort=False,
        direction="clockwise",
        rotation=90
    )

    fig.update_layout(
        showlegend=False,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        annotations=[
            dict(
                text=center_title,
                x=0.5,
                y=0.58,
                xanchor="center",
                yanchor="middle",
                showarrow=False,
                font=dict(
                    family="Trebuchet MS",
                    size=11,
                    color="#94a3b8"
                )
            ),
            dict(
                text=str(center_value),
                x=0.5,
                y=0.45,
                xanchor="center",
                yanchor="middle",
                showarrow=False,
                font=dict(
                    family="Arial Black",
                    size=28,
                    color="#f8fafc"
                )
            )
        ]
    )

    return fig


def horizontal_bar_chart(df, x, y, titulo=""):
    fig = px.bar(
        df,
        x=x,
        y=y,
        orientation="h",
        title=titulo
    )

    fig.update_traces(
        marker=dict(
            color=df[x] if x in df.columns else None,
            colorscale=[
                [0.0, "#22d3ee"],
                [0.5, "#3b82f6"],
                [1.0, "#a855f7"]
            ],
            line=dict(color="rgba(255,255,255,0.15)", width=1)
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#E5E7EB"),
        xaxis_title=x,
        yaxis_title="",
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


def ranking_cards(labels, values, colors=None, highlight_first=True):
    if colors is None:
        colors = ["#22d3ee", "#3b82f6", "#8b5cf6", "#ec4899", "#14b8a6"]

    total = sum(values) if values else 0
    cards_html = ""

    for i, (label, value) in enumerate(zip(labels, values)):
        perc = (value / total * 100) if total else 0
        cor = colors[i % len(colors)]
        destaque = "🔥 " if i == 0 and highlight_first else ""

        cards_html += f"""
        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            gap:12px;
            padding:12px 14px;
            border-radius:16px;
            margin-bottom:10px;
            background:rgba(255,255,255,0.03);
            border:1px solid rgba(255,255,255,0.06);
        ">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="
                    width:12px;
                    height:12px;
                    border-radius:999px;
                    background:{cor};
                    box-shadow: 0 0 12px {cor};
                "></div>
                <div style="color:#e2e8f0; font-weight:600;">
                    {destaque}{label}
                </div>
            </div>
            <div style="text-align:right;">
                <div style="color:#fff; font-weight:700;">{value}</div>
                <div style="color:#94a3b8; font-size:12px;">{perc:.1f}%</div>
            </div>
        </div>
        """

    st.markdown(cards_html, unsafe_allow_html=True)