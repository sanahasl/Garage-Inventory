# 🔧 Garage Inventory Manager

A web-based inventory system for a Land Rover Defender repair garage. It tracks
spare parts, paints and consumables so shortages are spotted *before* a job
starts, instead of after it's finished.

## The problem

Stock was tracked mentally and through WhatsApp photos, so the garage only
realised it needed to reorder once a job was already done.

## Current features

- Catalogue of parts, paints and consumables (part numbers, locations, minimum levels)
- Every stock change is logged as a movement (received, used, adjustment, waste)
- Stock levels are calculated from movement history, so they can't drift out of sync
- Low-stock detection, viewable in the Django admin

## Tech stack

Python 3.14, Django, SQLite (development)

## Getting started

```bash
git clone https://github.com/YOUR-USERNAME/garage-inventory.git
cd garage-inventory
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000/admin

## Roadmap

- [ ] Dashboard with stock summary and reorder list
- [ ] Phone-friendly "Stock Out" page for mechanics
- [ ] Jobs, vehicles and suppliers as their own tables
- [ ] Deployment

Work in progress, built as a Python and Django learning project.