from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains  import ActionChains
# import pandas as pd

from browser_config import create_browser
from config import Config
from functions import *


profile_url, new_file, file_name = prompt_user_profile_details()
driver = create_browser(Config.chromedriver_path)
max_no = prompt_like_maximum()
driver = login(driver)
if driver.current_url != 'https://www.linkedin.com/feed/':
    prompt_user_verification()


url = profile_url + '/recent-activity/all/'

driver.execute_script("window.open('');")   # Open a new tab

# Switch to the new tab
driver.switch_to.window(driver.window_handles[1])

driver.get(url)
time.sleep(5)
driver.execute_script("window.scrollTo(0, 4000);")  


user_profile_info = {}
time.sleep(3)


while True:
    try:
        user_profile_info['name'] = driver.find_element(By.CSS_SELECTOR, 'h3.single-line-truncate.t-16.t-black.t-bold.mt2').get_attribute('innerText')
        break
    except:
        time.sleep(3)
        pass
user_profile_info['ProfileID'] = profile_url.split('-')[-1]


time.sleep(7)



posts, driver = find_posts(driver)



j = 0
list_users_like = {}
list_users_comments = {}
total_no_likes = 0
total_no_comments = 0
for post in posts:
    if j==10:  # chnage to 10
        break
    try:
        print(f'Getting post {j}', end='\n\n')
        number_likes, comment_number = get_likes_comments(post)
        total_no_likes += int(number_likes)
        total_no_comments += int(comment_number)
        print(f'Getting users from post likes. Found {number_likes} likes.')
        users = get_users_likes(post, number_likes, max_no, driver)
       
        # users = get_users_likes(post, number_likes, driver)
        for user, profile_url in users:
            user_name = user
            inp = {user_name: {'count': 0, 'profile_url': ''}}
            if user_name in list_users_like:
                # print(user_name)
                list_users_like[user_name]['count'] += 1
            else:
                # print(user_name, 'new')

                inp[user_name]['count'] = 1
                inp[user_name]['profile_url'] = profile_url
                list_users_like.update(inp)
        j += 1
        print(j, number_likes, comment_number)
        print(f'Getting users from post  comments')
        users = get_users_comment(post, comment_number, driver)
        print('All users successfully gotten from comments')
        if len(users) == 0:
            continue
        for user, profile_url in users:
            user_name = user
            inp = {user_name: {'count': 0, 'profile_url': ''}}
            if user_name in list_users_comments:
                list_users_comments[user_name]['count'] += 1
            else:
                inp[user_name]['count'] = 1
                inp[user_name]['profile_url'] = profile_url
                list_users_comments.update(inp)
        print(f'User retrievals from post {j} completed')
    except Exception as e:
        print('Failed to get users from current post. Moving on...')
        time.sleep(2)
        pass


if len(list_users_like) > 0 or len(list_users_comments) > 0:
    print('\n\n')
    print('All posts successfully processed. Moving on to data analysis...')
    users, user_stats = assign_points(list_users_comments, list_users_like)
    # print(users, user_stats)

    if len(users) > 0:
        users = dict(sorted(users.items(), key=lambda item: item[1], reverse=True))


    print('Sorting data...')


    # user_counts = data_analysis(list_users)[:20]


    user_profile_info['total_no_likes'] = total_no_likes
    user_profile_info['total_no_comments'] = total_no_comments

    if new_file == 'yes':
        save_to_new_file(file_name, users, user_stats, user_profile_info, url)  
    else:
        save_to_existing_file(file_name, users, user_stats, user_profile_info, url)
    time.sleep(10)
driver.quit()
