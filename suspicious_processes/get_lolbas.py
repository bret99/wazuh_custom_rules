import requests
from bs4 import BeautifulSoup
import os

url = 'https://lolbas-project.github.io'
response=requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')

bin_names = soup.find_all(class_='bin-name')

bin_names_text = [bin.get_text().strip() for bin in bin_names]

with open('lolbas.txt', 'w', encoding='utf-8') as file:
    for name in bin_names_text:
        file.write(name + '\n')

os.system("cat lolbas.txt > /usr/local/bin/processes.txt")
os.system("cat gtfobins.txt >> /usr/local/bin/processes.txt")
os.system("rm -f /usr/local/bin/lolbas.txt")
