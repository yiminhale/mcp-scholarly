from scholarly import scholarly
from typing import List

MAX_RESULTS = 10


class GoogleScholar:
    def __init__(self):
        self.scholarly = scholarly

    def get_scholarly(self, keyword):
        return self.scholarly.search_pubs(keyword)

    @staticmethod
    def _parse_results(search_results):
        articles = []
        results_iter = 0
        for searched_article in search_results:
            bib = searched_article.get('bib', {})
            title = bib.get('title', None)
            abstract = bib.get('abstract', None)
            pub_url = searched_article.get('pub_url', None)
            article_string = "\n".join([title, abstract, pub_url])
            articles.append(article_string)
            results_iter += 1
            if results_iter > MAX_RESULTS:
                break
        return articles

    def search_pubs(self, keyword) -> List[str]:
        search_results = self.scholarly.search_pubs(keyword)
        articles = self._parse_results(search_results)
        return articles
