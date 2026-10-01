"""
Uurimisküsimus 3: hinnastamise ja tehnilised tegurid vs overcharge-ticket.
Analüüsi ühik: order (4166). Sihtmuutuja: had_ticket (0/1).
Väljund: CSV-failid Power BI jaoks (kaust pbi/).
"""
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportion_confint

SRC = "takso_andmed_clean.csv"
OUT = "pbi"
os.makedirs(OUT, exist_ok=True)

# ---------- 1. Order-tasand ----------
d = pd.read_csv(SRC)
o = (d.groupby("order_id_new")
       .agg(had_ticket=("overpaid_ride_ticket", "max"),
            price_type=("prediction_price_type", "first"),
            gps=("gps_confidence", "first"),
            dest_changes=("dest_change_number", "first"),
            change_reason=("change_reason_pricing", "first"),
            entered_by=("entered_by", "first"),
            eu=("eu_indicator", "first"),
            month=("month", "first"),
            upfront=("upfront_price", "first"),
            metered=("metered_price", "first"),
            dist=("distance", "first"),
            pred_dist=("predicted_distance", "first"))
       .reset_index())
o["had_ticket"] = o.had_ticket.fillna(0).astype(int)
o["price_type"] = o.price_type.fillna("puudub")
o["change_reason"] = o.change_reason.fillna("muutus puudub")
o["dest_changes_grp"] = o.dest_changes.clip(upper=3).map({1: "1", 2: "2", 3: "3+"})
o["region"] = o.eu.map({1: "EL", 0: "mitte-EL"})
o["gps_grp"] = o.gps.map({1: "GPS hea (1)", 0: "GPS halb (0)"})

BASE = o.had_ticket.mean()
TOTAL_T = o.had_ticket.sum()

def rates(df, cols, scope):
    g = df.groupby(cols).had_ticket.agg(n="count", tickets="sum").reset_index()
    lo, hi = proportion_confint(g.tickets, g.n, method="wilson")
    g["rate"], g["ci_low"], g["ci_high"] = g.tickets / g.n, lo, hi
    g["lift"] = g.rate / BASE
    g["share_of_all_tickets"] = g.tickets / TOTAL_T
    g["small_n"] = g.n < 50
    g["scope"] = scope
    return g

# ---------- 2. Tegurid eraldi (pikk formaat) ----------
factors = {"price_type": "Hinnatüüp", "gps_grp": "GPS confidence",
           "entered_by": "Sisestaja", "change_reason": "Muutuse põhjus",
           "dest_changes_grp": "Sihtkoha muutusi", "region": "Piirkond"}
rows = []
for scope, sub in [("kõik", o), ("mitte-EL", o[o.eu == 0]), ("EL", o[o.eu == 1])]:
    for col, label in factors.items():
        r = rates(sub, [col], scope).rename(columns={col: "value"})
        r.insert(0, "factor", label)
        rows.append(r)
pd.concat(rows).to_csv(f"{OUT}/f1_tegurid_eraldi.csv", index=False)

# ---------- 3. Koosmõjud ----------
pd.concat([rates(o, ["price_type", "gps_grp"], "kõik"),
           rates(o[o.eu == 0], ["price_type", "gps_grp"], "mitte-EL")]
          ).to_csv(f"{OUT}/f2_hinnatyyp_x_gps.csv", index=False)
rates(o, ["dest_changes_grp", "change_reason"], "kõik"
      ).to_csv(f"{OUT}/f3_sihtkoht_x_pohjus.csv", index=False)

# ---------- 4. Logistiline regressioon (kontrollitud efektid) ----------
o["prediction"] = (o.price_type == "prediction").astype(int)
o["gps_low"] = (o.gps == 0).astype(int)
o["client_entered"] = (o.entered_by == "client").astype(int)
o["client_dest_change"] = (o.change_reason == "client_destination_changed").astype(int)
o["dest_changed"] = (o.dest_changes >= 2).astype(int)
o["non_eu"] = (o.eu == 0).astype(int)

labels = {"prediction": "Hinnatüüp = prediction",
          "gps_low": "GPS confidence = 0",
          "client_entered": "Sisestaja = client",
          "client_dest_change": "Kliendi sihtkoha muutus",
          "dest_changed": "Sihtkohta muudeti (≥2)",
          "non_eu": "Piirkond = mitte-EL (kontroll)"}
controllable = {"non_eu": "kontekst"}

def logit(df, terms, model_name):
    # eemalda tunnused, millel alamhulgas varieeruvus puudub
    terms = [t for t in terms if df[t].nunique() > 1]
    m = smf.logit("had_ticket ~ " + " + ".join(terms), data=df).fit(disp=0)
    ci = m.conf_int()
    return pd.DataFrame({
        "model": model_name,
        "term": [labels[t] for t in terms],
        "odds_ratio": np.exp(m.params[terms]).values,
        "ci_low": np.exp(ci.loc[terms, 0]).values,
        "ci_high": np.exp(ci.loc[terms, 1]).values,
        "p_value": m.pvalues[terms].values,
        "type": [controllable.get(t, "mõjutatav") for t in terms],
        "n": int(m.nobs)})

# client_entered: driver-sisestus esineb ainult EL-is (1 ticket) -> ei ole hinnatav.
# client_dest_change: peaaegu sama tunnus kui dest_changed (kollineaarne) -> välja.
# Need kaks tegurit jäävad kirjeldavaks (f1, f3), mitte mudelisse.
T = ["prediction", "gps_low", "dest_changed"]
or_tab = pd.concat([
    logit(o, T + ["non_eu"], "kõik orderid, EL kontrollitud"),
    logit(o[o.eu == 0], T, "ainult mitte-EL"),
])
or_tab["significant_05"] = or_tab.p_value < 0.05
or_tab.to_csv(f"{OUT}/f4_odds_ratios.csv", index=False)

# ---------- 5. Mehhanism (order-tasandi rida) ----------
o["dist_ratio"] = o.dist / o.pred_dist.replace(0, np.nan)
o["price_ratio"] = o.metered / o.upfront.replace(0, np.nan)   # ainult upfront
o[["order_id_new", "had_ticket", "price_type", "gps_grp", "region",
   "dist_ratio", "price_ratio"]].to_csv(f"{OUT}/f5_mehhanism_orderid.csv", index=False)
mech = (o.groupby(["gps_grp", "had_ticket"])[["dist_ratio", "price_ratio"]]
          .median().reset_index())

# ---------- 6. Ajaline stabiilsus ----------
stab = pd.concat([rates(o, ["month", c], "kõik").rename(columns={c: "value"})
                    .assign(factor=factors[c]) for c in ["price_type", "gps_grp"]])
stab.to_csv(f"{OUT}/f6_stabiilsus_kuu.csv", index=False)

# ---------- Konsooli kokkuvõte ----------
pd.set_option("display.width", 200)
print(f"Orderid {len(o)}, ticketiga {TOTAL_T}, baseline {BASE:.3f}\n")
print(or_tab[["model", "term", "odds_ratio", "ci_low", "ci_high", "p_value"]].round(3), "\n")
print("Mehhanism, mediaanid:\n", mech.round(3), "\n")
print(stab[stab.small_n == False][["factor", "month", "value", "n", "rate"]].round(3))
