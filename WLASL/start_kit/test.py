import json

def getAllMissingLinks() -> None:
    with open("missing.txt", "r") as file:
        missingVideos: list[str] = [int(i.strip()) for i in file.readlines()]
        
    with open("WLASL_v0.3.json", "r") as file:
        data: dict = json.load(file)
        idToLink: dict[str, str] = {}
        
        # flatten dictionary into a list
        for gloss in data:
            listThing = gloss["instances"]
            for instance in listThing:
                idToLink[int(instance["video_id"].strip())] = instance["url"]
            
        # write all links to a text file
        missingLinks: list[str] = []
        for missingVideo in missingVideos:
            missingLinks.append(idToLink[missingVideo])
        
        # write to a file
        with open("missingLinks.txt", "w") as outputFile:
            for link in missingLinks:
                outputFile.write(link + "\n")
            
def getallsignbanklinks():
    with open("missingLinks.txt", "r") as file:
        missingLinks: list[str] = file.readlines()
        signBankLinks: set[str] = set()
        for link in missingLinks:
            if "aslsignbank" in link:
                signBankLinks.add(link)
        
        with open("signbank.txt", "w") as signbank:
            for l in list(signBankLinks):
                signbank.write(l)

if __name__ == "__main__":
    getAllMissingLinks()
    
    