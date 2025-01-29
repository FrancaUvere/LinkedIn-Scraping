from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains  import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import csv

from config import Config


def login(driver):
    """login to linkedin"""
    print('Logging into your account...Please wait')
    driver.get('https://www.linkedin.com/login')
    wait(driver, 10)
    email = driver.find_element(By.ID, 'username')
    email.send_keys(Config.ACCOUNT_EMAIL)
    time.sleep(2)
    password = driver.find_element(By.ID, 'password')
    password.send_keys(Config.ACCOUNT_PASSWORD)
    time.sleep(2)
    password.submit()
    time.sleep(10)
    return driver



def wait(browser, timeout=10):
    """Wait for the page to load"""
    try:
        WebDriverWait(browser, timeout).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
    except Exception as e:
        print('Timeout: There is an erro in your connection. Please, check your internet connection')
        exit(0)

def prompt_user_verification():
    """Prompt user to complete LinkedIn verification on the browser"""
    print('Please, complete the LinkedIn verification on the Browser')
    input_bool = input('Type "y" after verification is complete: ')
    if input_bool.lower() != 'y':
        print('Verifivation incomplete. Please restart the program. \n End program')
        exit(-1)
    time.sleep(2)


def prompt_user_profile_details():
    """Prompt user to enter LinkedIn profile details"""
    profile_url = input('Enter the LinkedIn profile URL: ')
    if profile_url.endswith('/'):
        profile_url = profile_url[:-1]
    new_file = input('Create new file (yes/no(input no to append to old file created)): ')
    file_name = input('Enter the file name to store data: ')
    return profile_url, new_file, file_name


def prompt_like_maximum():
    """Prompt user to enter the maximum number of likes to scrape"""
    res = 'no' or input('Do you want to scrape all likes? (yes/no): ')
    if res.lower() == 'yes':
        return -1
    number = 20 or int(input('Enter the maximum number of likes to scrape: '))
    print(f'The program will srape {number} <= likes <= {number+20}')
    return number


def find_posts(driver):
    """Find all posts on the LinkedIn profile"""
    time.sleep(10)
    posts_box = driver.find_element(By.CSS_SELECTOR, 'ul.display-flex.flex-wrap.list-style-none.justify-center')

    time.sleep(2)

    # Get the number of posts on the page
    driver.execute_script("window.scrollTo(0, 4000);")
    scroll_to_bottom(driver, posts_box)

    post_boxes = posts_box.find_elements(By.TAG_NAME, 'li')
    class_name = post_boxes[0].get_attribute('class')
    print(f'Found {len(post_boxes)} posts, with class name {class_name}')
    
    # Get first 10 posts and their URNs
    # posts = post_boxes[:10]
    # print(posts)
    # print('Getting the first 10 posts')
  


    return class_name, driver



def scroll_to_bottom(driver, scroll_box):
    """Scroll to the bottom of the page"""
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)


def get_likes_comments(post, driver):
    """Get the total number of likes and comments on a post"""
    print('About getting likes and comments')
    try:
        # Attempt to find likes using the first selector
        # likes = post.find_element(By.CSS_SELECTOR, 'span.social-details-social-counts__social-proof-fallback-number') \
        #             .get_attribute('innerText').replace(',', '')
        likes = post.find_element(By.CSS_SELECTOR, ' span[data-social-proof-fallback]') \
                    .get_attribute('innerText').replace(',', '')
        print('Likes: ', likes)
        likes = int(likes)
    except Exception as e1:
        try:
            # Fallback to the second selector if the first fails
            likes = post.find_element(By.CSS_SELECTOR, 'span.social-details-social-counts__reactions-count') \
                        .get_attribute('innerText').replace(',', '')
            print('No likes found using the first selector:')
            print('Likes: ', likes)
            likes = int(likes)
        except Exception as e2:
            # If both selectors fail, set likes to 0
            print('No likes found using either selector:')
            likes = 0
            print('Likes: ', likes)

    time.sleep(3)

    try:
        comment_link = post.find_element(By.CSS_SELECTOR, 'button.t-black--light.social-details-social-counts__count-value.social-details-social-counts__count-value-hover.text-body-small.hoverable-link-text.social-details-social-counts__btn')
        actions = ActionChains(driver)

        # Move to the element and click
        actions.move_to_element(comment_link).click().perform()
        time.sleep(1)
        comments = post.find_element(By.CSS_SELECTOR, 'button.t-black--light.social-details-social-counts__count-value.social-details-social-counts__count-value-hover.text-body-small.hoverable-link-text.social-details-social-counts__btn span').get_attribute('innerText').split(' ')[0]
        comments = int(comments)
        print('Comments: ', comments)
    except Exception as e:
        print('No comment link found')
        comments = 0
    
    return likes, comments


def check_profile_url(profile_url, driver):
    """Check the profile URL"""
    print('checking profile url')
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[2])
    driver.get(profile_url)
    wait(driver, 10)
    profile_url = driver.current_url
    time.sleep(1)
    driver.close()
    driver.switch_to.window(driver.window_handles[1])
    return profile_url

def get_users_likes(post, number, max_no, driver):
    """Get the users who liked or commented on a post"""
    users = []
    try:
        driver.execute_script("arguments[0].scrollIntoView();", post)
        time.sleep(5)

        like_box_link = post.find_element(By.CSS_SELECTOR, 'button.t-black--light.display-flex.align-items-center.social-details-social-counts__count-value.social-details-social-counts__count-value-hover.text-body-small.hoverable-link-text')
        # like_box_link = post.find_element(By.CSS_SELECTOR, 'span.social-details-social-counts__reactions-count')
        time.sleep(1)

        # Initialize ActionChains
        actions = ActionChains(driver)

        # Move to the element and click
        actions.move_to_element(like_box_link).click().perform()
        print("Like link clicked successfully")
        time.sleep(5)
        outer_box = driver.find_element(By.CSS_SELECTOR, 'div.artdeco-modal.artdeco-modal--layer-default.social-details-reactors-modal')
        likes_box = driver.find_element(By.CSS_SELECTOR, 'div.artdeco-modal__content.social-details-reactors-modal__content.ember-view')
        like_box = outer_box.find_element(By.CSS_SELECTOR, 'div.social-details-reactors-tab-body')
        # post_box = driver.find_element(By.CSS_SELECTOR, 'div.social-details-reactors-modal')
        new_len = 0
        
        if max_no != -1 and max_no < number:
            number = max_no
        print("Current number of items: 0, ", end='')
        while new_len < number:
                # Scroll to the bottom of the scroll box
                # driver.execute_script("arguments[0].scrollTop += 3000;", comment_box)

                # Wait for new items to load
                time.sleep(2)

                # Get the current number of items after scrolling
            
                likes = like_box.find_elements(By.CSS_SELECTOR, 'li.social-details-reactors-tab-body-list-item.artdeco-list__item')

                driver.execute_script("arguments[0].scrollIntoView();", likes[-1])
                
                print(f"{len(likes)}/{number}", end=', ')

                # Break the loop if no new items are loaded
                if len(likes) == number:
                    break

                if len(likes) == new_len and len(likes) >= number - 20:
                    break

                if len(likes) >= number:    
                    break

                new_len = len(likes)

                # click the load more button and add a conditional for if it is not present
                try:
                    load_more_button = likes_box.find_element(By.CSS_SELECTOR, 'button.artdeco-button.artdeco-button--muted.artdeco-button--1.artdeco-button--full.artdeco-button--secondary.ember-view.scaffold-finite-scroll__load-button')
                    actions.move_to_element(load_more_button).click().perform()
                except Exception as e:
                    print('No load more button found')
                    break

        print('\n')
        print('Getting Users from Likes...This may take a moment')
        for i, like in enumerate(likes):
            try:
                time.sleep(1)
                user = like.find_element(By.CSS_SELECTOR, 'span.text-view-model').get_attribute('innerText')
                profile_url = like.find_element(By.CSS_SELECTOR, 'a.link-without-hover-state.ember-view').get_attribute('href')
                # profile_url = check_profile_url(profile_url, driver)
                users.append([user, profile_url])
            except Exception as e:
                print(f'Error:  User name could not be retrieved for like{i}')
                continue
        time.sleep(1)
        print('Users retrieved successfully from Likes')
        close = outer_box.find_element(By.CSS_SELECTOR, 'button.artdeco-modal__dismiss')
        actions.move_to_element(close).click().perform()
        time.sleep(2)
        driver.execute_script("arguments[0].scrollIntoView();", post)

        #
        return users
    except Exception as e: 
        print('Error occurred in getting users from likes', e)
        time.sleep(10)
        return []


def get_users_comment(post, number, driver):
    """Get the users who commented on a post"""
    try:
        comment_box_link = post.find_element(By.CSS_SELECTOR, 'button.t-black--light.social-details-social-counts__count-value.social-details-social-counts__count-value-hover.text-body-small.hoverable-link-text.social-details-social-counts__btn')
    except Exception as e:
        print('No comment found')
        return []
    time.sleep(1)

    # Initialize ActionChains
    actions = ActionChains(driver)

    # Move to the element and click
    try:
        actions.move_to_element(comment_box_link).click().perform()
    except:
        print('Comment box not accessible')
        return []
    time.sleep(2)

    try:
        button_more = post.find_element(By.CSS_SELECTOR, 'div.comments-comments-list.comments-comments-list--cr button.comments-comments-list__load-more-comments-button--cr')
        print("More comment button found")
    except Exception as e:
        print('More comment button not found')
    
    load_more_comment = True
   
    users = []
    try:
        # Try loading all comments
        time.sleep(2)
        try:
            while load_more_comment:
                button_more = post.find_element(By.CSS_SELECTOR, 'div.comments-comments-list.comments-comments-list--cr button.comments-comments-list__load-more-comments-button--cr')
                driver.execute_script("arguments[0].scrollIntoView();", button_more)
                driver.execute_script("arguments[0].click();", button_more)
                print('Button clicked')
        except Exception as e:
            print('No more comments to load or error occurred:')

        # Get all comment articles
        comment_cont = post.find_element(By.CSS_SELECTOR, 'div.comments-comment-list__container')
        comment_boxes = comment_cont.find_elements(By.CSS_SELECTOR, 'article.comments-comment-entity')
        print(f"Found {len(comment_boxes)} comments")
        
        
        for comment in comment_boxes:
            try:
                # Get username from the description title span
                user = comment.find_element(
                    By.CSS_SELECTOR, 
                    'div.comments-comment-meta__container span.comments-comment-meta__description-title'
                ).get_attribute('innerText').strip()
                
                # Get profile URL from the link
                profile_url = comment.find_element(
                    By.CSS_SELECTOR, 
                    'div.comments-comment-meta__container a.comments-comment-meta__image-link'
                ).get_attribute('href')
                
                users.append([user, profile_url])
                driver.execute_script("arguments[0].scrollIntoView();", comment)
                
            except Exception as e:
                print('Error retrieving user info from comment:', e)
                continue

        print('Comment users:', users)
        return users

    except Exception as outer_error:
        print('An error occurred during comment processing:')
        return users


def data_analysis(list_users):
    """Analyse the data"""
        
    data = []

    # Populate the list with (id, user) pairs
    for entry in list_users:
        for user in entry['users']:
            data.append((entry['id'], user))

    # Convert the list to a DataFrame
    df = pd.DataFrame(data, columns=['id', 'user'])

    # Count the occurrences of each user
    user_counts = df['user'].value_counts().reset_index()
    user_counts.columns = ['user', 'count']

    # Sort users by the count in descending order
    user_counts = user_counts.sort_values(by='count', ascending=False)

    return user_counts
   

def save_to_new_file(file_name, user_counts, user_stats, user_profile_info, url):
    """Save the data to a new file"""
    with open(f'{file_name}.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['User', 'TotalCount', 'NumberofLikes', 'NumberofComments', 'ProfileURL'])
        for user, count in user_counts.items():
            try:
                writer.writerow([user, count, user_stats[user]['no_likes'], user_stats[user]['no_comments'], user_stats[user]['profile_url']])
            except Exception as e:
                print(e)
                continue
    with open(f'{file_name}.txt', 'w', encoding='utf-8') as f:
        f.write(str(f'ProfileURL: {url} \n'))
        f.write(str(f'ProfileName: {user_profile_info["name"]} \n'))
        f.write(str(f'ProfileID: {user_profile_info["ProfileID"]} \n'))
        f.write(str(f'TotalLikes: {user_profile_info["total_no_likes"]} \n'))
        f.write(str(f'TotalComments: {user_profile_info["total_no_comments"]} \n'))
        f.write(str(f'Most engaged users:  \n'))
        if len(user_counts) > 20:
            items = list(user_counts.items())
            # Create a new dictionary from the sliced list of items
            user_counts = dict(items[:20])
        for user, count in user_counts.items():
            try:
                f.write(f"{user} : (count: {count} profile_url: {user_stats[user]['profile_url']})\n")
                f.write(f"(number_of_likes: {user_stats[user]['no_likes']}, number_of_comments: {user_stats[user]['no_comments']})\n")
            except:
                continue
        print(f'Data saved successfully to {file_name}.csv')


def save_to_existing_file(file_name, user_counts, user_stats, user_profile_info, url):
    """Save the data to a new file"""
    with open(f'{file_name}.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['User', 'TotalCount', 'NumberofLikes', 'NumberofComments', 'ProfileURL'])
        for user, count in user_counts.items():
            try:
                writer.writerow([user, count, user_stats[user]['no_likes'], user_stats[user]['no_comments'], user_stats[user]['profile_url']])
            except Exception as e:
                continue
    with open(f'{file_name}.txt', 'a', encoding='utf-8') as f:
        f.write(str(f'ProfileURL: {url} \n'))
        f.write(str(f'ProfileName: {user_profile_info["name"]} \n'))
        f.write(str(f'ProfileID: {user_profile_info["ProfileID"]} \n'))
        f.write(str(f'TotalLikes: {user_profile_info["total_no_likes"]} \n'))
        f.write(str(f'TotalComments: {user_profile_info["total_no_comments"]} \n'))
        f.write(str(f'Most engaged users:  \n'))
        if len(users) > 20:
            items = list(users.items())

            # Create a new dictionary from the sliced list of items
            users = dict(items[:20])
        else:
            users = users
        for user, count in user_counts.items():
            f.write(f"{user} : (count: {count} profile_url: {user_stats[user]['profile_url']})\n")

            f.write(f"(number_of_likes: {user_stats[user]['no_likes']}, number_of_comments: {user_stats[user]['no_comments']})\n")

        print(f'Data saved successfully to {file_name}.csv')



def assign_points(users_comments, users_likes):
    """Assign points to comments and likes"""
    users = {}
    users_stats = {}
    for user, info in users_comments.items():
        users[user] = (2 *int(info['count']))
        users_stats[user] = {
                'no_comments': int(info['count']),
                'no_likes': 0,
                'total_points': int(info['count']),
                'profile_url': info['profile_url']
            }

    
    for user, info in users_likes.items():
        if user in users:
            users[user] += int(info['count'])
            users_stats[user]['no_likes'] += int(info['count'])
            users_stats[user]['total_points'] = users[user]
        else:
          # Initialize or update the dictionary with the new user key and corresponding values
            users[user] = int(info['count'])
            users_stats[user] = {
                'no_comments': 0,
                'no_likes': int(info['count']),
                'total_points': int(info['count']),
                'profile_url': info['profile_url']
            }

   
    
    return users, users_stats


def sort_users(users):
    """Sort the users by the total points"""
    sorted_users = sorted(users.items(), key=lambda x: x[1], reverse=True)
    return sorted_users


if __name__ == '__main__':
    pass
