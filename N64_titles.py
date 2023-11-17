import requests
from bs4 import BeautifulSoup
import csv
# from tabulate import tabulate
import re

url = 'https://en.wikipedia.org/wiki/List_of_Nintendo_64_games'
csv_file_path = 'N64_games.csv'
headers = ['Title', 'Developer(s)', 'Publisher(s)', 'Year', 'Platform(s)', 'Genre(s)']
response = requests.get(url)

if response.status_code == 200:

    soup = BeautifulSoup(response.text, 'lxml')
    rows = soup.select('table.wikitable tr')
    skip_header = True
    data = []
    
    for row in rows:
        if skip_header:
            skip_header = False
            continue    # Skip the header row

        columns = row.find_all('td')
        if len(columns) == 7:
            na_status = columns[5].get_text(strip=True)  # 'North America' column (index 5)

            if 'Unreleased' not in na_status:
                title_element = columns[0].find('a')    # Extract the hyperlink text from the 'Title' column (index 0) find() is the FIRST OCCURENCE


                # TITLE 📚
                if title_element:
                    sup_elements = columns[0].find_all('sup')
                    title = None
                    
                    for sup_element in sup_elements:
                        if 'NA' in sup_element.text.upper():
                            previous_sibling = sup_element.find_previous_sibling()
                            if previous_sibling:
                                title = previous_sibling.get_text(strip=True)
                                # break  # Stop looping once 'NA' is found
                    if not title:
                        # title = title_element.get_text(strip=True) 
                        title = columns[0].find('i').get_text(strip=True)   #NEEDED MAGA


                    # PLATFORM --> from the individual Wikipedia page 🎮
                    title_link = title_element['href']
                    title_url = f'https://en.wikipedia.org{title_link}'
                    title_response = requests.get(title_url)
                    title_soup = BeautifulSoup(title_response.text, 'lxml')
                    platform_element = title_soup.find('th', string='Platform(s)')
                    if platform_element:
                        for sup in platform_element.next_sibling.find_all('sup'):       #GOATED
                            sup.extract()
                            # print(sup)
                        platform_items = platform_element.find_next('td').find_all('a')
                        if platform_items:
                            platform = ', '.join([item.get_text(strip=True) for item in platform_items])
                        else:
                            platform_items = platform_element.find_next('td').find_all(string=True)
                            platform = ', '.join([item.get_text(strip=True) for item in platform_items])
                            # platform = 'Super Nintendo Entertainment System'
                    else:   #needed for Wii case
                        platform = 'Nintendo 64'
                        # platform = 'YAX PLAT'


                    # GENRE --> from the individual Wikipedia page 🔫
                    for br in title_soup.find_all('br'):
                        next_s = br.nextSibling
                        if next_s and (next_s.string is None or next_s.string.strip() in (',', '')):
                            next_s.extract()
                        prev_s = br.previousSibling
                        if prev_s and (prev_s.string is None or prev_s.string.strip() in (',', '')):
                            prev_s.extract()
                    genre_element = title_soup.find('th', string='Genre(s)')
                    if genre_element:
                        for sup in genre_element.next_sibling.find_all('sup'):       #GOATED
                            sup.extract()
                            # print(sup)    #use to check output (printing in console)
                        for br in genre_element.next_sibling.find_all('br'):
                            br.replace_with(', ')
                        #CLEANUP for bad nested <ul><li> Samurai Jack: The Shadow of Aku GCN
                        first_ul = genre_element.next_sibling.find('ul')
                        if first_ul:
                            inner_ul = first_ul.find('ul')
                            if inner_ul:
                                first_ul.replace_with(inner_ul.extract())
                        ul_elements = genre_element.next_sibling.find_all('ul')
                        if ul_elements:
                            # Create a list to store the text of each <li> element
                            li_text = []
                            # Loop through <ul> elements and add the text of each <li> element to the list
                            li_elements = genre_element.next_sibling.find_all('li')
                            for li in li_elements:
                                li_text.append(li.get_text(strip=False)) # ‼️⚠️‼️⚠️‼️⚠️‼️⚠️ for <li> ELEMENTS OK to use FALSE
                            genre = ', '.join(li_text)
                        else:   
                            # genre_data = genre_element.find_next('td').get_text(strip=True) #false to leave spaces between commas.. ⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛⚠️🐛
                            # genre_data = genre_element.find_next('td').get_text(strip=True).replace(',', ', ')
                            # genre_data = genre_data.replace('(', ' (')
                            # genre = genre_data  # Use genre data as is
                            # genre = ', '.join([part.strip() for part in genre_element.find_next('td').get_text().split(',')]) #commas fix
                            genre = ', '.join([re.sub(r'\s+', ' ', part.strip()) for part in genre_element.find_next('td').get_text().split(',')])  #parentheses final fix
                    else:
                        genre = 'N/A'
                        # genre = 'YAX GEN'

                #  THERE IS NO <a> element in TITLE
                else:
                    sup_elements = columns[0].find_all('sup')
                    # title = columns[0].get_text(strip=True)     #works vs below ON WII U ONLY since a game is missing <i>
                    title = columns[0].find('i')   #actually needed for SNES
                    platform = 'Nintendo 64'     #actually needed for NES
                    genre = 'N/A'   #actually needed for NES
                    if title is not None:
                        title = title.get_text(strip=True)  #actually printing the 'i' above
                    else:
                        title = ("YOooooooo")       #0
                    for sup_element in sup_elements:  #NEEDED
                        if 'NA' in sup_element.text.upper():
                            try:
                                title = sup_element.previous_sibling.strip()
                            except TypeError:   #for N64 case
                                previous_sibling = sup_element.find_previous_sibling()
                                title = previous_sibling.get_text(strip=True)

                   
                # DEVELOPER 👨‍💻
                developer_elements = columns[1].find('div', class_='hlist')
                if developer_elements:
                    developer_items = developer_elements.find_all('li')
                    developer = ', '.join([developer.get_text(strip=True) for developer in developer_items])
                else:
                    developer = columns[1].get_text(strip=True)


                # PUBLISHER ✍️
                sup_elements = columns[2].find_all('sup')
                for sup in sup_elements:    # Before looping through sup_elements, remove any HTML tags inside each <sup> element
                    for tag in sup.find_all():
                        tag.extract()
                sup = columns[2].find('sup', string=re.compile(r'NA', re.IGNORECASE))   # "Publisher(s)" column (index 2)
                if sup:
                    previous_sibling = sup.find_previous_sibling()
                    if previous_sibling and previous_sibling.name == 'a':
                        publisher = previous_sibling.get_text()
                    else:
                        publisher = sup.find_previous_sibling(string=True)
                    if publisher:
                        publisher = (publisher.strip())
                    else:
                        print('N/A')
                else:
                    sup = columns[2].find('sup')  
                    if sup and sup.text.strip():  # Check if <sup> contains any text
                        a_element = columns[2].find('a')
                        publisher = (a_element.text)
                    else:
                        publisher_elements = columns[2].find_all('a')
                        if publisher_elements:
                            publisher_items = [publisher.get_text().strip() for publisher in publisher_elements]
                            publisher = ', '.join(publisher_items)
                        else:
                            publisher = columns[2].get_text(strip=True)


                # YEAR 📆
                first_released = columns[5].get_text(strip=True)  # "First Released" column (index 3)
                year = first_released[-4:]   # Extract the first 4 characters from the "First Released" column (representing the year)


                data.append([title, developer, publisher, year, platform, genre])


    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)  # Write the header row
        writer.writerows(data)    # Write the data rows

    print(f"Data has been saved to '{csv_file_path}'.")

    # Print the data in a table in the console
    # print(tabulate(data, headers, tablefmt="pretty"))

else:
    print("Failed to retrieve the web page.")