import httpx
from bs4 import BeautifulSoup

url = 'https://www.houseoffraser.co.uk/men/hoodies-and-sweatshirts'

# websites will block you if you don't provide a user agent
# so we need to provide a user agent
# you can find your user agent by searching "my user agent" on google
# and copy the string that appears
# other headers may be needed as well, you will have to trial and error to see how to get the website to work
# you can find the headers by inspecting the website and looking at the network tab
# and looking at the headers that are sent when you load the website
# you can also find the headers by looking at the robots.txt file of the website

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"
}

def extract_product_data(product):
    try:
        name = product.find('span', class_='productdescriptionname').text
        brand = product.find('span', class_='productdescriptionbrand').text
        price = product.find('span', class_='CurrencySizeLarge curprice').text.strip()
        print(f'Brand: {brand}, Name: {name}, Price: {price}')
    except Exception as e:
        print(e)
    

def main():
    response = httpx.get(url, headers=headers)
    response_html = response.text

    soup = BeautifulSoup(response_html, 'html.parser')
    products = soup.find_all('div', class_='s-productthumbbox')
    for product in products:
        extract_product_data(product)

if __name__ == '__main__':
    main()