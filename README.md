# 🗡️ Raid Helper Calendar

Agregátor raid eventů z více Discord serverů s použitím Raid Helper API. Zobrazuje eventy seskupené podle dnů v českém formátu.

## Features

- ✅ Agregace eventů z více Discord serverů
- ✅ České datum a čas formátování
- ✅ Seskupení eventů podle dnů
- ✅ Aktuální týden prominentně zobrazen
- ✅ Příští týden sbalitelný
- ✅ Streamlit web interface
- ✅ Jednoduché spravování server ID
- ✅ Zabezpečený vstup pro access token

## Instalace

1. Klonujte repository:
```bash
git clone <your-repo-url>
cd raid-helper-calendar
```

2. Nainstalujte závislosti:
```bash
pip install -e .
```

3. Spusťte aplikaci:
```bash
streamlit run main.py
```

Nebo použijte startup script:
```bash
chmod +x run.sh
./run.sh
```

## Použití

### 1. Získání Access Token

1. Přihlaste se na [raid-helper.dev](https://raid-helper.dev)
2. Otevřete Developer Tools (F12)
3. Přejděte na Network tab
4. Načtěte stránku s eventy
5. Najděte request na `/api/events/`
6. Zkopírujte `accessToken` z request payload

### 2. Nastavení Server IDs

1. V postranním panelu aplikace můžete přidávat/odebírat Discord Server IDs
2. Default server IDs můžete upravit v `main.py` v proměnné `DEFAULT_SERVER_IDS`

### 3. Načtení eventů

1. Zadejte váš Access Token
2. Zkontrolujte/upravte Server IDs
3. Klikněte na "🔄 Načíst eventy"

## Struktura projektu

```
├── main.py              # Hlavní Streamlit aplikace
├── raid_helper_api.py   # API klient pro Raid Helper
├── event_processor.py   # Zpracování a seskupování eventů
├── pyproject.toml       # Python project konfigurace
├── run.sh              # Startup script
└── README.md           # Tato dokumentace
```

## API

Aplikace používá oficální Raid Helper API:
- Endpoint: `https://raid-helper.dev/api/events/`
- Payload: `{"serverid": "...", "accessToken": "..."}`

## Licence

MIT License