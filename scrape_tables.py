import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

FAWNS_BADGE_URL = "https://raw.githubusercontent.com/Joemccann-ux/melksham-league-tables/main/Fawns%20Badge.png"
DEFAULT_RUGBY_ICON = """<svg class="badge" viewBox="0 0 24 24" fill="none" stroke="#666666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>"""
WOMEN_ICS_URL = "https://ics.ecal.com/ecal-sub/6a946df25b80e60002dff5a3/RFU.ics"

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
    }
]

def generate_html(table_rows_html, title_name):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title_name} Standings</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: transparent;
      color: #111111;
      margin: 0; padding: 0;
    }}
    .table-wrap {{
      width: 100%;
      overflow-x: auto;
      background: #ffffff;
      border-radius: 8px;
      border: 1px solid #e5e5e5;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: center;
      font-size: 13px;
    }}
    thead {{
      background-color: #0d0e12;
      color: #ffffff;
    }}
    th {{
      padding: 12px 8px;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      border-bottom: 2px solid #e6007e;
    }}
    th.team-col, td.team-col {{
      text-align: left;
      padding-left: 14px;
    }}
    td {{
      padding: 10px 8px;
      border-bottom: 1px solid #eeeeee;
      font-weight: 600;
    }}
    tr:nth-child(even) {{ background-color: #f9f9fb; }}
    tr.highlight-melksham {{
      background-color: rgba(230, 0, 126, 0.08) !important;
      font-weight: 800;
    }}
    tr.highlight-melksham td {{ color: #e6007e; }}
    .badge {{
      width: 20px; height: 22px;
      vertical-align: middle;
      margin-right: 8px;
      object-fit: contain;
    }}
  </style>
</head>
<body>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th class="team-col">TEAM</th>
          <th>P</th><th>W</th><th>D</th><th>L</th>
          <th>PF</th><th>PA</th><th>+/-</th><th>TB</th><th>LB</th><th>PTS</th>
        </tr>
      </thead>
      <tbody>
        {table_rows_html}
      </tbody>
    </table>
  </div>
</body>
</html>"""

def parse_ics_fixtures():
    print("Fetching and parsing Women ICS Calendar...")
    try:
        res = requests.get(WOMEN_ICS_URL, headers=HEADERS, timeout=15)
        text = res.text
        events = []
        blocks = text.split("BEGIN:VEVENT")
        
        for block in blocks[1:]:
            block_content = block.split("END:VEVENT")[0]
            summary_m = re.search(r"SUMMARY:(.*)", block_content)
            start_m = re.search(r"DTSTART.*:(.*)", block_content)
            location_m = re.search(r"LOCATION:(.*)", block_content)
            
            if summary_m and start_m:
                title = summary_m.group(1).strip().replace("\\,", ",")
                dt_str = start_m.group(1).strip().replace("Z", "")
                location = location_m.group(1).strip().replace("\\,", ",") if location_m else "TBC Ground"
                
                # Exclude promo and non-match entries
                if "Welcome to RFU" in title or "ECAL" in title:
                    continue

                # Format clean ISO timestamp (YYYY-MM-DDTHH:MM:SS)
                try:
                    digits = re.sub(r'[^0-9]', '', dt_str)
                    y, m, d = digits[0:4], digits[4:6], digits[6:8]
                    hh = digits[8:10] if len(digits) >= 10 else "14"
                    mm = digits[10:12] if len(digits) >= 12 else "00"
                    ss = digits[12:14] if len(digits) >= 14 else "00"
                    iso_date = f"{y}-{m}-{d}T{hh}:{mm}:{ss}"
                except Exception:
                    iso_date = dt_str
                    
                events.append({
                    "title": title,
                    "date": iso_date,
                    "location": location
                })
                
        # Sort chronologically
        events.sort(key=lambda x: x["date"])
        
        with open("fixtures-women.json", "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)
        print("Successfully generated fixtures-women.json")
        
    except Exception as e:
        print(f"Error fetching ICS calendar: {e}")

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
                        team_text = cols[1].get_text(strip=True)
                        is_melksham = "melksham" in team_text.lower()
                        cls = ' class="highlight-melksham"' if is_melksham else ''
                        
                        badge_img = f'<img class="badge" src="{FAWNS_BADGE_URL}" alt="">' if is_melksham else DEFAULT_RUGBY_ICON
                        
                        cells_td = [f"<td>{cols[0].get_text(strip=True)}</td>"]
                        cells_td.append(f'<td class="team-col">{badge_img} {team_text}</td>')
                        
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
    parse_ics_fixtures()
