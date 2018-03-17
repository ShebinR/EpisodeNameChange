from lxml import html
import requests

data = ""
page = requests.get('https://en.wikipedia.org/wiki/The_Big_Bang_Theory_(season_8)')
#print page.content
tree = html.fromstring(page.content)

table = tree.xpath("//table[@class='wikitable sortable']//*")

#table_contents = dict(table.attrib)
episode_number = []
episode_name = []
count = 0
for element in table:
   # print element
    if element.tag != 'td':
        continue
    if count % 9 == 0:
        episode_number.append(element.text_content())
    if count % 9 == 1:
        epi_name = element.text_content()
        epi_name = epi_name.replace('"', '')
        episode_name.append(epi_name)
    count = count + 1

#print episode_number
#print episode_name

print episode_number
for index in range(len(episode_number)):
    #print index
    data = data + episode_number[index]
    data = data + " " + episode_name[index] + "\n"
#data = tree.xpath('//*[@id="mw-content-text"]/div/table[]/text()')
print data
#

f = open('list_of_episodes_Season_8.txt', 'w')
f.write(data)
f.close()
