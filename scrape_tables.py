import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

URL = "https://www.englandrugby.com/fixtures-and-results/search-results?team=128822&competition=2074&division=78211&season=2026-2027#tables"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# Custom uploaded badge path
FAWNS_BADGE_PATH = "Fawns%20Badge.png"

# Fallback SVG rugby icon
DEFAULT_RUGBY_ICON = """<svg class="badge-icon" viewBox="0 0 24 24" fill="none" stroke="#666666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="12" rx="10" ry="6" transform="rotate(-45 12 12)"/><path d="M5 5l14 14"/><path d="M12 8l-2 2"/><path d="M16 12l-2 2"/></svg>"""

def fetch_and_build_table():
    res = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    
    table = soup.find("table")
    if not table:
        print("Error: Could not find table element on page.")
        return

    rows = table.find_all("tr")

    html_output = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { 
      margin: 0; 
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif; 
      color: #222;
      background: transparent;
  }
  .wrapper { 
      overflow-x: auto; 
      width: 100%; 
      border: 1px solid #e5e5e5; 
      border-radius: 4px; 
      box-shadow: 0 2px 5px rgba(0,0,0,0.03);
      background: #ffffff;
  }
  table { 
      width: 100%; 
      border-collapse: collapse; 
      font-size: 13px; 
      text-align: center; 
  }
  thead {
      background-color: #ffffff;
      border-bottom: 2px solid #e5e5e5;
  }
  th { 
      color: #111111; 
      padding: 12px 8px; 
      font-size: 12px;
      font-weight: 800; 
      text-transform: uppercase; 
      letter-spacing: 0.5px;
  }
  td { 
      padding: 10px 8px; 
      border-bottom: 1px solid #e5e5e5; 
      color: #333333;
      vertical-align: middle;
  }
  tr:last-child td {
      border-bottom: none;
  }
  .team-cell { 
      text-align: left; 
      font-weight: 700; 
      color: #111111;
      display: flex;
      align-items: center;
      gap: 10px;
  }
  .badge {
      width: 24px;
      height: 24px;
      object-fit: contain;
  }
  .badge-icon {
      width: 20px;
      height: 20px;
      padding: 2px;
  }
  tr.melksham { 
      background-color: #ffffff !important; 
      border-left: 4px solid #c30000; 
  }
  tr.melksham td { 
      font-weight: 800; 
  }
  tr.melksham .team-name {
      color: #c30000 !important;
  }
  .pts { 
      font-weight: 800; 
      color: #111111;
  }
</style>
</head>
<body>
<div class="wrapper">
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th style="text-align:left; padding-left: 12px;">Team</th>
        <th>P</th>
        <th>W</th>
        <th>D</th>
        <th>L</th>
        <th>PF</th>
        <th>PA</th>
        <th>+/-</th>
        <th>TB</th>
        <th>LB</th>
        <th>Pts</th>
      </tr>
    </thead>
    <tbody>
"""

    for row in rows[1:]:
        cols = row.find_all(["td", "th"])
        if len(cols) >= 12:
            rank = cols[0].text.strip()
            
            team_td = cols[1]
            team_name = team_td.text.strip()
            is_melksham = "melksham" in team_name.lower()
            
            # Use custom uploaded badge for Melksham
            if is_melksham:
                badge_html = f'<img src="{FAWNS_BADGE_PATH}" class="badge" alt="Melksham Fawns" />'
            else:
                img_tag = team_td.find("img")
                badge_html = DEFAULT_RUGBY_ICON
                if img_tag and img_tag.get("src"):
                    src = img_tag["src"]
                    if not ("placeholder" in src.lower() or "default" in src.lower() or "icon" in src.lower()):
                        badge_url = urljoin(URL, src)
                        badge_html = f'<img src="{badge_url}" class="badge" alt="" onerror="this.outerHTML=\'{DEFAULT_RUGBY_ICON}\'" />'
            
            row_class = ' class="melksham"' if is_melksham else ""
            
            html_output += f"""
      <tr{row_class}>
        <td>{rank}</td>
        <td>
          <div class="team-cell">
            {badge_html}
            <span class="team-name">{team_name}</span>
          </div>
        </td>
        <td>{cols[2].text.strip()}</td>
        <td>{cols[3].text.strip()}</td>
        <td>{cols[4].text.strip()}</td>
        <td>{cols[5].text.strip()}</td>
        <td>{cols[6].text.strip()}</td>
        <td>{cols[7].text.strip()}</td>
        <td>{cols[8].text.strip()}</td>
        <td>{cols[9].text.strip()}</td>
        <td>{cols[10].text.strip()}</td>
        <td class="pts">{cols[11].text.strip()}</td>
      </tr>"""

    html_output += """
    </tbody>
  </table>
</div>
</body>
</html>
"""

    with open("table-counties-1.html", "w", encoding="utf-8") as f:
        f.write(html_output)

if __name__ == "__main__":
    fetch_and_build_table()
