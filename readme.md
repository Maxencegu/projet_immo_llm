# ImmoBot - Agent Immobilier IA

Agent conversationnel expert en immobilier, propulse par Claude (Anthropic) et LangGraph. Il recherche des biens en Ile-de-France, calcule les frais de notaire, simule des prets et repond aux questions reglementaires.

## Architecture

```
Utilisateur (Streamlit)
        |
        v
  Agent LangGraph
        |
        |--- recherche_rag         ->  ChromaDB (guides, reglementation, agence)
        |--- recherche_filtree     ->  Pandas (filtres exacts sur 2 820 annonces)
        |--- calcul_frais_notaire  ->  Calcul Python (bareme officiel)
        |--- simulation_pret       ->  Calcul Python (amortissement)
        |
        v
  Claude Sonnet 4.5 (Anthropic)
```

L'agent decide a chaque question quel(s) outil(s) utiliser. S'il n'en a pas besoin, il repond avec ses connaissances generales.

## Outils de l'agent

| Outil | Role | Source de donnees |
|-------|------|-------------------|
| `recherche_rag` | Questions reglementation, fiscalite, guides, infos agence | ChromaDB (7 633 vecteurs) |
| `recherche_filtree` | Recherche de biens par criteres (ville, prix, surface, DPE, parking...) | CSV charge en memoire via Pandas |
| `calcul_frais_notaire` | Calcul exact des frais par tranche (ancien/neuf) | Bareme reglemente |
| `simulation_pret` | Mensualites, cout total, taux d'endettement | Formule d'amortissement |

## Structure du projet

```
chat-rag-project/
├── app.py                          # Interface Streamlit
├── annonces_immo.csv               # Dataset source (2 820 annonces)
├── requirements.txt                # Dependances Python
├── .env                            # Cle API Anthropic (non versionne)
├── .streamlit/
│   └── config.toml                 # Theme Streamlit (dark navy)
├── src/
│   ├── agent.py                    # Agent LangGraph + prompt systeme
│   ├── tools.py                    # 4 outils (RAG, filtre, notaire, pret)
│   ├── ingest.py                   # Pipeline d'ingestion (Markdown -> ChromaDB)
│   ├── csv_to_markdown.py          # Conversion CSV -> fiches Markdown
│   └── answer.py                   # Ancien pipeline RAG (non utilise par l'agent)
├── knowledge-base/
│   ├── agence/                     # Presentation de l'agence (1 fichier)
│   ├── biens/                      # Fiches immobilieres (2 741 fichiers .md)
│   └── guides/                     # Guides pratiques (6 fichiers)
│       ├── etapes_achat_immobilier.md
│       ├── frais_notaire.md
│       ├── fiscalite_immobiliere.md
│       ├── diagnostics_obligatoires.md
│       ├── guide_location.md
│       └── copropriete.md
└── vector_db/                      # ChromaDB (genere par ingest.py)
```

## Installation

### Prerequis

- Python 3.11+
- Cle API Anthropic

### Mise en place

```bash
# Cloner le projet
git clone <url-du-repo>
cd chat-rag-project

# Creer et activer le venv
python -m venv venv
source venv/Scripts/activate        # Windows/Git Bash
# source venv/bin/activate          # Linux/macOS

# Installer les dependances
pip install -r requirements.txt

# Configurer la cle API
echo "ANTHROPIC_API_KEY=votre_cle_ici" > .env
```

### Preparer la base de connaissances

Ces deux etapes sont necessaires uniquement lors de la premiere installation ou apres modification des donnees.

```bash
# 1. Convertir le CSV en fiches Markdown
python src/csv_to_markdown.py

# 2. Indexer les documents dans ChromaDB
python src/ingest.py
```

## Lancement

```bash
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`.

## Exemples de questions

**Recherche de biens**
- Quels T3 sont disponibles a Boulogne-Billancourt pour moins de 400 000 euros ?
- Je cherche un appartement avec parking et cave a Rueil-Malmaison
- Montrez-moi des biens avec un DPE A ou B a Paris

**Calculs**
- Quels sont les frais de notaire pour un bien a 350 000 euros dans l'ancien ?
- Simulez un pret de 300 000 euros sur 25 ans a 3,5% avec 50 000 euros d'apport
- Je gagne 4 500 euros net par mois, puis-je emprunter 300 000 euros sur 20 ans ?

**Reglementation et guides**
- Quelles sont les etapes pour acheter un appartement ?
- Mon bien est classe F en DPE, est-ce que je peux encore le louer ?
- Comment fonctionne le statut LMNP ?

**Multi-outils**
- Je veux un T3 a Colombes pour moins de 350 000 euros, combien je paierai par mois ?

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| LLM | Claude Sonnet 4.5 (Anthropic) |
| Agent | LangGraph (react agent) |
| Embeddings | all-MiniLM-L6-v2 (HuggingFace) |
| Vector store | ChromaDB |
| Orchestration | LangChain |
| Donnees structurees | Pandas |
| Interface | Streamlit |
| Langage | Python 3.13 |

## Configuration

**Chunking** (`src/ingest.py`) :
- Taille des chunks : 1 000 caracteres
- Chevauchement : 300 caracteres

**Agent** (`src/agent.py`) :
- Modele : `claude-sonnet-4-5-20250929`
- Temperature : 0

**Recherche RAG** (`src/tools.py`) :
- Top K : 10 documents

## Ajout de nouvelles donnees

1. Ajouter des fichiers `.md` dans `knowledge-base/` (ou des lignes dans le CSV puis relancer `csv_to_markdown.py`)
2. Relancer l'ingestion : `python src/ingest.py`
3. Redemarrer l'application
