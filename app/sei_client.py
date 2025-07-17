# app/sei_client.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

SEI_BASE    = "https://sei.antt.gov.br/sei/"
SEARCH_PATH = "modulos/pesquisa/md_pesq_processo_pesquisar.php"

class SEIClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent":      "Mozilla/5.0",
            "Accept":          "text/html,application/xhtml+xml",
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Referer":         urljoin(SEI_BASE, SEARCH_PATH)
        })
        init = self.session.get(self.session.headers["Referer"], timeout=10)
        init.raise_for_status()

    def pesquisar_por_interessado(self, nome: str, id_orgao: int = 0):
        url = urljoin(SEI_BASE, SEARCH_PATH)
        # 2) Monta o form‑data exatamente como o formulário envia
        data = {
            "acao_externa":            "protocolo_pesquisar",
            "acao_origem_externa":     "protocolo_pesquisar",
            "id_orgao_acesso_externo": id_orgao,
            "txtPesquisaLivre":        nome,
            "chkInteressado":          "on"
        }
        # 3) Envia POST com form‑data
        resp = self.session.post(url, data=data, timeout=30)
        resp.raise_for_status()
        return self._parse_html(resp.text)

    def _parse_html(self, html: str):
        soup  = BeautifulSoup(html, "html.parser")
        table = soup.find("table", id="tblResultado") or soup.find("table")
        if not table:
            return []
        headers = [th.get_text(strip=True) for th in table.thead.find_all("th")]
        results = []
        for tr in table.tbody.find_all("tr"):
            cols = [td.get_text(strip=True) for td in tr.find_all("td")]
            results.append(dict(zip(headers, cols)))
        return results
