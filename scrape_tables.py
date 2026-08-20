import requests
from bs4 import BeautifulSoup

URL = "https://www.englandrugby.com/fixtures-and-results/search-results?team=128822&competition=2074&division=78211&season=2026-2027#tables"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

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
  body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  .wrapper { overflow-x: auto; width: 100%; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; text-align: center; }
  th { background-color: #111; color: #fff; padding: 10px 8px; font-weight: 700; text-transform: uppercase; }
  td { padding: 10px 8px; border-bottom: 1px solid #eee; }
  .team-name { text-align: left; font-weight: 600; }
  tr.melksham { background-color: #fff0f0 !important; border-left: 4px solid #c30000; font-weight: 700; color: #c30000; }
  .pts { font-weight: 800; }
</style>
</head>
<body>
<div class="wrapper">
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th style="text-align:left;">Team</th>
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
        cols = [td.text.strip() for td in row.find_all(["td", "th"])]
        if len(cols) >= 12:
            is_melksham = "melksham" in cols[1].lower()
            row_class = ' class="melksham"' if is_melksham else ""
            
            html_output += f"""
      <tr{row_class}>
        <td>{cols[0]}</td>
        <td class="team-name">{cols[1]}</td>
        <td>{cols[2]}</td>
        <td>{cols[3]}</td>
        <td>{cols[4]}</td>
        <td>{cols[5]}</td>
        <td>{cols[6]}</td>
        <td>{cols[7]}</td>
        <td>{cols[8]}</td>
        <td>{cols[9]}</td>
        <td>{cols[10]}</td>
        <td class="pts">{cols[11]}</td>
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
        
    print("Table updated successfully.")

if __name__ == "__main__":
    fetch_and_build_table()
