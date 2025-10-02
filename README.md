# Stocks

Système de gestion de stock avancé pour entreprises avec interface web (Django) et API REST (DRF).

- Gestion Produits, Fournisseurs, Entrepôts (Locations)
- Gestion des niveaux de stock par entrepôt (InventoryItem)
- Bons d’achat (Purchase Orders) et réception de stock
- Commandes clients (Sales Orders) et décrément du stock
- Rapports de ventes (revenus, coûts, profits) avec filtres
- UI web (Bootstrap + crispy forms), authentification (inscription/connexion)
- API documentée (OpenAPI/Swagger via drf-spectacular)

## Sommaire
- [Stack](#stack)
- [Fonctionnalités](#fonctionnalités)
- [Démarrage rapide](#démarrage-rapide)
- [Interface Web](#interface-web)
- [API REST](#api-rest)
- [Rapports](#rapports)
- [Ajustement de stock](#ajustement-de-stock)
- [Commandes d’administration](#commandes-dadministration)
- [Configuration & ENV](#configuration--env)
- [Développement](#développement)

## Stack
- Python 3.13
- Django 5.1
- Django REST Framework 3.15
- django-filter, django-cors-headers
- drf-spectacular (OpenAPI + Swagger UI)
- django-crispy-forms + crispy-bootstrap5
- SQLite (par défaut)

## Fonctionnalités
- Produits: SKU, nom, prix, coût, actif, fournisseur lié
- Fournisseurs: coordonnées et site
- Entrepôts (Locations): code, nom, adresse
- Stock par entrepôt: quantité, seuil de réapprovisionnement
- Bons d’achat (Purchase Orders): statut (draft/pending/received/cancelled), réception = incrément du stock
- Commandes clients (Sales Orders): statut (draft/pending/completed/cancelled), completion = décrément du stock avec vérification de disponibilité
- Rapports de ventes: revenus, coûts et profits, filtrage par période/produit/fournisseur, groupements
- Alertes de stock bas: commande de gestion pour lister (et envoyer un email si configuré)

## Démarrage rapide
1) Créer et activer un environnement virtuel (Windows PowerShell):
```powershell
./venv/Scripts/python -m pip install -r requirements.txt
```
(Si vous n’avez pas encore de venv: `python -m venv venv` puis réexécutez la commande ci-dessus.)

2) Migrations et lancement:
```powershell
./venv/Scripts/python manage.py migrate
./venv/Scripts/python manage.py runserver
```

3) Accès:
- UI Web: http://127.0.0.1:8000/
- API Docs (Swagger): http://127.0.0.1:8000/api/docs/
- Schéma OpenAPI: http://127.0.0.1:8000/api/schema/

4) Compte utilisateur:
- Inscription: http://127.0.0.1:8000/signup/
- Connexion: http://127.0.0.1:8000/login/

## Interface Web
- Navigation principale (connecté): Produits, Fournisseurs, Entrepôts, Stocks, Bons d’achat, Commandes, API Docs
- Listes: recherche (?q=) + pagination
- Actions:
  - Bons d’achat: Réceptionner (incrémente le stock dans l’entrepôt cible)
  - Commandes: Compléter (décrémente le stock; bloque si stock insuffisant)
  - Stocks: Ajuster (delta +/− avec raison)

## API REST
Racine: `/api/`
- CRUD:
  - `/api/suppliers/`
  - `/api/products/`
  - `/api/locations/`
  - `/api/inventory/`
  - `/api/purchase-orders/` (+ `POST /{id}/receive/`)
  - `/api/sales-orders/` (+ `POST /{id}/complete/`)
- Exemple création produit (curl):
```bash
curl -X POST http://127.0.0.1:8000/api/products/ -H "Content-Type: application/json" -d '{"sku":"SKU-001","name":"Produit 1","unit_cost":"10.00","unit_price":"15.00"}'
```

## Rapports
- Endpoint: `/api/reports/sales/`
- Paramètres: `start_date`, `end_date`, `product`, `supplier`, `group_by=product|supplier|day|month`
- Exemple:
```bash
curl "http://127.0.0.1:8000/api/reports/sales/?group_by=product&start_date=2025-01-01&end_date=2025-12-31"
```

## Ajustement de stock
- UI: `/inventory/{id}/adjust/`
- API: utilisez `inventory` + vos propres règles métier si nécessaire.

## Commandes d’administration
- Lister les stocks bas (<= seuil):
```powershell
./venv/Scripts/python manage.py check_low_stock
```
- Envoi d’email (si EMAIL_* configurés et STOCK_ALERT_EMAIL défini):
```powershell
./venv/Scripts/python manage.py check_low_stock --email
```

## Configuration & ENV
- Paramètres principaux: `config/settings.py`
- CORS: activé en dev (CORS_ALLOW_ALL_ORIGINS=True)
- Email: configurez `EMAIL_*` et `STOCK_ALERT_EMAIL` pour les alertes
- Static files: `./static` (déjà présent)

## Développement
- Dépendances: `requirements.txt`
- Migrations:
```powershell
./venv/Scripts/python manage.py makemigrations
./venv/Scripts/python manage.py migrate
```
- Tests (si ajoutés plus tard):
```powershell
./venv/Scripts/python manage.py test
```
