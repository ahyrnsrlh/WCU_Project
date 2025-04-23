import csv

def write_articles_to_csv(articles, filename='sinta_articles.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Title', 'Link', 'Authors', 'Year', 'Cited'])
        writer.writeheader()
        for article in articles:
            writer.writerow(article.to_dict())
