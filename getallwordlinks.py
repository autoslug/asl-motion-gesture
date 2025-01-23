import requests, argparse, bs4
from tqdm import tqdm

API_URL: str = "https://www.handspeak.com/word/asl-eng/asleng-data.php"
HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://www.handspeak.com/word/asl-eng/",
    "Origin": "https://www.handspeak.com",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Priority": "u=4",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
}
PAYLOAD: dict = {
    "page": "1",
    "fig": "",
    "mov": "",
    "loc": "",
    "both": ""
}
LAST_PAGE: int = 549

links = []

def extractWords() -> None:
    for page in tqdm(range(1, LAST_PAGE + 1), desc="Extracting pages"):
        PAYLOAD["page"] = str(page)
        response: requests.Response = requests.post(API_URL, headers=HEADERS, data=PAYLOAD)
        if response.status_code != 200:
            tqdm.write(f"Error fetching page {page}")
            continue
        
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.content, 'lxml')
        wordList = soup.find('body').find('ul', class_='col-abc').find_all('li')
        for word in wordList:
            link = word.find('a').get('href')
            links.append(link)
    
    with open('allWordLinks.txt', 'w') as file:
        for l in links:
            file.write(l + '\n')


if __name__ == "__main__":
    parser : argparse.ArgumentParser = argparse.ArgumentParser(description="stuff")
    parser.add_argument('-e', "--extract", action='store_true', help="Extract all word links on Handspeak")
    args : argparse.ArgumentParser = parser.parse_args()

    if args.extract:
        extractWords()
