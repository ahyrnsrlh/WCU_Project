class Article:
    def __init__(self, title, link, authors, year, cited):
        self.title = title
        self.link = link
        self.authors = authors
        self.year = year
        self.cited = cited

    def to_dict(self):
        return {
            'Title': self.title,
            'Link': self.link,
            'Authors': self.authors,
            'Year': self.year,
            'Cited': self.cited
        }
