"""
Outils disponibles pour l'agent immobilier.
"""

import os
import pandas as pd
from pathlib import Path
from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DB_NAME = str(Path(__file__).parent.parent / "vector_db")
CSV_PATH = Path(__file__).parent.parent / "annonces_immo.csv"

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory=DB_NAME, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# Chargement du CSV en mémoire pour la recherche filtrée
_df = pd.read_csv(CSV_PATH, encoding="utf-8")

# Nettoyage des colonnes numériques
_df["_prix"] = pd.to_numeric(_df["Prix"].str.replace(r"[^\d]", "", regex=True), errors="coerce")
_df["_surface"] = pd.to_numeric(_df["Surface_totale"].str.replace(r"[^\d.,]", "", regex=True).str.replace(",", "."), errors="coerce")
_df["_nb_pieces"] = pd.to_numeric(_df["Nb_pieces"], errors="coerce")


@tool
def recherche_rag(question: str) -> str:
    """Recherche dans la base de connaissances (guides immobiliers, infos agence, descriptions de biens).
    Utiliser pour les questions sur la réglementation, la fiscalité, les étapes d'un achat,
    les diagnostics, la copropriété, les infos sur l'agence, ou toute question générale sur l'immobilier
    qui nécessite des informations détaillées provenant de la base documentaire."""
    docs = retriever.invoke(question)
    if not docs:
        return "Aucun résultat trouvé dans la base de connaissances."
    results = []
    for doc in docs:
        source = doc.metadata.get("source", "Inconnu")
        results.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(results)


@tool
def recherche_filtree(
    ville: str = None,
    prix_max: float = None,
    prix_min: float = None,
    surface_min: float = None,
    surface_max: float = None,
    nb_pieces: int = None,
    nb_chambres: int = None,
    classe_dpe: str = None,
    parking: bool = None,
    cave: bool = None,
    ascenseur: bool = None,
    meuble: bool = None,
    limit: int = 10,
) -> str:
    """Recherche des biens immobiliers par critères exacts dans la base d'annonces.
    Utiliser quand l'utilisateur cherche des biens avec des critères précis :
    ville, budget, surface, nombre de pièces, DPE, équipements (parking, cave, ascenseur).
    Renvoie une liste de biens correspondant aux critères."""
    df = _df.copy()

    if ville:
        df = df[df["Ville"].str.contains(ville, case=False, na=False)]
    if prix_max is not None:
        df = df[df["_prix"] <= prix_max]
    if prix_min is not None:
        df = df[df["_prix"] >= prix_min]
    if surface_min is not None:
        df = df[df["_surface"] >= surface_min]
    if surface_max is not None:
        df = df[df["_surface"] <= surface_max]
    if nb_pieces is not None:
        df = df[df["_nb_pieces"] == nb_pieces]
    if nb_chambres is not None:
        df = df[pd.to_numeric(df["Nb_chambres"], errors="coerce") == nb_chambres]
    if classe_dpe is not None:
        classes = [c.strip().upper() for c in classe_dpe.split(",")]
        df = df[df["Classe_energie"].str.upper().isin(classes)]
    if parking is True:
        df = df[df["Parking"].astype(str).str.lower() == "true"]
    if cave is True:
        df = df[df["Cave"].astype(str).str.lower() == "true"]
    if ascenseur is True:
        df = df[df["Ascenseur"].astype(str).str.lower() == "true"]
    if meuble is True:
        df = df[df["Meuble"].astype(str).str.lower() == "true"]

    total = len(df)
    df = df.head(limit)

    if df.empty:
        return "Aucun bien ne correspond à ces critères."

    results = [f"{total} bien(s) trouvé(s) (affichage des {min(limit, total)} premiers) :\n"]
    for _, row in df.iterrows():
        bien = f"- **{row.get('Type', 'Bien')}** à **{row.get('Ville', '?')}**\n"
        bien += f"  Prix : {row.get('Prix', '?')} | Surface : {row.get('Surface_totale', '?')} | Pièces : {row.get('Nb_pieces', '?')}\n"
        bien += f"  Chambres : {row.get('Nb_chambres', '?')} | DPE : {row.get('Classe_energie', '?')}\n"

        equips = []
        if str(row.get("Parking", "")).lower() == "true":
            equips.append("Parking")
        if str(row.get("Cave", "")).lower() == "true":
            equips.append("Cave")
        if str(row.get("Ascenseur", "")).lower() == "true":
            equips.append("Ascenseur")
        if equips:
            bien += f"  Équipements : {', '.join(equips)}\n"

        bien += f"  Réf : {row.get('Ref_superimmo', '?')}"
        results.append(bien)

    return "\n\n".join(results)


@tool
def calcul_frais_notaire(prix: float, neuf: bool = False) -> str:
    """Calcule les frais de notaire pour un achat immobilier.
    Utiliser quand l'utilisateur demande une estimation des frais de notaire pour un prix donné.
    Paramètres : prix du bien et si le bien est neuf (moins de 5 ans) ou ancien."""

    if neuf:
        # Neuf : taxe de publicité foncière réduite
        droits_mutation = prix * 0.00715
        taxe_description = "Taxe de publicité foncière (neuf)"
    else:
        # Ancien : droits de mutation complets
        droits_mutation = prix * 0.0580
        taxe_description = "Droits de mutation (ancien : 5,80%)"

    # Émoluments du notaire (barème réglementé)
    tranches = [
        (6500, 0.03870),
        (17000, 0.01596),
        (60000, 0.01064),
        (float("inf"), 0.00799),
    ]
    emoluments = 0
    reste = prix
    seuil_precedent = 0
    for seuil, taux in tranches:
        tranche_montant = min(reste, seuil - seuil_precedent)
        if tranche_montant <= 0:
            break
        emoluments += tranche_montant * taux
        reste -= tranche_montant
        seuil_precedent = seuil
    emoluments_ttc = emoluments * 1.20  # TVA 20%

    # Contribution de sécurité immobilière
    contribution_si = max(prix * 0.001, 15)

    # Débours
    debours = 1200

    total = droits_mutation + emoluments_ttc + contribution_si + debours
    pourcentage = (total / prix) * 100

    return f"""Estimation des frais de notaire pour un bien à {prix:,.0f} € ({'neuf' if neuf else 'ancien'}) :

- {taxe_description} : {droits_mutation:,.0f} €
- Émoluments du notaire (TTC) : {emoluments_ttc:,.0f} €
- Contribution de sécurité immobilière : {contribution_si:,.0f} €
- Débours estimés : {debours:,.0f} €

**Total estimé : {total:,.0f} € ({pourcentage:.1f}% du prix)**

Coût total de l'acquisition : {prix + total:,.0f} €"""


@tool
def simulation_pret(
    montant: float,
    taux_annuel: float = 3.5,
    duree_annees: int = 25,
    apport: float = 0,
    revenus_mensuels: float = None,
) -> str:
    """Simule un prêt immobilier et calcule les mensualités, le coût total et le taux d'endettement.
    Utiliser quand l'utilisateur demande une simulation de prêt, de mensualités,
    ou veut savoir combien il va payer par mois.
    Paramètres : montant du bien, taux annuel (défaut 3.5%), durée en années (défaut 25),
    apport personnel, revenus mensuels nets (pour le taux d'endettement)."""

    capital = montant - apport
    if capital <= 0:
        return "L'apport couvre le prix du bien, pas besoin de prêt."

    taux_mensuel = taux_annuel / 100 / 12
    nb_mensualites = duree_annees * 12

    if taux_mensuel > 0:
        mensualite = capital * taux_mensuel / (1 - (1 + taux_mensuel) ** (-nb_mensualites))
    else:
        mensualite = capital / nb_mensualites

    cout_total = mensualite * nb_mensualites
    cout_interets = cout_total - capital

    result = f"""Simulation de prêt immobilier :

**Paramètres :**
- Prix du bien : {montant:,.0f} €
- Apport personnel : {apport:,.0f} €
- Montant emprunté : {capital:,.0f} €
- Taux annuel : {taux_annuel}%
- Durée : {duree_annees} ans ({nb_mensualites} mensualités)

**Résultats :**
- Mensualité : {mensualite:,.0f} € /mois
- Coût total du crédit : {cout_total:,.0f} €
- Dont intérêts : {cout_interets:,.0f} €"""

    if revenus_mensuels and revenus_mensuels > 0:
        taux_endettement = (mensualite / revenus_mensuels) * 100
        result += f"""

**Taux d'endettement : {taux_endettement:.1f}%**"""
        if taux_endettement > 35:
            result += f"\n⚠ Attention : le taux d'endettement dépasse le seuil recommandé de 35%."
        else:
            result += f"\n Le taux d'endettement est sous le seuil de 35%."

    return result


# Liste de tous les outils pour l'agent
all_tools = [recherche_rag, recherche_filtree, calcul_frais_notaire, simulation_pret]
