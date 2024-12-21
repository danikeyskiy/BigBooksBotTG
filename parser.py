import requests
from bs4 import BeautifulSoup

from app.database.models import Book

def parse_text(soup, class_name, start_marker, end_marker):
    element = soup.find('div', class_=class_name)
    if not element:
        return ''
    
    content = element.decode_contents() if hasattr(element, 'decode_contents') else ''
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        return ''
    
    start_idx += len(start_marker)
    end_idx = content.find(end_marker, start_idx)
    
    return content[start_idx:end_idx].strip()

def get_book(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    name = parse_text(soup, 'book_name', '<h1>', '<')
    description = parse_text(soup, 'b_biblio_book_annotation', '<p>', '</p>')
    year = parse_text(soup, 'row year_public', '"row_content">', '<')
    author = parse_text(soup, 'row author', '"author">', '<')

    genre_element = soup.find('div', class_='row genre')
    genre = ''
    if genre_element:
        genre_links = genre_element.find_all('a')
        genre = ', '.join(link.text.strip() for link in genre_links)

    download_links = soup.find('div', class_='b_download').find_all('span', class_='link')
    download_link = None
    for link in download_links:
        onclick_attr = link.get('onclick', '')
        if 'fb2.zip' in onclick_attr:
            download_link = "https://flibusta.su" + onclick_attr.split("'")[1]
            break

    if name and download_link:
        book, created = Book.get_or_create(
            name=name,
            defaults={
                'description': description,
                'author': author,
                'year': year,
                'genre': genre,
                'download_link': download_link
            }
        )
        
        if not created:
            print(f"Книга '{name}' уже существует в базе данных.")
        else:
            print(f"Книга '{name}' добавлена в базу данных.")

    return book

def get_books_from_page(page: int):
    url = f'https://flibusta.su/book/?page={page}/'
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")
    book_elements = soup.find_all('div', class_='book_name')
    books = []

    for book_element in book_elements:
        link_tag = book_element.find('a')
        if link_tag:
            book_url = f"https://flibusta.su{link_tag.get('href', '')}"
            book = get_book(book_url)
            if book:
                books.append(book)

    return books

def get_books_from_pages(count: int):
    all_books = []

    for page in range(1, count + 1):
        books_on_page = get_books_from_page(page)
        for book in books_on_page:
            all_books.append(book)

    print("\nAll books were collected")

    return all_books

if __name__ == "__main__":
    get_books_from_pages(50)