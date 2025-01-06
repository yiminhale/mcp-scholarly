from scholarly import scholarly
from typing import List

class GoogleScholar:
    def __init__(self):
        self.scholarly = scholarly.Scholarly()

    def get_scholarly(self, keyword):
        return self.scholarly.search_pubs(keyword)

    @staticmethod
    def _parse_results(search_results):
        articles = []
        for searched_article in search_results:
            bib = searched_article.get('bib', {})
            title = bib.get('title', None)
            abstract = bib.get('abstract', None)
            pub_url = searched_article.get('pub_url', None)
            article_string = "\n".join([title, abstract, pub_url])
            articles.append(article_string)
        return articles

    def search_pubs(self, keyword) -> List[str]:
        search_results = self.scholarly.search_pubs(keyword)
        articles = self._parse_results(search_results)
        return articles
