import csv
import os
import re
import sys
import html
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_common as seo

BRAND = "WineDB"
BASE = "https://winedb.dataengineered.io"


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def _esc(v):
    return html.escape(str(v if v is not None else ''))


def _oxford(items):
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _fnum(x):
    """Render a float without a trailing '.0' (14.5 -> '14.5', 14.0 -> '14')."""
    return f"{x:g}"


def vintage_h1(winery, wine, year):
    return f"{winery} {wine} — {year} Vintage"


def make_vintage_title(rec, extra=None):
    """Title entity is '<wine> <year>' (year never truncatable away); the winery
    is the preferred descriptor, with a short 'vintage' fallback so a long winery
    name is dropped before the entity ever is. `extra` (ABV/volume/slug) is folded
    into the entity itself when two vintages would otherwise collide, since a
    descriptor can be dropped by fit_title but the entity is protected."""
    entity = f"{seo._cut(rec['wine'], 34)} {rec['year']}"
    if extra:
        entity = f"{entity} ({extra})"
    return seo.fit_title(entity, [rec['winery'], "vintage"], BRAND)


def build_vintage_titles(vrecs):
    """Every vintage title unique; disambiguate collisions with ABV, then bottle
    volume, then both, then the (always-unique) slug as a last resort."""
    titles = {r['vid']: make_vintage_title(r) for r in vrecs}
    tiers = ['abv', 'vol', 'both', 'slug']
    tier_idx = {r['vid']: -1 for r in vrecs}
    for _ in range(len(tiers)):
        counts = Counter(titles.values())
        dupes = {t for t, c in counts.items() if c > 1}
        if not dupes:
            break
        for r in vrecs:
            if titles[r['vid']] not in dupes:
                continue
            tier_idx[r['vid']] += 1
            tier = tiers[min(tier_idx[r['vid']], len(tiers) - 1)]
            abv = (r['row'].get('abv_percent') or '').strip()
            vol = (r['row'].get('bottle_volume_ml') or '').strip()
            if tier == 'abv' and abv:
                extra = f"{abv}% ABV"
            elif tier == 'vol' and vol:
                extra = f"{vol} mL"
            elif tier == 'both' and (abv or vol):
                extra = ", ".join(x for x in [f"{abv}% ABV" if abv else None,
                                              f"{vol} mL" if vol else None] if x)
            else:
                extra = r['slug']
            titles[r['vid']] = make_vintage_title(r, extra)
    return titles


def dominant_variety(blend_rows):
    """The blend's largest-share variety, or None when there's no blend data."""
    parts = []
    for b in blend_rows:
        var = (b.get('variety_name') or '').strip()
        if not var:
            continue
        try:
            p = float(b.get('percent'))
        except (TypeError, ValueError):
            p = None
        parts.append((var, p))
    if not parts:
        return None
    parts.sort(key=lambda x: (x[1] is not None, x[1] or 0), reverse=True)
    return parts[0][0]


def wine_blend(blend_rows):
    """(chips_html, prose) for a vintage's varietal blend, sorted by percent desc."""
    parts = []
    for b in blend_rows:
        var = (b.get('variety_name') or '').strip()
        if not var:
            continue
        try:
            p = float(b.get('percent'))
        except (TypeError, ValueError):
            p = None
        parts.append((var, p))
    parts.sort(key=lambda x: (x[1] is not None, x[1] or 0), reverse=True)
    chips, txt = [], []
    for var, p in parts:
        label = f"{_esc(var)} {p:g}%" if p is not None else _esc(var)
        chips.append(f'<span class="badge" style="background:#3a0f20;color:#f0d0dc;margin:2px;">{label}</span>')
        txt.append(f"{var} ({p:g}%)" if p is not None else var)
    return " ".join(chips), _oxford(txt)


def vintage_profile(winery, wine, year, abv, vol, aging, cases, rel_price, val,
                    wine_type, appellation, w_country, w_region, blend_rows, tasting_rows):
    """Unique, data-derived profile from real vintage fields + relational joins."""
    blend_chips, blend_txt = wine_blend(blend_rows)
    descriptors = [(t.get('descriptor') or '').strip() for t in tasting_rows]
    descriptors = [d for d in descriptors if d]
    typ = f"{wine_type} wine" if wine_type else "wine"
    loc_parts = []
    for x in [appellation, w_region, w_country]:
        if x and x not in loc_parts:
            loc_parts.append(x)
    loc = ", ".join(loc_parts)
    p1 = f"The {_esc(year)} {_esc(wine)} from {_esc(winery)} is a {_esc(typ)}"
    if loc:
        p1 += f" from {_esc(loc)}"
    p1 += f", bottled at {_esc(abv)}% ABV in a {_esc(vol)} mL format."
    if blend_txt:
        p1 += f" Its varietal composition is {blend_txt}."
    if aging:
        p1 += f" Maturation regime: {_esc(aging)}."
    bits = []
    try:
        if cases:
            bits.append(f"a production run of {int(float(cases)):,} cases")
    except (TypeError, ValueError):
        pass
    try:
        if rel_price:
            bits.append(f"a release price of ${float(rel_price):,.0f}")
    except (TypeError, ValueError):
        pass
    p2 = ("This vintage carries " + _oxford(bits) + ".") if bits else ""
    try:
        if val and val not in ('None', 'NULL', ''):
            p2 += f" Its secondary-market valuation index stands at ${float(val):,.2f} USD, aggregated from a minimum of three auction observations."
    except (TypeError, ValueError):
        pass
    blend_block = (f'<div style="margin-top:1.4rem;"><div class="metric-label">Varietal Blend</div>'
                   f'<div style="margin-top:0.5rem;">{blend_chips}</div></div>') if blend_chips else ""
    desc_block = ""
    if descriptors:
        chips = " ".join(f'<span class="badge" style="background:rgba(212,175,55,0.12);color:#e8cf8a;margin:2px;">{_esc(d)}</span>' for d in descriptors)
        desc_block = (f'<div style="margin-top:1.4rem;"><div class="metric-label">Tasting Descriptors ({len(descriptors)})</div>'
                      f'<div style="margin-top:0.5rem;">{chips}</div></div>')
    winery_link = f'<a href="/wineries/{slugify(winery)}" style="color:#d4af37;">{_esc(winery)}</a>'
    p2_html = f'<p style="color:#d8c4cc; margin-top:0.6rem;">{p2}</p>' if p2 else ''
    return f"""
    <section style="margin-top:2rem; line-height:1.7;">
      <h2 style="font-family:'Outfit',sans-serif; font-size:1.4rem; color:#fcf6f8; margin-bottom:0.8rem;">Vintage Profile</h2>
      <p style="color:#d8c4cc;">{p1}</p>
      {p2_html}
      {blend_block}
      {desc_block}
      <p style="color:#a8929b; margin-top:1.4rem; font-size:0.9rem;">Producer record: {winery_link}.</p>
    </section>"""


def winery_prose(recs):
    """2-4 sentences computed from a winery's own vintage records; skip empty fields, never invent."""
    if not recs:
        return ""
    n = len(recs)
    years = sorted(r['year_int'] for r in recs if r['year_int'] is not None)
    varieties = sorted({r['variety'] for r in recs if r['variety']})
    abvs = []
    for r in recs:
        try:
            abvs.append(float(r['row'].get('abv_percent')))
        except (TypeError, ValueError):
            pass
    vols = sorted({(r['row'].get('bottle_volume_ml') or '').strip()
                   for r in recs if (r['row'].get('bottle_volume_ml') or '').strip()})

    sentences = []
    if years:
        span = f"{years[0]}" if years[0] == years[-1] else f"{years[0]} to {years[-1]}"
        sentences.append(f"WineDB tracks {n} vintage{'s' if n != 1 else ''} from this winery, spanning {span}.")
    if varieties:
        sentences.append(f"Recorded varietal composition across these vintages includes {_oxford(varieties)}.")
    if abvs:
        lo, hi = min(abvs), max(abvs)
        if lo == hi:
            sentences.append(f"Alcohol content is recorded at {_fnum(lo)}% ABV.")
        else:
            sentences.append(f"Alcohol content ranges from {_fnum(lo)}% to {_fnum(hi)}% ABV across these bottlings.")
    if vols:
        if len(vols) == 1:
            sentences.append(f"All tracked releases are bottled in a {vols[0]} mL format.")
        else:
            sentences.append(f"Bottle formats on record include {_oxford(vols)} mL.")
    return " ".join(sentences[:4])


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vintages_csv = os.path.join(root_dir, 'samples', 'vintages.csv')
    wineries_csv = os.path.join(root_dir, 'samples', 'wineries.csv')
    wines_csv = os.path.join(root_dir, 'samples', 'wines.csv')
    vintages_dir = os.path.join(root_dir, 'vintages')
    wineries_dir = os.path.join(root_dir, 'wineries')

    os.makedirs(vintages_dir, exist_ok=True)
    os.makedirs(wineries_dir, exist_ok=True)

    wines_by_id = {}
    if os.path.exists(wines_csv):
        with open(wines_csv, mode='r', encoding='utf-8', errors='ignore') as f:
            for row in csv.DictReader(f):
                wines_by_id[row.get('wine_id')] = row

    wineries = []
    wineries_by_name = {}
    if os.path.exists(wineries_csv):
        with open(wineries_csv, mode='r', encoding='utf-8', errors='ignore') as f:
            for row in csv.DictReader(f):
                name = row.get('name', '').strip()
                if name:
                    wineries.append(row)
                    wineries_by_name[name] = row

    vintages = []
    if os.path.exists(vintages_csv):
        with open(vintages_csv, mode='r', encoding='utf-8', errors='ignore') as f:
            for row in csv.DictReader(f):
                if row.get('wine_name') and row.get('vintage_year'):
                    vintages.append(row)

    blends_by_vid = defaultdict(list)
    tasting_by_vid = defaultdict(list)
    wines_by_key = {}
    blends_csv = os.path.join(root_dir, 'samples', 'blends.csv')
    tasting_csv = os.path.join(root_dir, 'samples', 'tasting_profiles.csv')
    if os.path.exists(blends_csv):
        with open(blends_csv, encoding='utf-8', errors='ignore') as f:
            for row in csv.DictReader(f):
                blends_by_vid[(row.get('vintage_id') or '').strip()].append(row)
    if os.path.exists(tasting_csv):
        with open(tasting_csv, encoding='utf-8', errors='ignore') as f:
            for row in csv.DictReader(f):
                tasting_by_vid[(row.get('vintage_id') or '').strip()].append(row)
    if os.path.exists(wines_csv):
        with open(wines_csv, encoding='utf-8', errors='ignore') as f:
            for row in csv.DictReader(f):
                wines_by_key[((row.get('winery_name') or '').strip(), (row.get('name') or '').strip())] = row

    print(f"Loaded {len(vintages)} vintage records and {len(wineries)} winery records from CSVs.")

    # --- Relational indices for related-links + winery prose -------------------
    vrecs = []
    for v in vintages:
        winery = v.get('winery_name', 'Estate').strip()
        wine = v.get('wine_name', 'Cuvee').strip()
        year = v.get('vintage_year', 'NV').strip()
        vid = (v.get('vintage_id') or '').strip()
        try:
            year_int = int(year)
        except ValueError:
            year_int = None
        vrecs.append({
            'row': v, 'winery': winery, 'wine': wine, 'year': year, 'year_int': year_int,
            'vid': vid, 'slug': slugify(f"{winery}-{wine}-{year}"),
            'variety': dominant_variety(blends_by_vid.get(vid, [])),
        })

    by_wine = defaultdict(list)
    for r in vrecs:
        by_wine[(r['winery'], r['wine'])].append(r)
    for key in by_wine:
        by_wine[key].sort(key=lambda r: (r['year_int'] if r['year_int'] is not None else 0))

    by_variety = defaultdict(list)
    for r in vrecs:
        if r['variety']:
            by_variety[r['variety'].lower()].append(r)
    for key in by_variety:
        by_variety[key].sort(key=lambda r: (r['winery'].lower(), r['wine'].lower(), r['year']))

    by_winery = defaultdict(list)
    for r in vrecs:
        by_winery[r['winery']].append(r)
    for key in by_winery:
        by_winery[key].sort(key=lambda r: (r['year_int'] if r['year_int'] is not None else 0, r['wine'].lower()))

    vrecs_by_name = sorted(vrecs, key=lambda r: (r['winery'].lower(), r['wine'].lower(), r['year']))
    vintage_titles = build_vintage_titles(vrecs)

    wineries_sorted = sorted(wineries, key=lambda w: (w.get('name') or '').strip().lower())
    winery_names_sorted = [(w.get('name') or '').strip() for w in wineries_sorted]
    by_country = defaultdict(list)
    for w in wineries_sorted:
        by_country[(w.get('country') or '').strip()].append((w.get('name') or '').strip())

    def vintage_related(rec):
        href_set, items = set(), []
        w_href = f"../wineries/{slugify(rec['winery'])}"
        items.append((w_href, rec['winery'], "producer"))
        href_set.add(w_href)

        siblings = by_wine.get((rec['winery'], rec['wine']), [])
        idx = next((i for i, s in enumerate(siblings) if s['vid'] == rec['vid']), None)
        adjacent = []
        if idx is not None:
            if idx - 1 >= 0:
                adjacent.append(siblings[idx - 1])
            if idx + 1 < len(siblings):
                adjacent.append(siblings[idx + 1])
        for s in adjacent[:2]:
            href = f"../vintages/{s['slug']}"
            if href in href_set:
                continue
            items.append((href, vintage_h1(s['winery'], s['wine'], s['year']), f"{s['year']} vintage of the same wine"))
            href_set.add(href)

        if rec['variety']:
            cands = [s for s in by_variety.get(rec['variety'].lower(), []) if s['winery'] != rec['winery']]
            for s in cands[:2]:
                href = f"../vintages/{s['slug']}"
                if href in href_set:
                    continue
                items.append((href, vintage_h1(s['winery'], s['wine'], s['year']), f"same {rec['variety']} varietal"))
                href_set.add(href)

        idx_g = next(i for i, s in enumerate(vrecs_by_name) if s['vid'] == rec['vid'])
        n_total = len(vrecs_by_name)
        step = 1
        while len(items) < 2 and step < n_total:
            cand = vrecs_by_name[(idx_g + step) % n_total]
            href = f"../vintages/{cand['slug']}"
            if href not in href_set and cand['vid'] != rec['vid']:
                items.append((href, vintage_h1(cand['winery'], cand['wine'], cand['year']), None))
                href_set.add(href)
            step += 1

        items = items[:5] + [("../vintages/", "All vintages", None)]
        return items

    def winery_related(name, country):
        href_set, items = set(), []
        for s in by_winery.get(name, []):
            href = f"../vintages/{s['slug']}"
            items.append((href, vintage_h1(s['winery'], s['wine'], s['year']), f"{s['year']}"))
            href_set.add(href)

        same_country = [n for n in by_country.get(country, []) if n != name]
        for n in same_country[:2]:
            href = f"../wineries/{slugify(n)}"
            if href in href_set:
                continue
            items.append((href, n, f"also in {country}" if country else None))
            href_set.add(href)

        idx_g = winery_names_sorted.index(name)
        n_total = len(winery_names_sorted)
        step = 1
        while len(items) < 2 and step < n_total:
            cand = winery_names_sorted[(idx_g + step) % n_total]
            href = f"../wineries/{slugify(cand)}"
            if href not in href_set and cand != name:
                items.append((href, cand, None))
                href_set.add(href)
            step += 1

        items.append(("../wineries/", "All wineries", None))
        return items

    sitemap_entries = [
        (f"{BASE}/", os.path.join(root_dir, "index.html"), "weekly", "1.0"),
    ]
    vintages_index = os.path.join(vintages_dir, "index.html")
    wineries_index = os.path.join(wineries_dir, "index.html")
    if os.path.exists(vintages_index):
        sitemap_entries.append((f"{BASE}/vintages/", vintages_index, "weekly", "0.8"))
    if os.path.exists(wineries_index):
        sitemap_entries.append((f"{BASE}/wineries/", wineries_index, "weekly", "0.8"))

    # Generate Vintage Specimen Pages
    for rec in vrecs:
        v = rec['row']
        winery = rec['winery']
        wine = rec['wine']
        year = rec['year']
        abv = v.get('abv_percent', '14.0').strip()
        vol = v.get('bottle_volume_ml', '750').strip()
        val = v.get('valuation_index_usd', '').strip()
        source = v.get('source_name', 'WineDB Verified Ledger').strip()

        slug = rec['slug']
        page_url = f"{BASE}/vintages/{slug}"
        out_path = os.path.join(vintages_dir, f"{slug}.html")
        sitemap_entries.append((page_url, out_path, "monthly", "0.8"))

        val_display = f"${float(val):,.2f} USD" if (val and val != 'None' and val != 'NULL') else "Requires >= 3 Auction Observations"

        vid = rec['vid']
        aging = (v.get('aging_regime') or '').strip()
        cases = (v.get('production_cases') or '').strip()
        rel_price = (v.get('release_price_usd') or '').strip()
        wine_meta = wines_by_key.get((winery, wine), {})
        wine_type = (wine_meta.get('wine_type') or '').strip()
        appellation = (wine_meta.get('appellation_name') or '').strip()
        winery_meta = wineries_by_name.get(winery, {})
        w_country = (winery_meta.get('country') or '').strip()
        w_region = (winery_meta.get('region') or '').strip()
        blend_rows = blends_by_vid.get(vid, [])
        tasting_rows = tasting_by_vid.get(vid, [])
        gold_badge = _esc(appellation or (wine_type.title() if wine_type else 'Provenance-Tracked'))
        appellation_disp = _esc(appellation or w_region or '—')
        try:
            production_disp = f"{int(float(cases)):,} cases" if cases else '—'
        except (TypeError, ValueError):
            production_disp = '—'
        profile_html = vintage_profile(winery, wine, year, abv, vol, aging, cases, rel_price, val,
                                       wine_type, appellation, w_country, w_region, blend_rows, tasting_rows)

        title = vintage_titles[rec['vid']]

        variety_clause = f" ({rec['variety']} blend)" if rec['variety'] else ""
        desc_raw = f"{year} {wine} from {winery}{variety_clause}: {abv}% ABV, {vol} mL bottle."
        desc_bits = []
        if aging:
            desc_bits.append(f"Aged {aging}.")
        if tasting_rows:
            desc_bits.append(f"{len(tasting_rows)} tasting descriptors on record.")
        if val and val not in ('None', 'NULL', ''):
            desc_bits.append("Secondary-market valuation tracked.")
        if desc_bits:
            desc_raw += " " + " ".join(desc_bits)
        description = seo.fit_desc(desc_raw)

        related_html = seo.related_block(vintage_related(rec), heading="Related", limit=6)

        html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{page_url}" />

  <meta property="og:title" content="{winery} {wine} ({year}) Vintage Record — WineDB" />
  <meta property="og:description" content="Exact ABV ({abv}%), bottle format ({vol} mL), varietal blend, tasting descriptors, and secondary auction market index." />
  <meta property="og:url" content="{page_url}" />
  <meta property="og:type" content="article" />
  <meta property="og:image" content="https://winedb.dataengineered.io/assets/winedb-cover.png" />

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Dataset",
    "name": "{winery} {wine} ({year}) Structured Vintage Record",
    "description": "Normalized vintage metrics for {winery} {wine} {year}: {abv}% ABV, {vol}ml format, varietal blend composition, tasting descriptors, aging regime, and secondary auction index.",
    "url": "{page_url}",
    "creator": {{"@type": "Organization", "name": "WineDB Initiative", "url": "https://winedb.dataengineered.io"}},
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "isAccessibleForFree": true,
    "variableMeasured": ["alcohol by volume percentage", "bottle format in ml", "varietal blend percentage", "tasting descriptors", "aging regime", "production cases", "secondary auction index USD"]
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://winedb.dataengineered.io/"}},
      {{"@type": "ListItem", "position": 2, "name": "Sommelier Explorer", "item": "https://winedb.dataengineered.io/#explorer"}},
      {{"@type": "ListItem", "position": 3, "name": "{winery} {wine} {year}", "item": "{page_url}"}}
    ]
  }}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <link rel="stylesheet" href="../index.css" />
  <style>
    body {{ background: #0c0508; color: #f2e8eb; font-family: 'Inter', sans-serif; padding: 3rem 1.5rem; }}
    .spec-container {{ max-width: 800px; margin: 0 auto; background: rgba(26, 11, 18, 0.85); border: 1px solid rgba(212, 175, 55, 0.25); border-radius: 12px; padding: 2.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
    .spec-header {{ border-bottom: 1px solid rgba(212, 175, 55, 0.2); padding-bottom: 1.5rem; margin-bottom: 2rem; }}
    .spec-header h1 {{ font-family: 'Outfit', sans-serif; font-size: 2.2rem; color: #fcf6f8; margin-bottom: 0.5rem; }}
    .badge {{ display: inline-block; background: #800020; color: #fff; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.85rem; font-weight: 600; margin-right: 0.5rem; }}
    .badge-gold {{ background: #d4af37; color: #000; }}
    .grid-metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
    .metric-card {{ background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); padding: 1.2rem; border-radius: 8px; }}
    .metric-label {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #a8929b; margin-bottom: 0.4rem; }}
    .metric-val {{ font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 700; color: #d4af37; }}
    .btn-back {{ display: inline-block; margin-top: 2rem; padding: 0.75rem 1.5rem; background: transparent; border: 1px solid #d4af37; color: #d4af37; text-decoration: none; border-radius: 6px; font-weight: 600; transition: all 0.2s; }}
    .btn-back:hover {{ background: #d4af37; color: #000; }}
  </style>
</head>
<body>
  <div class="spec-container">
    <div class="spec-header">
      <span class="badge">3NF Relational Record</span>
      <span class="badge badge-gold">{gold_badge}</span>
      <h1>{winery} {wine} — {year} Vintage</h1>
      <p style="color: #a8929b;">Verified primary producer specification and secondary auction market indices.</p>
    </div>
    <div class="grid-metrics">
      <div class="metric-card"><div class="metric-label">Harvest Vintage</div><div class="metric-val">{year}</div></div>
      <div class="metric-card"><div class="metric-label">Alcohol by Volume</div><div class="metric-val">{abv}%</div></div>
      <div class="metric-card"><div class="metric-label">Bottle Format</div><div class="metric-val">{vol} mL</div></div>
      <div class="metric-card"><div class="metric-label">Appellation</div><div class="metric-val" style="font-size: 1rem;">{appellation_disp}</div></div>
      <div class="metric-card"><div class="metric-label">Production</div><div class="metric-val" style="font-size: 1rem;">{production_disp}</div></div>
      <div class="metric-card"><div class="metric-label">Valuation Index</div><div class="metric-val" style="font-size: 1rem;">{val_display}</div></div>
    </div>
{profile_html}
    <div style="background: rgba(212, 175, 55, 0.08); padding: 1.2rem; border-left: 3px solid #d4af37; border-radius: 4px; font-size: 0.9rem;">
      <strong>Provenance Audit:</strong> This record is linked to primary authority <em>{source}</em>. All varietal composition percentages satisfy the database-level constraint `(0.0, 100.0]` with `SUM <= 100.001%`.
    </div>
    {related_html}
    <a href="/#explorer" class="btn-back">← Back to Sommelier Explorer</a>
  </div>
</body>
</html>"""
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    # Generate Winery Specimen Pages
    for w in wineries:
        name = w.get('name', '').strip()
        country = w.get('country', 'Global').strip()
        region = w.get('region', 'Prestige Region').strip()
        founded = w.get('founded_year', '').strip()
        url = w.get('source_url', '').strip()

        slug = slugify(name)
        page_url = f"{BASE}/wineries/{slug}"
        out_path = os.path.join(wineries_dir, f"{slug}.html")
        sitemap_entries.append((page_url, out_path, "monthly", "0.8"))

        recs = by_winery.get(name, [])
        n_vintages = len(recs)
        years = sorted(r['year_int'] for r in recs if r['year_int'] is not None)
        varieties = sorted({r['variety'] for r in recs if r['variety']})

        loc_descriptor = [d for d in [f"{region} winery" if region else None,
                                      f"{country} winery" if country else None, "winery"] if d]
        title = seo.fit_title(name, loc_descriptor, BRAND)

        year_span = ""
        if years:
            year_span = f"{years[0]}" if years[0] == years[-1] else f"{years[0]}–{years[-1]}"
        var_clause = f", spanning {_oxford(varieties)}" if varieties else ""
        if n_vintages:
            desc_raw = (f"{name} has {n_vintages} vintage{'s' if n_vintages != 1 else ''} in WineDB"
                       + (f" ({year_span})" if year_span else "") + f"{var_clause}.")
        else:
            desc_raw = f"{name} is a canonical winery record in WineDB."
        if founded:
            desc_raw += f" Founded {founded} in {region}, {country}."
        else:
            desc_raw += f" Located in {region}, {country}."
        description = seo.fit_desc(desc_raw)

        prose = winery_prose(recs)
        prose_html = (f'<p style="color: #d8c4cc; margin-top: 1rem; line-height: 1.6;">{prose}</p>'
                     if prose else '')

        related_html = seo.related_block(winery_related(name, country), heading="Related", limit=None)

        html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{page_url}" />

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Winery",
    "name": "{name}",
    "address": {{"@type": "PostalAddress", "addressRegion": "{region}", "addressCountry": "{country}"}},
    "url": "{page_url}"
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://winedb.dataengineered.io/"}},
      {{"@type": "ListItem", "position": 2, "name": "Wineries", "item": "https://winedb.dataengineered.io/#explorer"}},
      {{"@type": "ListItem", "position": 3, "name": "{name}", "item": "{page_url}"}}
    ]
  }}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <link rel="stylesheet" href="../index.css" />
  <style>
    body {{ background: #0c0508; color: #f2e8eb; font-family: 'Inter', sans-serif; padding: 3rem 1.5rem; }}
    .spec-container {{ max-width: 800px; margin: 0 auto; background: rgba(26, 11, 18, 0.85); border: 1px solid rgba(212, 175, 55, 0.25); border-radius: 12px; padding: 2.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
    .spec-header h1 {{ font-family: 'Outfit', sans-serif; font-size: 2.2rem; color: #fcf6f8; margin-bottom: 0.5rem; }}
    .badge {{ display: inline-block; background: #800020; color: #fff; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.85rem; font-weight: 600; margin-right: 0.5rem; }}
    .btn-back {{ display: inline-block; margin-top: 2rem; padding: 0.75rem 1.5rem; background: transparent; border: 1px solid #d4af37; color: #d4af37; text-decoration: none; border-radius: 6px; font-weight: 600; transition: all 0.2s; }}
    .btn-back:hover {{ background: #d4af37; color: #000; }}
  </style>
</head>
<body>
  <div class="spec-container">
    <span class="badge">Canonical Producer</span>
    <h1>{name}</h1>
    <p style="color: #d4af37; font-weight: 600; font-size: 1.1rem; margin-top: 0.5rem;">{region}, {country} {f'· Founded {founded}' if founded else ''}</p>
    <p style="color: #a8929b; margin-top: 1.5rem; line-height: 1.6;">Registered in the WineDB canonical producer table (`wineries.csv`). This entity serves as the parent foreign key (`winery_id`) for cuvee classifications (`wines.csv`) and harvest vintage metrics (`vintages.csv`).</p>
    {prose_html}
    {related_html}
    <a href="/#explorer" class="btn-back">← Back to Sommelier Explorer</a>
  </div>
</body>
</html>"""
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    n_written = seo.write_sitemap(root_dir, sitemap_entries)
    print(f"Generated {len(vintages)} vintage specimen pages, {len(wineries)} winery pages, and wrote sitemap.xml with {n_written} URLs.")

if __name__ == '__main__':
    main()
