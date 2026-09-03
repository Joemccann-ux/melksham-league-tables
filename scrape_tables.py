import requests
import json
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# Raw GitHub Badge URLs
MENS_BADGE_URL = "https://melkshamnews.com/wp-content/uploads/2026/09/Badge-RC-1.png"
FAWNS_BADGE_URL = "https://raw.githubusercontent.com/Joemccann-ux/melksham-league-tables/main/Fawns%20Badge.png"
DEFAULT_RUGBY_ICON = """<svg class="badge" viewBox="0 0 24 24" fill="none" stroke="#666666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>"""

WOMEN_ICS_URL = "https://ics.ecal.com/ecal-sub/6a946df25b80e60002dff5a3/RFU.ics"
MENS_ICS_URL = "https://ics.ecal.com/ecal-sub/6a5909492e368d00021229e9/RFU.ics"

CONFIGS = [
    {
        "name": "U16 Fawns",
        "url": "https://www.englandrugby.com/fixtures-and-results/search-results?team=128822&competition=2074&division=78211&season=2026-2027#tables",
        "output_file": "table-counties-1.html"
    },
    {
        "name": "U18 Academy",
        "url": "https://www.englandrugby.com/fixtures-and-results/search-results?team=130920&competition=2509&division=78155&season=2026-2027#tables",
        "output_file": "table-u18.html"
    },
    {
        "name": "Melksham Women 1XV",
        "url": "https://www.englandrugby.com/fixtures-and-results/search-results?team=13650&competition=1782&division=76187&season=2026-2027#tables",
        "output_file": "table-women.html"
    },
    {
        "name": "Melksham Mens 1st XV",
        "url": "https://www.englandrugby.com/fixtures-and-results/search-results?team=13645&competition=1699&division=75794&season=2026-2027#tables",
        "output_file": "table-mens.html"
    }
]

def generate_html(table_rows_html, title_name):
    accent_color = "#0072ce" if "Mens" in title_name else "#e6007e"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title_name} Standings</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
    body {{ font-family: 'Inter', sans-serif; background: transparent; color: #111111; margin: 0; padding: 0; }}
    .table-wrap {{ width: 100%; overflow-x: auto; background: #ffffff; border-radius: 8px; border: 1px solid #e5e5e5; }}
    table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 13px; }}
    thead {{ background-color: #0d0e12; color: #ffffff; }}
    th {{ padding: 12px 8px; font-size: 11px; font-weight: 800; text-transform: uppercase; border-bottom: 2px solid {accent_color}; }}
    th.team-col, td.team-col {{ text-align: left; padding-left: 14px; }}
    td {{ padding: 10px 8px; border-bottom: 1px solid #eeeeee; font-weight: 600; }}
    tr:nth-child(even) {{ background-color: #f9f9fb; }}
    tr.highlight-melksham {{ background-color: rgba(0, 114, 206, 0.08) !important; font-weight: 800; }}
    tr.highlight-melksham td {{ color: {accent_color}; }}
    .badge {{ width: 20px; height: 22px; vertical-align: middle; margin-right: 8px; object-fit: contain; }}
  </style>
</head>
<body>
  <div class="table-wrap">
    <table>
      <thead>
        <tr><th>#</th><th class="team-col">TEAM</th><th>P</th><th>W</th><th>D</th><th>L</th><th>PF</th><th>PA</th><th>+/-</th><th>TB</th><th>LB</th><th>PTS</th></tr>
      </thead>
      <tbody>
        {table_rows_html}
      </tbody>
    </table>
  </div>
</body>
</html>"""

def parse_ics_fixtures(ics_url, output_json):
    print(f"Fetching and parsing ICS Calendar -> {output_json}...")
    try:
        res = requests.get(ics_url, headers=HEADERS, timeout=15)
        events = []
        blocks = res.text.split("BEGIN:VEVENT")
        
        for block in blocks[1:]:
            block_content = block.split("END:VEVENT")[0]
            summary_m = re.search(r"SUMMARY:(.*)", block_content)
            start_m = re.search(r"DTSTART.*:(.*)", block_content)
            location_m = re.search(r"LOCATION:(.*)", block_content)
            
            if summary_m and start_m:
                title = summary_m.group(1).strip().replace("\\,", ",")
                dt_str = start_m.group(1).strip().replace("Z", "")
                location = location_m.group(1).strip().replace("\\,", ",") if location_m else "TBC Ground"
                
                if "Welcome to RFU" in title or "ECAL" in title:
                    continue

                try:
                    digits = re.sub(r'[^0-9]', '', dt_str)
                    y, m, d = digits[0:4], digits[4:6], digits[6:8]
                    hh = digits[8:10] if len(digits) >= 10 else "15"
                    mm = digits[10:12] if len(digits) >= 12 else "00"
                    ss = digits[12:14] if len(digits) >= 14 else "00"
                    iso_date = f"{y}-{m}-{d}T{hh}:{mm}:{ss}"
                except Exception:
                    iso_date = dt_str
                    
                events.append({"title": title, "date": iso_date, "location": location})
                
        events.sort(key=lambda x: x["date"])
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)
        print(f"Successfully generated {output_json}")
    except Exception as e:
        print(f"Error fetching ICS calendar {ics_url}: {e}")

def scrape_and_build():
    for config in CONFIGS:
        print(f"Scraping {config['name']}...")
        try:
            res = requests.get(config["url"], headers=HEADERS, timeout=15)
            soup = BeautifulSoup(res.text, "html.parser")
            table = soup.find("table")
            rows_out = []
            if table:
                rows = table.find_all("tr")[1:]
                for row in rows:
                    cols = row.find_all(["td", "th"])
                    if len(cols) >= 10:
                        team_cell = cols[1]
                        team_text = team_cell.get_text(strip=True)
                        is_melksham = "melksham" in team_text.lower()
                        cls = ' class="highlight-melksham"' if is_melksham else ''

                        # MENS 1XV BADGE LOGIC
                        if config["name"] == "Melksham Mens 1st XV":
                            if is_melksham:
                                badge_img = f'<img class="badge" src="{MENS_BADGE_URL}" alt="Melksham Badge">'
                            else:
                                badge_img = DEFAULT_RUGBY_ICON

                        # ORIGINAL UNTOUCHED LOGIC FOR WOMEN, U16 FAWNS & ACADEMY
                        else:
                            badge_img = f'<img class="badge" src="{FAWNS_BADGE_URL}" alt="">' if is_melksham else DEFAULT_RUGBY_ICON

                        cells_td = [
                            f"<td>{cols[0].get_text(strip=True)}</td>",
                            f'<td class="team-col">{badge_img} {team_text}</td>'
                        ]

                        for c in cols[2:]:
                            cells_td.append(f"<td>{c.get_text(strip=True)}</td>")

                        rows_out.append(f"<tr{cls}>" + "".join(cells_td) + "</tr>")

            final_html = generate_html("\n".join(rows_out), config["name"])
            with open(config["output_file"], "w", encoding="utf-8") as f:
                f.write(final_html)
            print(f"Successfully generated {config['output_file']}")

        except Exception as e:
            print(f"Error scraping {config['name']}: {e}")

if __name__ == "__main__":
    scrape_and_build()
    parse_ics_fixtures(WOMEN_ICS_URL, "fixtures-women.json")
    parse_ics_fixtures(MENS_ICS_URL, "fixtures-mens.json")
