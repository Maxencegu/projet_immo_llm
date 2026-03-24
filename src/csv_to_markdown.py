"""
Script de conversion du fichier annonces_immo.csv en fiches Markdown individuelles.
Chaque annonce devient un fichier .md dans knowledge-base/biens/
"""

import csv
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CSV_PATH = PROJECT_ROOT / "annonces_immo.csv"
OUTPUT_DIR = PROJECT_ROOT / "knowledge-base" / "biens"

# Mapping des champs CSV vers des labels lisibles
EQUIPEMENTS_FIELDS = {
    "Double_vitrage": "Double vitrage",
    "Cave": "Cave",
    "Parking": "Parking",
    "Ascenseur": "Ascenseur",
    "Gardien": "Gardien",
    "Meuble": "Meublé",
}


def clean_value(value):
    """Retourne None si la valeur est vide ou non renseignée."""
    if value is None or str(value).strip() in ("", "nan", "None"):
        return None
    return str(value).strip()


def build_markdown(row):
    """Génère le contenu Markdown pour une annonce."""
    ref = clean_value(row.get("Ref_superimmo")) or "SANS_REF"
    type_bien = clean_value(row.get("Type")) or "Bien"
    ville = clean_value(row.get("Ville")) or "Ville inconnue"
    prix = clean_value(row.get("Prix")) or "Prix non communiqué"
    surface = clean_value(row.get("Surface_totale")) or "Non renseignée"

    lines = []
    lines.append(f"# {type_bien} à {ville}")
    lines.append("")
    lines.append(f"**Référence :** {ref}")
    lines.append("")

    # --- Informations principales ---
    lines.append("## Informations principales")
    lines.append("")
    lines.append(f"- **Type :** {type_bien}")
    lines.append(f"- **Prix :** {prix}")

    prix_m2 = clean_value(row.get("Prix_par_m2"))
    if prix_m2:
        lines.append(f"- **Prix au m² :** {prix_m2} €/m²")

    lines.append(f"- **Surface totale :** {surface}")

    surface_sejour = clean_value(row.get("Surface_sejour_m2"))
    if surface_sejour:
        lines.append(f"- **Surface séjour :** {surface_sejour} m²")

    lines.append(f"- **Ville :** {ville}")

    for field, label in [
        ("Nb_pieces", "Nombre de pièces"),
        ("Nb_chambres", "Nombre de chambres"),
        ("Nb_salles_bain", "Salles de bain"),
        ("Nb_wc", "WC"),
    ]:
        val = clean_value(row.get(field))
        if val:
            lines.append(f"- **{label} :** {val}")

    orientation = clean_value(row.get("Orientation"))
    if orientation:
        lines.append(f"- **Orientation :** {orientation}")

    etage = clean_value(row.get("Num_etage_logement"))
    etage_total = clean_value(row.get("Etage_total"))
    if etage and etage_total:
        lines.append(f"- **Étage :** {etage}/{etage_total}")
    elif etage:
        lines.append(f"- **Étage :** {etage}")

    annee = clean_value(row.get("Annee_construction"))
    if annee:
        lines.append(f"- **Année de construction :** {annee}")

    chauffage = clean_value(row.get("Type_chauffage"))
    if chauffage:
        lines.append(f"- **Chauffage :** {chauffage}")

    lines.append("")

    # --- Équipements ---
    equips = []
    for field, label in EQUIPEMENTS_FIELDS.items():
        val = clean_value(row.get(field))
        if val and val.lower() == "true":
            equips.append(label)

    if equips:
        lines.append("## Équipements")
        lines.append("")
        for eq in equips:
            lines.append(f"- {eq}")
        lines.append("")

    # --- Charges et fiscalité ---
    charges = clean_value(row.get("Charges_annuelles"))
    taxe = clean_value(row.get("Taxe_fonciere"))
    copro = clean_value(row.get("Copro_nb_lots"))

    if charges or taxe or copro:
        lines.append("## Charges et copropriété")
        lines.append("")
        if charges:
            lines.append(f"- **Charges annuelles :** {charges} €")
        if taxe:
            lines.append(f"- **Taxe foncière :** {taxe} €")
        if copro:
            lines.append(f"- **Nombre de lots en copropriété :** {copro}")
        lines.append("")

    # --- DPE ---
    classe_energie = clean_value(row.get("Classe_energie"))
    conso = clean_value(row.get("Conso_energie_kWh_m2_an"))
    classe_co2 = clean_value(row.get("Classe_emission_CO2"))
    emission_co2 = clean_value(row.get("Emission_CO2_kgeq_m2_an"))
    dep_min = clean_value(row.get("Depense_min"))
    dep_max = clean_value(row.get("Depense_max"))

    if classe_energie or conso or classe_co2:
        lines.append("## Diagnostic de performance énergétique (DPE)")
        lines.append("")
        if classe_energie:
            lines.append(f"- **Classe énergie :** {classe_energie}")
        if conso:
            lines.append(f"- **Consommation :** {conso} kWh/m²/an")
        if classe_co2:
            lines.append(f"- **Classe émission CO2 :** {classe_co2}")
        if emission_co2:
            lines.append(f"- **Émission CO2 :** {emission_co2} kg éq. CO2/m²/an")
        if dep_min and dep_max:
            lines.append(f"- **Dépenses énergétiques estimées :** {dep_min} € à {dep_max} € /an")
        lines.append("")

    # --- Agence ---
    agence = clean_value(row.get("Agence"))
    if agence:
        lines.append("## Agence")
        lines.append("")
        lines.append(f"- **Agence :** {agence}")

        ref_agence = clean_value(row.get("Ref_agence"))
        if ref_agence:
            lines.append(f"- **Référence agence :** {ref_agence}")
        lines.append("")

    # --- Description ---
    description = clean_value(row.get("Description"))
    if description:
        lines.append("## Description")
        lines.append("")
        lines.append(description)
        lines.append("")

    return "\n".join(lines)


def sanitize_filename(name):
    """Crée un nom de fichier valide à partir d'une chaîne."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r"\s+", "_", name)
    return name[:100]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for i, row in enumerate(reader):
            ref = clean_value(row.get("Ref_superimmo")) or f"annonce_{i+1}"
            type_bien = clean_value(row.get("Type")) or "bien"
            ville = clean_value(row.get("Ville")) or "inconnu"

            filename = sanitize_filename(f"{ref}_{type_bien}_{ville}")
            filepath = OUTPUT_DIR / f"{filename}.md"

            content = build_markdown(row)
            with open(filepath, "w", encoding="utf-8") as out:
                out.write(content)
            count += 1

    print(f"Conversion terminée : {count} fiches générées dans {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
