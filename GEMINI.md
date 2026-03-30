# Multiple Independent Projects Workspace

Deze directory (`/root`) fungeert als een container voor meerdere onafhankelijke softwareprojecten. Elk project heeft zijn eigen repository, technologie-stack en deployment-methode.

## 📁 Onafhankelijke Projecten

### 1. FixJeEnergy (`/root/FixJeEnergy`)
- **Doel**: Een geavanceerd energie-managementsysteem (EMS) voor Home Assistant.
- **Stack**: Python (FastAPI), aiohttp, MQTT, Chart.js.
- **Beheer**: Draait als Home Assistant Add-on. Gebruikt `strategy.py` voor optimalisatielogica en `main.py` voor I/O.
- **Mandaten**: Houd logica in `strategy.py` vrij van side-effects. Valideer wijzigingen altijd via simulatie.

### 2. fji (`/root/fji`)
- **Doel**: FixJeICT Enterprise Ticketsysteem.
- **Stack**: Python (FastAPI), PostgreSQL (Native), Nginx, Systemd.
- **Beheer**: Geoptimaliseerd voor Debian LXC containers. Native PostgreSQL installatie vereist.

### 3. GeminiNexus (`/root/GeminiNexus`)
- **Doel**: Bridge tussen Gemini CLI en een web/Telegram interface.
- **Stack**: Python, FastAPI, JWT, Bcrypt, Telegram API.
- **Beheer**: Beveiligde webinterface op poort 8000 voor remote container beheer.

### 4. Websitemaker (`/root/Websitemaker`)
- **Doel**: AI-gestuurd platform voor het genereren van websites.
- **Stack**: Next.js 15, TypeScript, Prisma, Tailwind CSS, Stripe.
- **Beheer**: Full-stack applicatie met asynchrone site-generatie na Stripe webhook triggers.

### 5. my-autonomous-app (`/root/my-autonomous-app`)
- **Doel**: Notebook Pro - Productiviteit workspace.
- **Stack**: React 19 (Vite), Express 5, Node.js, ImapFlow.
- **Beheer**: Glassmorphic UI met diepe e-mailintegratie. Bevat Python onderhoudscripts voor UI updates.

---

## 🛠 Root-Level Scripts & Tools
De volgende scripts in `/root` zijn bedoeld voor algemeen onderhoud of batch-bewerkingen over de verschillende projecten heen:
- `apply_fixes.py`: Batch-toepassing van bugfixes.
- `apply_rbac.py`: Configureert Role-Based Access Control instellingen.
- `generate_icons.py`: Tool voor het genereren van applicatie-icoontjes.
- `refactor_main.py`: Helpt bij grote refactorings-operaties.
- `script_check.js`: JavaScript/Node.js validatie utility.

## 📐 Ontwikkelmandaten (Globaal)
1. **Project Sovereignty**: Behandel elk project als een aparte entiteit. Deel geen configuratie of database tussen projecten tenzij expliciet vermeld.
2. **Contextual Adherence**: Volg de specifieke code-stijl en documentatie van het project waar je op dat moment in werkt.
3. **Security First**: API-sleutels en secrets horen in `.env` bestanden binnen de projectmap of HA `options.json`, nooit in de code.
4. **Autonomous Operation**: Handel proactief bij het oplossen van bugs of implementeren van features, maar blijf binnen de grenzen van de project-specifieke architectuur.

*GEMINI.md is bijgewerkt om de onafhankelijkheid van de projecten te weerspiegelen.*
