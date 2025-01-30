import requests, argparse, bs4, json
from tqdm import tqdm
from collections import defaultdict

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

links: dict[str, str] = {}

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
            word_text = word.find('a').text.strip()
            link = word.find('a').get('href')

            # sometimes multiple words link to the same article, eg "close, close-by, close to"
            # split by ", " and make multiple things
            words: list[str] = word_text.split(", ")
            for w in words:
                links[w] = link
    
    with open('allWordLinks2.json', 'w') as file:
        json.dump(links, file, indent=4)

def extractVideosFromArticle(word: str, url: str) -> list[str]:
    response: requests.Response = requests.get("https://www.handspeak.com" + url, headers=HEADERS)
    if response.status_code != 200:
        tqdm.write(f"Error fetching page for {word}, code {response.status_code}")
        tqdm.write(response.text)
        return []
    
    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.content, 'lxml')
    videos = soup.find_all('video', class_='v-asl')
    return [video.get('src') for video in videos]


if __name__ == "__main__":
    parser : argparse.ArgumentParser = argparse.ArgumentParser(description="stuff")
    parser.add_argument('-e', "--extract",    action='store_true', help="Extract all word links on Handspeak")
    parser.add_argument('-v', "--get-videos", action='store_true', help="Extract videos from all links")
    args : argparse.ArgumentParser = parser.parse_args()

    if args.extract:
        extractWords()
    
    if args.get_videos:
        with open('allWordLinks2.json', 'r') as file:
            lookup: dict[str, str] = json.load(file)

        with open('WLASL/start_kit/WLASL_v0.3.json', 'r') as file:
            starterData: dict[str, str] = json.load(file)
        
        updatedURLs: defaultdict[str, list] = defaultdict(list)
        
        # loop through the WLASL json, and find all words with handspeak.com links
        for gloss in tqdm(starterData, desc='Extracting videos'):
            word: str = gloss["gloss"]

            for instance in gloss["instances"]:
                if instance["source"] != "handspeak": continue

                # found a word with handspeak.com link. find its updated URL.
                if word not in lookup: continue 
                
                updatedURLs[word] = extractVideosFromArticle(word, lookup[word])

        with open('updatedURLs.json', 'w') as file:
            json.dump(dict(updatedURLs), file, indent=4)
                




