import codecs
import time
import urllib2
from datetime import datetime
from parser.buli_parser import BuliParser
from parser.news_parser import BVDGParser, SpeyerParser, SchwedtParser
from tabulate import tabulate

def update_readme(blog_parsers_classes):
    headers = ["Blog Name", "Heading", "Date", "Image", "Content"]
    table = list()
    for blog_parser_class in blog_parsers_classes:
        blog_parser_instance = blog_parser_class()
        page = urllib2.urlopen(blog_parser_class.ARTICLES_URL + "1").read()
        first_article_url = blog_parser_instance.parse_article_urls(page)[0]
        article = blog_parser_class.parse_article_from_url(first_article_url)
        row = [blog_parser_instance.BLOG_NAME,
               "[{}]({})".format(article["heading"], article["url"]),
               datetime.fromtimestamp(float(article["date"])).strftime("%Y-%m-%d"),
               "<img src='{}' width='100px'/>".format(article["image"]) if article["image"] else "",
               article["content"][:20] + "..."
               ]
        table.append(row)
    table = sorted(table, key=lambda k: datetime.strptime(k[2], "%Y-%m-%d"), reverse=True)

    with codecs.open("README.md", 'r', encoding='utf8') as f:
        readme = f.read()
    before_news = readme.split("## Current News")[0]
    new_readme = before_news + "## Current News\n\n" + tabulate(table, headers, tablefmt="pipe")
    with codecs.open("README.md", 'w', encoding='utf8') as f:
        f.write(new_readme)

if __name__ == '__main__':
    SEASON = "1516"
    BuliParser1A = BuliParser(SEASON, "1", "Gruppe+A", "1A_schedule", "1A_competitions", "1A_table", "1. Bundesliga - Gruppe A", "2")
    BuliParser1B = BuliParser(SEASON, "1", "Gruppe+B", "1B_schedule", "1B_competitions", "1B_table", "1. Bundesliga - Gruppe B", "3")
    BuliParser2South = BuliParser(SEASON, "2", "S%FCdwest", "2South_schedule", "2South_competitions", "2South_table", u"2. Bundesliga - Staffel S\u00fcdwest", "5")
    BuliParser2North = BuliParser(SEASON, "2", "Nordost", "2North_schedule", "2North_competitions", "2North_table", "2. Bundesliga - Staffel Nordost", "6")
    BuliParser2Middle = BuliParser(SEASON, "2", "Mitte", "2Middle_schedule", "2Middle_competitions", "2Middle_table", "2. Bundesliga - Staffel Mitte", "7")

    #for parser in [BuliParser1A, BuliParser1B, BuliParser2South, BuliParser2North, BuliParser2Middle]:
    #    parser.create_buli_files()

    blog_parsers_classes = [BVDGParser, SpeyerParser, SchwedtParser]
    for blog_parser_class in blog_parsers_classes:
        blog_parser_instance = blog_parser_class()
        blog_parser_instance.parse_articles()

    time.sleep(60 * 60)
