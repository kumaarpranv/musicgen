import requests
from bs4 import BeautifulSoup
import os
from os import path
from tqdm import tqdm
import sys

genre=input('genre? ')

ct = 1

if not path.exists('./data/' + genre+'/'):
    os.makedirs('./data/' + genre +'/')

genresize = sum([sum(map(lambda fname: os.path.getsize(os.path.join(directory, fname)), files)) for directory, folders, files in os.walk('./data/' + genre +'/')])
size = 1e8

filelist = os.listdir('./data/' + genre + '/')
filelist = [x.split('.mid')[0] for x in filelist]

with tqdm(total=100, position = 0,desc = 'genre download') as pbar: 
    while genresize < size:  # 200 mb approx
        update = 0.01
        
        url = 'https://www.midiworld.com/search/'+str(ct)+'/?q='+genre 
            
        try:
            murl=requests.get(url)
            soup = BeautifulSoup(murl.content,'html5lib')
            links = soup.findAll('a',{'target':'_blank'})

            links = list(set(links)-set(filelist))
            if links == []:
                break
            
            for i in links:
                lk = i['href']
                r = requests.get(lk, allow_redirects=True)
                fl = lk.split('/')[-1] + '.mid'
                if not path.exists('./data/'+genre+'/'+fl):
                    with open('./data/'+genre+'/'+fl, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)
                        
                    filesize=r.headers.get('content-length',None)

                    genresize += int(filesize)
                    
                    if genresize >= size*update and update < 1:
                        update += 0.01
                        pbar.update(1)
            ct+=1
            
        except Exception as e:
                print(e)             
