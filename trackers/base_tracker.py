from bs4 import BeautifulSoup
from utils.fetcher import fetch_html

class Tracker:
    
    
    def __init__(self, name, base_url, config):
        self.name = name
        self.base_url = base_url
        self.config = config
        
    async def track_pricing(self):
        html = await fetch_html(self.base_url + self.config['pricing_page'])
        soup = BeautifulSoup(html, 'html.parser')
        
        selector = self.config.get("price_selector")
        elements = soup.select(selector)
        text = " ".join(element.get_text(strip=True) + " " for element in elements)
        
        return {"pricing_text": text}

    async def track_blogs(self):
        html = await fetch_html(self.base_url + self.config['blog_page'])
        soup = BeautifulSoup(html, 'html.parser')
        
        selector = self.config.get("blog_selector")
        elements = soup.select(selector)
        text = " ".join(
            element.get_text(strip=True)
            for element in elements
            if not any(year in element.get_text() + " " for year in ["2021", "2022", "2023", "2024"])
        )
                
        return {"blog_text": text}
    