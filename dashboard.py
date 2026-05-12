import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import os

# Chargement des données
df_emp = pd.read_csv("output/employes.csv")
df_sal = pd.read_csv("output/salaires.csv")
df_abs = pd.read_csv("output/absences.csv")

# Style
sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = "DejaVu Sans"

# Calculs KPIs
effectifs = df_emp.groupby("subsidiary_id")["employee_id"].count().reset_index()
effectifs.columns = ["Filiale", "Effectif"]

salaire_moyen = df_sal.groupby("subsidiary_id")["salaire_eur"].mean().round(0).reset_index()
salaire_moyen.columns = ["Filiale", "Salaire moyen (EUR)"]

turnover = df_emp.groupby("subsidiary_id").apply(
    lambda x: round(x["est_parti"].sum() / len(x) * 100, 1)
).reset_index()
turnover.columns = ["Filiale", "Turnover (%)"]

absences = df_abs.groupby("subsidiary_id")["duree_jours"].sum().reset_index()
absences.columns = ["Filiale", "Jours absence"]

type_absence = df_abs.groupby("type_absence")["duree_jours"].count().reset_index()
type_absence.columns = ["Type", "Nombre"]

salaire_niveau = df_sal.groupby("niveau")["salaire_eur"].mean().round(0).reset_index()
salaire_niveau.columns = ["Niveau", "Salaire moyen (EUR)"]
ordre = ["Stagiaire", "Junior", "Confirme", "Senior", "Manager", "Directeur"]
salaire_niveau = salaire_niveau.sort_values("Salaire moyen (EUR)")

# Dashboard
fig = plt.figure(figsize=(18, 12))
fig.suptitle("Dashboard KPIs RH — Multi-filiales 2026", fontsize=18, fontweight="bold", y=0.98)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

# 1. Effectifs par filiale
ax1 = fig.add_subplot(gs[0, 0])
bars = ax1.bar(effectifs["Filiale"], effectifs["Effectif"], color=sns.color_palette("Blues_d", len(effectifs)))
ax1.set_title("Effectifs par filiale", fontweight="bold")
ax1.set_xlabel("Filiale")
ax1.set_ylabel("Nombre d'employes")
for bar in bars:
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             str(int(bar.get_height())), ha="center", va="bottom", fontsize=9)

# 2. Salaire moyen par filiale
ax2 = fig.add_subplot(gs[0, 1])
bars2 = ax2.bar(salaire_moyen["Filiale"], salaire_moyen["Salaire moyen (EUR)"],
                color=sns.color_palette("Greens_d", len(salaire_moyen)))
ax2.set_title("Salaire moyen par filiale (EUR)", fontweight="bold")
ax2.set_xlabel("Filiale")
ax2.set_ylabel("EUR")
for bar in bars2:
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
             f"{int(bar.get_height())}€", ha="center", va="bottom", fontsize=9)

# 3. Turnover par filiale
ax3 = fig.add_subplot(gs[0, 2])
colors_turn = ["#d32f2f" if t > 15 else "#ff9800" if t > 10 else "#4caf50" for t in turnover["Turnover (%)"]]
bars3 = ax3.bar(turnover["Filiale"], turnover["Turnover (%)"], color=colors_turn)
ax3.set_title("Taux de turnover par filiale (%)", fontweight="bold")
ax3.set_xlabel("Filiale")
ax3.set_ylabel("%")
ax3.axhline(y=10, color="red", linestyle="--", alpha=0.5, label="Seuil 10%")
ax3.legend(fontsize=8)
for bar in bars3:
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             f"{bar.get_height()}%", ha="center", va="bottom", fontsize=9)

# 4. Jours d'absence par filiale
ax4 = fig.add_subplot(gs[1, 0])
bars4 = ax4.bar(absences["Filiale"], absences["Jours absence"],
                color=sns.color_palette("Oranges_d", len(absences)))
ax4.set_title("Total jours d'absence par filiale", fontweight="bold")
ax4.set_xlabel("Filiale")
ax4.set_ylabel("Jours")
for bar in bars4:
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
             str(int(bar.get_height())), ha="center", va="bottom", fontsize=9)

# 5. Types d'absence
ax5 = fig.add_subplot(gs[1, 1])
wedges, texts, autotexts = ax5.pie(
    type_absence["Nombre"],
    labels=type_absence["Type"],
    autopct="%1.1f%%",
    colors=sns.color_palette("Set2"),
    startangle=90
)
ax5.set_title("Repartition types d'absence", fontweight="bold")

# 6. Salaire moyen par niveau
ax6 = fig.add_subplot(gs[1, 2])
bars6 = ax6.barh(salaire_niveau["Niveau"], salaire_niveau["Salaire moyen (EUR)"],
                 color=sns.color_palette("Purples_d", len(salaire_niveau)))
ax6.set_title("Salaire moyen par niveau (EUR)", fontweight="bold")
ax6.set_xlabel("EUR")
for bar in bars6:
    ax6.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
             f"{int(bar.get_width())}€", ha="left", va="center", fontsize=9)

# Sauvegarde
os.makedirs("output", exist_ok=True)
plt.savefig("output/dashboard_kpis_rh.png", dpi=150, bbox_inches="tight")
print("Dashboard sauvegarde -> output/dashboard_kpis_rh.png")
plt.show()