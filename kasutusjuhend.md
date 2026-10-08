# Sõiduteenuse hinnakaebuste Power BI aruande kasutusjuhend

See juhend kirjeldab, kuidas taastada projekti andmebaas oma arvutis, ühendada sellega Power BI aruanne ning lugeda aruande nelja lehte. Projekt: [GitHub – raikokarpov-star/takso](https://github.com/raikokarpov-star/takso).

## 1. Vajalik tarkvara ja failid

Vaja on **PostgreSQL-i**, **DBeaverit** ja **Power BI Desktopi** (Windowsis). PostgreSQL peab töötama kohalikus arvutis; selles juhendis kasutatakse serverit `localhost`, porti `5432` ja andmebaasi `postgres`.

Laadi GitHubi repositoorium alla valikuga **Code → Download ZIP**, paki ZIP lahti ja leia järgmised failid:

| Fail | Otstarve |
| --- | --- |
| `data/takso_andmed_clean.csv` | Puhastatud lähteandmed |
| `sql/Script_tahtskeem.sql` | Tähtskeemi tabelite loomine ja täitmine |
| `power_bi/sõiduteenus_final.pbix` | Power BI aruanne (kontrolli täpset asukohta repositooriumis) |

Projekti teised failid (nt notebook'id ja Streamliti rakendus) ei ole selle Power BI aruande avamiseks vajalikud.

## 2. PostgreSQL-i ühenduse loomine

1. Käivita PostgreSQL. Veendu, et kohalik server kasutab porti `5432`.
2. Ava DBeaver ja loo PostgreSQL-i ühendus (**New Database Connection → PostgreSQL**).
3. Sisesta **Host:** `localhost`, **Port:** `5432`, **Database:** `postgres`, **Username:** oma PostgreSQL-i kasutajanimi (tavaliselt `postgres`) ja enda määratud parool.
4. Kontrolli ühendust (**Test Connection**) ja lõpeta seadistamine.
5. Ava ühenduses **Databases → postgres → Schemas → public**.

**Kasuta uut, tühja töökeskkonda.** Tähtskeemi SQL-skript sisaldab käske `DROP TABLE IF EXISTS ... CASCADE`, mis võivad olemasolevad samanimelised tabelid kustutada. Ära käivita seda skripti andmebaasis, kus asuvad säilitamist vajavad tabelid.

## 3. CSV importimine otse `public`-skeemi

Lähteandmed imporditakse **tabelisse `public.takso_andmed_clean`**.

1. DBeaveris tee paremklõps **Schemas → public → Tables** ja vali **Import Data**.
2. Veendu, et **Target** on `public` ja **Source format** on **CSV**; vali **Next**.
3. Vali **Browse** ja ava `data/takso_andmed_clean.csv`.
4. Kontrolli CSV seadistusi: **Encoding:** `UTF-8`, **Column delimiter:** koma (`,`), **Header position:** `top`.
5. Vali **Next** ja ava **Tables mapping**. Kontrolli, et sihttabeli nimi oleks täpselt **`takso_andmed_clean`**. Kui DBeaver pakub lisaliitega nime, määra see enne importi õigeks. Uues keskkonnas ei tohiks olla samanimelist tabelit ega vaadet.
6. Vajuta **Customise...** ja kontrolli veerutüüpe. Muuda veeru **`date`** sihttüübiks **`date`**. `is_invalid_ride` peab olema `boolean`; ülejäänud automaatselt tuvastatud tüübid jäta esialgu samaks (sh `calc_created` ja `time` tekstina).
7. Vali **OK → Next**. **Data load settings** vaates võivad jääda vaikeseaded: **Truncate target table(s) before load** märkimata, **Replace method** `<None>` ja **Use transactions** märgitud.
8. Vali **Next**. **Confirm**-aknas kontrolli, et siht oleks **`public.takso_andmed_clean [Create]`**, mitte mõni lisaliitega nimi. Seejärel vali **Proceed**.

**Kontroll:** värskenda DBeaveri tabeliloendit ja käivita SQL-redaktoris:

```sql
SELECT COUNT(*) AS ridu,
       COUNT(DISTINCT order_id_new) AS soite,
       COUNT(DISTINCT ticket_id_new) AS poordumisi
FROM public.takso_andmed_clean;
```

Projekti lähteandmete puhul on oodatavad tulemused **4943 rida**, **4166 eri sõitu** ja **4943 eri `ticket_id_new` väärtust**. Viimane näitaja kirjeldab lähteandmete ticket-ridu, mitte 4943 hinnakaebust.

Kui import ebaõnnestub, kontrolli esmajoones veergude tüüpe ja kuupäeva vormingut. **Ära jätka tähtskeemi loomisega, kuni import ja kontrollpäring pole õnnestunud.**

## 4. Tähtskeemi loomine

1. Ava DBeaveri SQL-redaktoris fail `sql/Script_tahtskeem.sql`.
2. Kontrolli, et redaktor oleks ühendatud õige andmebaasiga (`postgres`) ning aktiivne skeem oleks `public`. Vajaduse korral määra skeem enne skripti käivitamist: 

   ```sql
   SET search_path TO public;
   ```

3. Käivita **terve SQL-skript** DBeaveri käsuga **Execute SQL Script (Alt + X)**. Ära käivita ainult üksikuid ridu.
4. Veendu, et veateateid ei tekkinud, ja värskenda tabelite loendit.

Skript peab looma **viis dimensioonitabelit** (`dim_date`, `dim_order`, `dim_device`, `dim_app_version`, `dim_pricing_context`) ning **kaks faktitabelit** (`fact_rides`, `fact_tickets`). Nende tabelite vahele luuakse kuus välisvõtmeseost.

Kontrollpäring:

```sql
SELECT (SELECT COUNT(*) FROM public.fact_rides) AS fact_rides_rows,
       (SELECT COUNT(*) FROM public.fact_tickets) AS fact_tickets_rows,
       (SELECT COUNT(*) FROM public.dim_order) AS dim_order_rows;
```

Oodatavad tulemused: **4166**, **4943**, **4166**. Skripti lõpus on ka seoste ja puuduvate võtmete kontrollid.

**Ära lisa `dim_order` tabelisse käsitsi täiendavaid veerge.** Power BI saab vajalikud tellimuse staatuse ja loomise aja väljad `Rides`-päringuga tehtud Power Query ühendusest.

## 5. Power BI aruande avamine ja andmete värskendamine

1. Ava fail **`sõiduteenus_final.pbix`** Power BI Desktopis. Faili leiad projekti `power_bi`-kaustast, kui see on repositooriumisse nii salvestatud.
2. Ava **Home → Transform data → Data source settings**.
3. Valige **Data sources in current file**. Projektis on andmeallikas **`localhost:5432;postgres`**. Kui kasutad teist hosti, porti või andmebaasinime, vali **Change Source...** ja muuda vastavad ühenduse väljad.
4. Vali andmeallikas ja **Edit Permissions... → Credentials → Edit...**. Autentimisviis on **Database**: sisesta **oma** PostgreSQL-i kasutajanimi ja parool ning vali **Save**. Projekti algses seadistuses on **Encrypt connections** välja lülitatud ja **Privacy Level** `None`; ära lülita krüpteerimist välja turvanõuete vastaselt. Vajaduse korral seadista turvaline kohalik ühendus.
5. Sulge seadistusaknad. Vali Power BI-s **Home → Refresh** ning oota, kuni andmete laadimine lõpeb.
6. Kui värskendamine õnnestus ja visualiseeringud kuvatakse, salvesta fail soovi korral oma arvutisse.

Power BI mudel kasutab **Import-režiimi**. Seetõttu võib salvestatud `.pbix` kuvada aruannet ka ilma kohaliku PostgreSQL-i ühenduseta, kuid **andmete värskendamiseks ja lahenduse taastamiseks** on vaja selles juhendis kirjeldatud andmebaasi. Ärge pidage `Refresh`-nupu ebaõnnestumist automaatselt märgiks, et failis salvestatud aruannet ei saa vaadata.

### Kui värskendamine ebaõnnestub

- **Ühendust ei leita:** kontrolli, et PostgreSQL töötaks ja server/port/andmebaasinimi vastaks Power BI seadele.
- **Autentimise viga:** kontrolli **Edit Permissions → Credentials** all kasutajanime ja parooli.
- **Tabelit või veergu ei leita:** kontrolli, et CSV oleks imporditud **`public.takso_andmed_clean`** nime alla ja tähtskeemi skript õnnestuks tervikuna.

## 6. Aruandes liikumine ja graafikute lugemine

Aruandel on **neli lehte**, mida saab vahetada Power BI akna **allservas asuvate lehesakkide** kaudu. Mõned lehed on pikad: kõigi graafikute nägemiseks tuleb **kerida vertikaalselt**. Vajaduse korral kasuta all paremal **suurenduse** liugurit.

Üldjuhised interaktiivsete visualiseeringute kasutamiseks:

- Liiguta kursor tulba, punkti või joone peale, et näha täpsemaid väärtusi (**tooltip**).
- Klõpsa diagrammi kategoorial, et esile tõsta või filtreerida seotud andmeid. Valiku eemaldamiseks klõpsa sama kategooriat uuesti või tühjenda filter.
- Kui aruandelehel on eraldi filtrid, kontrolli enne järelduste tegemist, milline piirkond, GPS-i kvaliteet või hinnastamisviis on valitud.
- Erista **sõitude arvu**, **hinnakaebusega sõitude arvu** ja **hinnakaebuste osakaalu**. Need ei ole samad mõõdikud.
- Kombineeritud tulp- ja joondiagrammil kontrolli mõlemat vertikaaltelge: üks võib näidata sõitude arvu, teine protsenti.

### Leht 1. „EU/Non-EU võrdlus (Felena)”

Võrdleb Euroopa Liidus ja väljaspool ELi toimunud sõite: nende osakaalu, hinnakaebusega sõitude hulka, hinnastamisviise ja GPS-i kvaliteeti. Lehe alguses on põhinäitajad (4943 ticket-rida, 4166 sõitu, 309 hinnakaebusega sõitu ja 7,4% hinnakaebusega sõite).

**Lugemise põhimõte:** ELi-välised sõidud moodustavad umbes 40% andmestiku sõitudest, kuid umbes 96% hinnakaebusega sõitudest. Hinnakaebusega sõitude osakaal on selles segmendis **17,6%**, ELis **0,52%**. Hinnastamise tüübi ja GPS-i graafikud aitavad erinevust täpsemalt uurida, kuid ei tõesta selle põhjust.

### Leht 2. „Sõiduprognoos vs tegelikkus (Raiko)”

Võrdleb sõidu tegelikku distantsi ja kestust prognoositud väärtustega ning näitab hinnakaebuste osakaalu erinevates sõidupikkuse ja -kestuse vahemikes.

Lehe ülaosas saab valida **EU / Non-EU**, **GPS: Inaccurate / Accurate** ja **Prediction price type: prediction / upfront**. Diagrammid reageerivad valikutele. Kahel hajuvusdiagrammil eristavad punased ja sinised punktid hinnakaebusega ning hinnakaebuseta sõite.

### Leht 3. „Hinnastus (Liis)”

Võrdleb **hinnastamise tüüpe** (`upfront`, `prediction` jt), **tegeliku ja eeldatava hinna erinevust**, **hinnamuutuse põhjuseid** ja **sihtkoha muutmiste arvu**. Leht on pikk ja jaotatud neljaks analüüsiosaks; lõpus on kokkuvõte.

Esimese analüüsiosa juures on **EU Indicator** filter. Kui graafikul on korraga tulbad ja joon, loe tulpasid sõitude arvu ning joont hinnakaebuste osakaalu teljelt. Erinevate segmentide näitajate võrdlemisel arvesta nende sõitude arvuga.

### Leht 4. „Tehnilised tegurid (Hannes)”

Analüüsib **GPS-i kvaliteeti**, **juhi rakenduse versiooni**, **telefonimudeleid** ning nende tegurite koosmõju. Leht on jagatud osadeks **A–G**: üldine kaebuste määr, GPS, äpiversioonid, telefonid, koosmõju, kohandatud mõju ning probleemsete segmentide prioriseerimine.

Tulpdiagrammid võrdlevad tehnilisi gruppe, hajuvusdiagramm seostab näiteks telefonimudelite GPS-i ebatäpsust ja hinnakaebuste osakaalu. Lõpuosas vaadeldakse ka **95% usaldusvahemikke** ja segmendi suurust. Väikese sõitude arvuga grupi kõrget protsenti ei tohiks automaatselt pidada suurimaks äriliseks probleemiks.

## 7. Andmete tõlgendamise piirang

Projektis analüüsitakse **klienditoe pöördumistega seotud sõite**, mitte kõiki teenusepakkuja sõite. Seetõttu näitab „hinnakaebuste osakaal” **hinnakaebusega sõitude osakaalu selles andmestikus**, mitte hinnakaebuse tõenäosust kogu ettevõtte sõitude hulgas. Samuti näitavad võrreldud tunnused seoseid, kuid ei tõesta iseenesest põhjuslikku mõju.

---

**Dokumentatsiooni seis:** 8. oktoober 2026. 
