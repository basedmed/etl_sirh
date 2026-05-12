import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
import io
import base64
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import date

# Chargement des données
df_emp = pd.read_csv("output/employes.csv")
df_sal = pd.read_csv("output/salaires.csv")
df_abs = pd.read_csv("output/absences.csv")

# Préparation dates
df_emp["date_embauche"] = pd.to_datetime(df_emp["date_embauche"], errors="coerce")
df_emp["annee_embauche"] = df_emp["date_embauche"].dt.year
today = pd.Timestamp(date.today())
df_emp["anciennete_ans"] = ((today - df_emp["date_embauche"]).dt.days / 365.25).round(1)
df_emp["tranche_anciennete"] = pd.cut(
    df_emp["anciennete_ans"],
    bins=[-1, 1, 3, 5, 100],
    labels=["< 1 an", "1-3 ans", "3-5 ans", "+ 5 ans"]
)

COLORS = {
    "bg":      "#F8F9FA",
    "card":    "#FFFFFF",
    "blue":    "#4361EE",
    "green":   "#4CC9A0",
    "red":     "#F72585",
    "orange":  "#F4A261",
    "purple":  "#7209B7",
    "text":    "#2B2D42",
    "subtext": "#8D99AE",
}

CHART_COLORS = ["#4361EE", "#4CC9A0", "#F72585", "#F4A261", "#7209B7"]

app = Dash(__name__, suppress_callback_exceptions=True)

filiales = ["Toutes"] + sorted(df_emp["subsidiary_id"].unique().tolist())
depts    = ["Tous"]   + sorted(df_emp["departement"].unique().tolist())
niveaux  = ["Tous"]   + sorted(df_emp["niveau"].unique().tolist())
contrats = ["Tous"]   + sorted(df_emp["contrat"].unique().tolist())


def kpi_card(id, color):
    return html.Div(id=id, style={
        "backgroundColor": color, "color": "white",
        "padding": "24px 20px", "borderRadius": "12px",
        "textAlign": "center", "flex": "1", "margin": "8px",
        "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
    })


def filtre(label, id, options, value):
    return html.Div([
        html.Label(label, style={
            "fontWeight": "600", "color": COLORS["text"],
            "fontSize": "13px", "marginBottom": "6px", "display": "block"
        }),
        dcc.Dropdown(
            id=id,
            options=[{"label": o, "value": o} for o in options],
            value=value, clearable=False,
            style={"fontSize": "14px"}
        )
    ], style={"flex": "1", "marginRight": "16px"})


def graph_card(figure):
    return html.Div(dcc.Graph(figure=figure), style={
        "flex": "1", "backgroundColor": COLORS["card"],
        "borderRadius": "12px", "margin": "8px",
        "boxShadow": "0 2px 8px rgba(0,0,0,0.06)", "padding": "8px"
    })


layout_base = dict(
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Segoe UI, Arial", color=COLORS["text"], size=12),
    margin=dict(t=40, b=30, l=30, r=30),
    showlegend=False
)

app.layout = html.Div([

    # Header
    html.Div([
        html.Div([
            html.H1("Dashboard KPIs RH", style={
                "color": COLORS["text"], "margin": "0",
                "fontSize": "26px", "fontWeight": "700"
            }),
            html.P("Suivi des indicateurs sociaux — Multi-filiales 2026", style={
                "color": COLORS["subtext"], "margin": "4px 0 0 0", "fontSize": "14px"
            }),
        ]),
        html.Button(
            "Exporter PDF",
            id="btn-export-pdf",
            style={
                "backgroundColor": COLORS["blue"], "color": "white",
                "border": "none", "padding": "10px 20px",
                "borderRadius": "8px", "cursor": "pointer",
                "fontSize": "14px", "fontWeight": "600",
            }
        ),
        dcc.Download(id="download-pdf"),
    ], style={
        "padding": "28px 32px 16px", "borderBottom": "1px solid #E9ECEF",
        "display": "flex", "justifyContent": "space-between", "alignItems": "center"
    }),

    # Filtres
    html.Div([
        filtre("Filiale",     "filiale-filter", filiales, "Toutes"),
        filtre("Département", "dept-filter",    depts,    "Tous"),
        filtre("Niveau",      "niveau-filter",  niveaux,  "Tous"),
        filtre("Contrat",     "contrat-filter", contrats, "Tous"),
    ], style={"display": "flex", "padding": "16px 32px", "alignItems": "flex-end"}),

    # KPI Cards
    html.Div([
        kpi_card("kpi-effectif", COLORS["blue"]),
        kpi_card("kpi-salaire",  COLORS["green"]),
        kpi_card("kpi-turnover", COLORS["red"]),
        kpi_card("kpi-absences", COLORS["orange"]),
    ], style={"display": "flex", "padding": "0 24px"}),

    # Onglets
    dcc.Tabs(id="onglets", value="effectifs", children=[
        dcc.Tab(label="Effectifs",    value="effectifs"),
        dcc.Tab(label="Rémunération", value="remuneration"),
        dcc.Tab(label="Absentéisme",  value="absenteisme"),
        dcc.Tab(label="Turnover",     value="turnover"),
    ], style={"margin": "16px 32px 0"}),

    # Contenu onglets
    html.Div(id="contenu-onglet", style={"padding": "0 24px 32px"}),

], style={
    "backgroundColor": COLORS["bg"],
    "minHeight": "100vh",
    "fontFamily": "'Segoe UI', Arial, sans-serif"
})


def get_filtered_data(filiale, dept, niveau, contrat):
    emp    = df_emp.copy()
    sal    = df_sal.copy()
    abs_df = df_abs.copy()

    if filiale != "Toutes": emp = emp[emp["subsidiary_id"] == filiale]
    if dept    != "Tous":   emp = emp[emp["departement"]   == dept]
    if niveau  != "Tous":   emp = emp[emp["niveau"]        == niveau]
    if contrat != "Tous":   emp = emp[emp["contrat"]       == contrat]

    ids    = emp["employee_id"].tolist()
    sal    = sal[sal["employee_id"].isin(ids)]
    abs_df = abs_df[abs_df["employee_id"].isin(ids)]

    return emp, sal, abs_df


def kpi_content(valeur, label, indicateur=None):
    children = [
        html.P(str(valeur), style={"fontSize": "32px", "fontWeight": "700", "margin": "0"}),
        html.P(label, style={"fontSize": "13px", "margin": "4px 0 0", "opacity": "0.9"})
    ]
    if indicateur:
        color_ind = "#ff6b6b" if "↑" in indicateur else "#a8e6cf"
        children.append(html.P(indicateur, style={
            "fontSize": "12px", "margin": "4px 0 0",
            "color": color_ind, "fontWeight": "600"
        }))
    return children


@app.callback(
    Output("kpi-effectif", "children"),
    Output("kpi-salaire",  "children"),
    Output("kpi-turnover", "children"),
    Output("kpi-absences", "children"),
    Output("kpi-turnover", "style"),
    Input("filiale-filter", "value"),
    Input("dept-filter",    "value"),
    Input("niveau-filter",  "value"),
    Input("contrat-filter", "value"),
)
def update_kpis(filiale, dept, niveau, contrat):
    emp, sal, abs_df = get_filtered_data(filiale, dept, niveau, contrat)

    effectif    = len(emp)
    salaire_moy = round(sal["salaire_eur"].mean(), 0) if len(sal) > 0 else 0
    turnover    = round(emp["est_parti"].sum() / len(emp) * 100, 1) if len(emp) > 0 else 0
    total_abs   = int(abs_df["duree_jours"].sum())

    ref_turnover = round(df_emp["est_parti"].sum() / len(df_emp) * 100, 1)
    diff_turn    = round(turnover - ref_turnover, 1)
    fleche_turn  = f"↑ +{diff_turn}%" if diff_turn > 0 else f"↓ {diff_turn}%"

    ref_sal   = round(df_sal["salaire_eur"].mean(), 0)
    diff_sal  = round(salaire_moy - ref_sal, 0)
    fleche_sal = f"↑ +{int(diff_sal)}€" if diff_sal > 0 else f"↓ {int(diff_sal)}€"

    turnover_style = {
        "color": "white", "padding": "24px 20px", "borderRadius": "12px",
        "textAlign": "center", "flex": "1", "margin": "8px",
        "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
        "backgroundColor": "#c0392b" if turnover > 10 else COLORS["red"],
        "border": "3px solid #ff0000" if turnover > 10 else "none",
    }

    return (
        kpi_content(effectif, "Effectif total"),
        kpi_content(f"{int(salaire_moy)}€", "Salaire moyen", fleche_sal),
        kpi_content(f"{turnover}%", "Taux de turnover", fleche_turn),
        kpi_content(f"{total_abs:,}", "Jours d'absence"),
        turnover_style
    )


@app.callback(
    Output("contenu-onglet", "children"),
    Input("onglets",         "value"),
    Input("filiale-filter",  "value"),
    Input("dept-filter",     "value"),
    Input("niveau-filter",   "value"),
    Input("contrat-filter",  "value"),
)
def update_onglet(onglet, filiale, dept, niveau, contrat):
    emp, sal, abs_df = get_filtered_data(filiale, dept, niveau, contrat)

    if onglet == "effectifs":
        d1 = emp.groupby("subsidiary_id")["employee_id"].count().reset_index()
        d1.columns = ["Filiale", "Effectif"]
        fig1 = px.bar(d1, x="Filiale", y="Effectif", title="Effectifs par filiale",
                      color_discrete_sequence=CHART_COLORS)
        fig1.update_layout(**layout_base)

        d2 = emp.groupby("genre")["employee_id"].count().reset_index()
        d2.columns = ["Genre", "Nombre"]
        d2["Genre"] = d2["Genre"].map({"M": "Homme", "F": "Femme"})
        fig2 = px.pie(d2, names="Genre", values="Nombre",
                      title="Répartition Hommes / Femmes",
                      color_discrete_sequence=[COLORS["blue"], COLORS["red"]], hole=0.4)
        fig2.update_layout(**layout_base)

        d3 = emp.groupby("contrat")["employee_id"].count().reset_index()
        d3.columns = ["Contrat", "Nombre"]
        fig3 = px.bar(d3, x="Contrat", y="Nombre", title="Répartition par contrat",
                      color_discrete_sequence=CHART_COLORS)
        fig3.update_layout(**layout_base)

        d4 = emp.groupby("tranche_anciennete", observed=True)["employee_id"].count().reset_index()
        d4.columns = ["Tranche", "Nombre"]
        fig4 = px.bar(d4, x="Tranche", y="Nombre", title="Répartition par ancienneté",
                      color_discrete_sequence=[COLORS["purple"]])
        fig4.update_layout(**layout_base)

        cols = ["employee_id", "subsidiary_id", "prenom", "nom",
                "departement", "niveau", "contrat", "anciennete_ans"]
        tableau_df = emp[cols].head(20).copy()
        tableau = dash_table.DataTable(
            data=tableau_df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in cols],
            style_table={"overflowX": "auto"},
            style_cell={
                "fontFamily": "Segoe UI", "fontSize": "13px",
                "padding": "8px 12px", "color": COLORS["text"],
                "border": "1px solid #E9ECEF"
            },
            style_header={
                "backgroundColor": COLORS["bg"], "fontWeight": "600",
                "fontSize": "13px", "border": "1px solid #E9ECEF"
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#F8F9FA"}
            ],
            page_size=10,
        )

        return html.Div([
            html.Div([graph_card(fig1), graph_card(fig2)], style={"display": "flex"}),
            html.Div([graph_card(fig3), graph_card(fig4)], style={"display": "flex"}),
            html.Div([
                html.H3("Détail employés", style={
                    "color": COLORS["text"], "fontSize": "16px",
                    "fontWeight": "600", "margin": "8px 8px 0"
                }),
                html.Div(tableau, style={
                    "backgroundColor": "white", "borderRadius": "12px",
                    "margin": "8px", "boxShadow": "0 2px 8px rgba(0,0,0,0.06)",
                    "padding": "16px"
                })
            ])
        ])

    elif onglet == "remuneration":
        d1 = sal.groupby("subsidiary_id")["salaire_eur"].mean().round(0).reset_index()
        d1.columns = ["Filiale", "Salaire moyen"]
        fig1 = px.bar(d1, x="Filiale", y="Salaire moyen",
                      title="Salaire moyen par filiale (EUR)",
                      color_discrete_sequence=[COLORS["green"]])
        fig1.update_layout(**layout_base)

        d2 = sal.groupby("niveau")["salaire_eur"].mean().round(0).reset_index()
        d2.columns = ["Niveau", "Salaire"]
        d2 = d2.sort_values("Salaire")
        fig2 = px.bar(d2, x="Salaire", y="Niveau", orientation="h",
                      title="Salaire moyen par niveau (EUR)",
                      color_discrete_sequence=[COLORS["purple"]])
        fig2.update_layout(**layout_base)

        d3 = sal.groupby("subsidiary_id")["salaire_eur"].sum().round(0).reset_index()
        d3.columns = ["Filiale", "Masse salariale"]
        fig3 = px.bar(d3, x="Filiale", y="Masse salariale",
                      title="Masse salariale totale par filiale (EUR)",
                      color_discrete_sequence=[COLORS["blue"]])
        fig3.update_layout(**layout_base)

        fig4 = px.histogram(sal, x="salaire_eur", nbins=30,
                            title="Distribution des salaires (EUR)",
                            color_discrete_sequence=[COLORS["orange"]])
        fig4.update_layout(**layout_base)

        return html.Div([
            html.Div([graph_card(fig1), graph_card(fig2)], style={"display": "flex"}),
            html.Div([graph_card(fig3), graph_card(fig4)], style={"display": "flex"}),
        ])

    elif onglet == "absenteisme":
        d1 = abs_df.groupby("subsidiary_id")["duree_jours"].sum().reset_index()
        d1.columns = ["Filiale", "Jours"]
        fig1 = px.bar(d1, x="Filiale", y="Jours",
                      title="Total jours d'absence par filiale",
                      color_discrete_sequence=[COLORS["orange"]])
        fig1.update_layout(**layout_base)

        d2 = abs_df.groupby("type_absence")["duree_jours"].count().reset_index()
        d2.columns = ["Type", "Nombre"]
        fig2 = px.pie(d2, names="Type", values="Nombre", title="Types d'absence",
                      color_discrete_sequence=CHART_COLORS, hole=0.4)
        fig2.update_layout(**layout_base)

        d3 = abs_df.merge(emp[["employee_id", "departement"]], on="employee_id", how="left")
        d3 = d3.groupby("departement")["duree_jours"].sum().reset_index()
        d3.columns = ["Département", "Jours"]
        d3 = d3.sort_values("Jours", ascending=False).head(5)
        fig3 = px.bar(d3, x="Jours", y="Département", orientation="h",
                      title="Top 5 départements — Jours d'absence",
                      color_discrete_sequence=[COLORS["red"]])
        fig3.update_layout(**layout_base)

        jours_theoriques = len(emp) * 220
        taux_abs = round(int(abs_df["duree_jours"].sum()) / jours_theoriques * 100, 2) if jours_theoriques > 0 else 0
        fig4 = px.pie(
            values=[taux_abs, 100 - taux_abs],
            names=["Absent", "Présent"],
            title=f"Taux d'absentéisme : {taux_abs}%",
            color_discrete_sequence=[COLORS["red"], COLORS["green"]],
            hole=0.6
        )
        fig4.update_layout(**layout_base)

        return html.Div([
            html.Div([graph_card(fig1), graph_card(fig2)], style={"display": "flex"}),
            html.Div([graph_card(fig3), graph_card(fig4)], style={"display": "flex"}),
        ])

    elif onglet == "turnover":
        d1 = emp.groupby("subsidiary_id").apply(
            lambda x: round(x["est_parti"].sum() / len(x) * 100, 1)
        ).reset_index()
        d1.columns = ["Filiale", "Turnover"]
        fig1 = px.bar(d1, x="Filiale", y="Turnover", title="Taux de turnover (%)",
                      color_discrete_sequence=[COLORS["red"]])
        fig1.update_layout(**layout_base)
        fig1.add_hline(y=10, line_dash="dash", line_color="gray",
                       annotation_text="Seuil 10%")

        d2 = emp.groupby("annee_embauche").apply(
            lambda x: round(x["est_parti"].sum() / len(x) * 100, 1)
        ).reset_index()
        d2.columns = ["Annee", "Turnover"]
        d2 = d2.dropna().sort_values("Annee")
        fig2 = px.line(d2, x="Annee", y="Turnover",
                       title="Evolution du turnover par année",
                       markers=True, color_discrete_sequence=[COLORS["red"]])
        fig2.update_layout(**layout_base)

        d3 = emp.groupby("subsidiary_id")["anciennete_ans"].mean().round(1).reset_index()
        d3.columns = ["Filiale", "Ancienneté moyenne"]
        fig3 = px.bar(d3, x="Filiale", y="Ancienneté moyenne",
                      title="Ancienneté moyenne par filiale (ans)",
                      color_discrete_sequence=[COLORS["purple"]])
        fig3.update_layout(**layout_base)

        comp = emp.groupby("subsidiary_id").apply(
            lambda x: round(x["est_parti"].sum() / len(x) * 100, 1)
        ).reset_index()
        comp.columns = ["Filiale", "Turnover"]
        fig4 = px.bar(comp, x="Filiale", y="Turnover",
                      title="Comparaison turnover toutes filiales",
                      color="Filiale", color_discrete_sequence=CHART_COLORS)
        fig4.update_layout(**layout_base)
        fig4.update_layout(showlegend=True)

        return html.Div([
            html.Div([graph_card(fig1), graph_card(fig2)], style={"display": "flex"}),
            html.Div([graph_card(fig3), graph_card(fig4)], style={"display": "flex"}),
        ])


@app.callback(
    Output("download-pdf", "data"),
    Input("btn-export-pdf", "n_clicks"),
    prevent_initial_call=True
)
def export_pdf(n_clicks):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Dashboard KPIs RH — Multi-filiales 2026", styles["Title"]))
    elements.append(Spacer(1, 20))

    kpis = [
        ["KPI", "Valeur"],
        ["Effectif total", str(len(df_emp))],
        ["Salaire moyen (EUR)", f"{round(df_sal['salaire_eur'].mean(), 0):.0f}€"],
        ["Taux de turnover", f"{round(df_emp['est_parti'].sum() / len(df_emp) * 100, 1)}%"],
        ["Total jours absence", str(int(df_abs['duree_jours'].sum()))],
    ]
    table = Table(kpis, colWidths=[200, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#4361EE")),
        ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
        ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, -1), 12),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("GRID",           (0, 0), (-1, -1), 0.5, colors.HexColor("#E9ECEF")),
        ("PADDING",        (0, 0), (-1, -1), 10),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Effectifs par filiale", styles["Heading2"]))
    eff = df_emp.groupby("subsidiary_id")["employee_id"].count().reset_index()
    eff_data = [["Filiale", "Effectif"]] + [[str(r[0]), str(r[1])] for r in eff.values.tolist()]
    eff_table = Table(eff_data, colWidths=[150, 100])
    eff_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#4CC9A0")),
        ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
        ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",           (0, 0), (-1, -1), 0.5, colors.HexColor("#E9ECEF")),
        ("PADDING",        (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
    ]))
    elements.append(eff_table)

    doc.build(elements)
    buffer.seek(0)
    pdf_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    return dict(
        content=pdf_base64,
        filename="dashboard_kpis_rh.pdf",
        base64=True,
        type="application/pdf"
    )


if __name__ == "__main__":
    print("Dashboard sur http://127.0.0.1:8050")
    app.run(debug=True)