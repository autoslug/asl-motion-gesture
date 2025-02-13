import sys, json

# usage: python3 filter.py [original big file with everything] [failed download json]
if __name__ == "__main__":
    # open the files
    originalFile    = open(sys.argv[1])
    failedDownloads = open(sys.argv[2])

    # load all failed URLs to a list
    downloads: list = json.load(failedDownloads)
    missingLabels: list[int] = []
    for failure in downloads:
        missingLabels.append(failure["url"])
    
    # iterate through original big file 
    # if the entry's url is in the failed set, skip it. otherwise append to new file
    allDownloads: list = json.load(originalFile)
    missingLabels = set(missingLabels)
    updatedFile = []
    for download in allDownloads:
        if download["url"] in missingLabels: continue

        updatedFile.append(download)
    
    # write to file
    with open(sys.argv[1] + "UPDATED.json", "w") as file:
        json.dump(updatedFile, file)
        print(f'New file: {len(updatedFile)}, failed: {len(downloads)}, og: {len(allDownloads)}')



