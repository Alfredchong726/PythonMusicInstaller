#!/usr/bin/env python3
from prettytable import PrettyTable
import requests
import parsel
from rich.progress import Progress # type: ignore

def search(keywords):
    infoList = []
    tb = PrettyTable()
    tb.field_names = ['ID', 'Song Name', 'Singer']
    baseUrl = 'https://www.gequbao.com/s/'
    response = requests.get(baseUrl + keywords)

    selector = parsel.Selector(response.text)
    songNames = [i.strip() for i in selector.css('.col-5.col-content a::text').getall()]
    songIDs = [i.strip().split('/')[-1] for i in selector.css('.col-5.col-content a::attr(href)').getall()]
    singers = [i.strip() for i in selector.css('.text-success.col-4.col-content::text').getall()]

    page = 0
    for songName, songID, singer in zip(songNames, songIDs, singers):
        tb.add_row([page, songName, singer])
        page += 1
        infoList.append({"SongName": songName, "SongID": songID, "Singer": singer})

    print(tb)

    songToInstall = input("输入要下载的歌曲序号: ")
    if 0 <= int(songToInstall) < len(infoList):
        getSongUrl(infoList[int(songToInstall)])
    else:
        print("输入序号不在范围内!")

def getSongUrl(songInfo):
    url = f"https://www.gequbao.com/api/play_url?id={songInfo["SongID"]}&json=1"
    response = requests.get(url)
    jsonInfo = response.json()
    songUrl = jsonInfo['data']['url']

    if songUrl:
        downloadSong(songUrl, songInfo['SongName'], songInfo['Singer'])
    else:
        print("获取歌曲 URL 失败!")
    
def downloadSong(songUrl, songName, singer):
    response = requests.get(songUrl, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    chunk_size = 1024
    with open(f"{songName}--{singer}.mp3", 'wb') as fs, Progress() as progress:
        task = progress.add_task(f"Downloading {songName}--{singer}.mp3", total=total_size)
        for data in response.iter_content(chunk_size=chunk_size):
            fs.write(data)
            progress.update(task, advance=len(data))

keyword = input("搜索关键字: ")
search(keyword)
