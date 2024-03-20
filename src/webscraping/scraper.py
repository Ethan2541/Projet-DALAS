import bs4
import numpy as np
import pandas as pd
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib import request

class Scraper():
    def __init__(self):
        self.base_url = 'https://goodreads.com'
        self.genres_uri = []
        self.lists_uri = []
        self.books_uri = []
        self.books_data = []
        self.driver = None

    @classmethod
    def load_from_files(cls, genres_filename, lists_filename, books_filename):
        scraper = cls()
        with open(genres_filename, 'r') as f:
            scraper.genres_uri = f.read().split('\n')
        with open(lists_filename, 'r') as f:
            scraper.lists_uri = f.read().split('\n')
        with open(books_filename, 'r') as f:
            scraper.books_uri = f.read().split('\n')
        return scraper

    def scrape(self):
        self.scrape_homepage()
        self.scrape_all_catalogs()
        self.scrape_all_lists()
        self.scrape_all_books()
        self.save_data()


    def save_data(self, filename):
        columns = ['title', 'author', 'price', 'description', 'author_description', 'genres', 'n_ratings', 'n_reviews', 'ratings', 'pages_format', 'publication_info', 'literary_awards', 'original_title', 'series', 'characters', 'format', 'published', 'isbn', 'language', 'setting']
        data = pd.DataFrame(self.books_data, columns=columns)
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if len(lines) > 0:
            data.to_csv(filename, mode='a', index=False, header=False)
        else:
            data.to_csv(filename, index=False)


    def scrape_homepage(self):
        request_text = request.urlopen(self.base_url).read()
        home_page = bs4.BeautifulSoup(request_text, "html.parser")
        links = home_page.find_all('a', {'class': 'gr-hyperlink'})
        for a in links:
            href = a.get('href', [])
            if href.startswith('/genres/'):
                self.genres_uri.append(href)
        with open('./loading_files/genres_uri.txt', 'w') as f:
            f.write('\n'.join(self.genres_uri))


    def scrape_all_catalogs(self, save_progress=True):
        for genre in self.genres_uri:
            self.scrape_catalog(self.base_url + genre)
        
        if save_progress:
            with open('./loading_files/lists_uri.txt', 'w') as f:
                f.write('\n'.join(self.lists_uri))
            with open('./loading_files/books_uri.txt', 'w') as f:
                f.write('\n'.join(self.books_uri))

    def scrape_catalog(self, url):
        request_text = request.urlopen(url).read()
        catalog_page = bs4.BeautifulSoup(request_text, "html.parser")
        links = catalog_page.find_all('a')
        for a in links:
            href = a.get('href', '')
            if href.startswith('/list/show/') and href not in self.lists_uri:
                self.lists_uri.append(href)
            elif href.startswith('/book/show/') and href not in self.books_uri:
                self.books_uri.append(href)


    def scrape_all_lists(self, save_progress=True):
        try:
            for list_uri in self.lists_uri:
                print(list_uri)
                self.scrape_list(self.base_url + list_uri)
        except:
            if save_progress:
                with open('./loading_files/books_uri.txt', 'w') as f:
                    f.write('\n'.join(self.books_uri))
            return list_uri

    def scrape_list(self, url, page_max=10):
        if f'page={page_max+1}' in url:
            return
        request_text = request.urlopen(url).read()
        list_page = bs4.BeautifulSoup(request_text, "html.parser")
        links = list_page.find_all('a', {'class': 'bookTitle'})
        for a in links:
            href = a.get('href', '')
            if href.startswith('/book/show/') and href not in self.books_uri:
                self.books_uri.append(href)
        next_link = list_page.find('a', {'class': 'next_page'})
        if next_link is not None:
            url = self.base_url + next_link.get('href', [])
            self.scrape_list(url)


    def scrape_all_books(self):
        self.driver = webdriver.Firefox()
        for book in self.books_uri:
            try:
                self.scrape_book(self.base_url + book)
            except:
                continue
        self.driver.quit()
            
    def scrape_n_books(self, n):
        self.driver = webdriver.Firefox()
        cpt = 0
        for book in self.books_uri:
            try:
                self.scrape_book(self.base_url + book)
                cpt += 1
            except Exception as e:
                continue
            finally:
                if cpt == n:
                    break
            
        self.driver.quit()
        

    def scrape_book(self, url):
        self.driver.get(url)

        try:
            close_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close"]')
            close_button.click()
        except:
            pass

        more_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Book details and editions"]')
        more_button.click()

        book_page = bs4.BeautifulSoup(self.driver.page_source, "html.parser")
        book_data = {}
        book_data['title'] = book_page.find('h1', {'class': 'Text__title1'}).text
        book_data['author'] = book_page.find('span', {'class': 'ContributorLink__name'}).text
        book_data['price'] = float(re.search(r'\d+.\d+', book_page.find('button', {'class': 'Button--buy'}).find('span', {'class': 'Button__labelItem'}).text).group())
        
        descriptions = book_page.find_all('div', {'class': 'DetailsLayoutRightParagraph__widthConstrained'})
        book_data['description'] = descriptions[0].find('span', {'class': 'Formatted'}).text.replace('\n', ' ')
        book_data['author_description'] = descriptions[1].find('span', {'class': 'Formatted'}).text.replace('\n', ' ')
        book_data['genres'] = [block.text for block in book_page.find('div', {'data-testid': 'genresList'}).find_all('span', {'class': 'Button__labelItem'})]

        book_data['n_ratings'] = float(book_page.find('span', {'data-testid': 'ratingsCount'}).text.split()[0].replace(',', ''))
        book_data['n_reviews'] = float(book_page.find('span', {'data-testid': 'reviewsCount'}).text.split()[0].replace(',', ''))
        book_data[f'ratings'] = [float(book_page.find('div', {'data-testid': f'labelTotal-{n_stars}'}).text.split()[0].replace(',', '')) for n_stars in range(1,6)]

        book_details = book_page.find('div', {'class': 'BookDetails'})
        book_data['pages_format'] = book_details.find('p', {'data-testid': 'pagesFormat'}).text
        book_data['publication_info'] = book_details.find('p', {'data-testid': 'publicationInfo'}).text

        work_details = book_details.find('div', {'class': 'WorkDetails'})
        work_dt = work_details.find_all('dt')
        work_categories = [dt.text.lower().replace(' ', '_') for dt in work_dt]

        work_dd = work_details.find_all('dd')
        work_data = []
        for dd in work_dd:
            if dd.find('a') is not None:
                work_data.append([a.text for a in dd.find_all('a')])
            else:
                work_data.append(dd.find('div', {'data-testid': 'contentContainer'}).text)

        for categorie, data in zip(work_categories, work_data):
            book_data[categorie] = data

        edition_details = book_details.find('div', {'class': 'EditionDetails'})
        edition_dt = edition_details.find_all('dt')
        edition_categories = [dt.text.lower().replace(' ', '_') for dt in edition_dt]

        edition_dd = edition_details.find_all('dd')
        edition_data = []
        for dd in edition_dd:
            if dd.find('a') is not None:
                edition_data.append([a.text for a in dd.find_all('a')])
            else:
                edition_data.append(dd.find('div', {'data-testid': 'contentContainer'}).text)

        for categorie, data in zip(edition_categories, edition_data):
            book_data[categorie] = data

        self.books_data.append(book_data)

        # TO BE DELETED
        with open('scraped_books_uri.txt', 'a') as f:
            f.write(url + '\n')



if __name__ == '__main__':
    # while True:
    #     scraper = Scraper.load_from_files('./loading_files/genres_uri.txt', './lists_uri.txt', './loading_files/books_uri.txt')
    #     nom_liste = scraper.scrape_all_lists()
    #     print("Erreur, on recommence")
    #     with open('./lists_uri.txt', 'r') as f:
    #         lines = f.readlines()
    #     print(f"Reste : {len(lines)} lignes")
    #     if len(lines) == 0:
    #         break
    #     ind = 0
    #     for line in lines:
    #         if nom_liste in line:
    #             break
    #         ind += 1
    #     with open('./lists_uri.txt', 'w') as f:
    #         f.write(''.join(lines[ind:]))
    #     time.sleep(3)


    np.random.seed(0)
    with open('./loading_files/books_uri.txt', 'r') as f:
        lines = f.readlines()
    lines = np.array(lines)
    indices = np.random.permutation(len(lines))
    lines = lines[indices]
    with open('./books_to_scrape.txt', 'w') as f:
        f.write(''.join(lines))


    while True:
        scraper = Scraper.load_from_files('./loading_files/genres_uri.txt', './loading_files/lists_uri.txt', './books_to_scrape.txt')
        try:
            print("Scraping")
            scraper.scrape_n_books(500)
        except:
            print("Fin scraping (erreur)")
        finally:
            print("Sauvegarde des données")
            scraper.save_data('./goodreads_data.csv')

            with open('./scraped_books_uri.txt', 'r') as f:
                lines = f.readlines()
            last_scraped_book = lines[-1]

            ind = 0
            with open('./books_to_scrape.txt', 'r') as f:
                lines2 = f.readlines()
            
            for line in lines:
                if last_scraped_book == lines2:
                    break
                ind += 1

            with open('./books_to_scrape.txt', 'w') as f:
                f.write(''.join(lines2[ind+1:]))
        print("Pause de 3 secondes")
        time.sleep(3)