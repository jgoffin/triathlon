import csv
import classes
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
import os
import glob
import time
from multiprocessing import Pool


starting_url = "https://www.athlinks.com/search/events?category=events&filters=%7B%22dateRangeFilter%22%3A%7B%22enabled%22%3Atrue%2C%22value%22%3A%7B%22from%22%3A%222018-04-28%22%2C%22to%22%3A%222019-04-28%22%7D%7D%2C%22locationFilter%22%3A%7B%22enabled%22%3Afalse%2C%22value%22%3A%7B%22location%22%3A%22%22%2C%22range%22%3A50%7D%7D%2C%22typeFilter%22%3A%7B%22olympic%22%3Atrue%2C%22triathlon%22%3Atrue%7D%7D&term="
options = Options()
options.headless = True

def get_event_urls():
    driver = webdriver.Chrome()
    driver.get(starting_url)
    wait = WebDriverWait(driver, 10)

    filepath = '/Users/jacobgoffin/Documents/GitHub/triathlon/data/event_urls.csv'
    file = open(filepath, 'w')
    headers = ['id', 'url']
    writer = csv.DictWriter(f=file, fieldnames=headers)
    writer.writeheader()

    more_exists = True
    while more_exists:
        try:
            load_more_button = wait.until(EC.element_to_be_clickable((By.ID, 'load-more-link')))
            driver.execute_script("arguments[0].click();", load_more_button)
        #except NoSuchElementException, TimeoutException:
        except Exception as e: # Make more specfic
            print(Exception)
            more_exists = False

    results = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="results"]/a')))
    event_urls = [result.get_attribute('href') for result in results]

    for i, url in enumerate(event_urls):
        writer.writerow({'id': i, 'url': url})

    file.close()


def process_events():
    filepath = '/Users/jacobgoffin/Documents/GitHub/triathlon/data/event_urls.csv'
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f=f)
        # url_tuples = [(row['id'], row['url']) for row in reader()]
        for row in reader:
            result = view_all_racers(row['id'], row['url'])


def view_all_racers(event_id, event_url):
    success_status = 1

    filepath = f'/Users/jacobgoffin/Documents/GitHub/triathlon/data/racer_url_files/{event_id}_racers.csv'
    # If file has already been populated, skip
    if not os.path.exists(filepath) or os.stat(filepath).st_size == 0:
        with open(filepath, 'w') as f:
            headers = ['id', 'event_id', 'racer_url']
            writer = csv.DictWriter(f=f, fieldnames=headers)
            writer.writeheader()

            driver = webdriver.Chrome()
            driver.get(event_url)
            wait = WebDriverWait(driver, 10)

            try:
                course_names = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//*[@class='view-all-results']/../../div[1]")
                    )
                )
                if len(course_names):
                    # need i to keep track of which course/view-all-button we want to click into
                    for i, element in enumerate(course_names):
                        course_name = element.text.lower()
                        # Approximate way to check if course is an "olympic" distance triathlon, and not a relay
                        bike_check = any(val in course_name for val in ['40k', '40 k'])
                        relay_check = 'relay' not in course_name
                        if all([bike_check, relay_check]):
                            row_id = 0
                            # Loads first n (50) racers
                            view_all_button = wait.until(
                                                EC.presence_of_element_located(
                                                    (By.XPATH, f"(//*[@class='view-all-results'])[{i+1}]")
                                                )
                            )
                            driver.execute_script("arguments[0].click();", view_all_button)
                            row_id = get_racers(wait, writer, row_id, event_id)

                            page_buttons = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='pager']/div/div/button")))
                            page_values = [button_element.get_attribute("value") for button_element in page_buttons]
                            page_values = [int(val) for val in page_values]
                            min_page_value, max_page_value = min(page_values), max(page_values)

                            for page_value in range(min_page_value+1, max_page_value+1):  # +1 since we already parsed page 0
                                next_page_button = wait.until(
                                                        EC.element_to_be_clickable(
                                                            (By.XPATH, f"//*[@id='pager']/div/div/button[@value={page_value}]")
                                                        )
                                )
                                driver.execute_script("arguments[0].click();", next_page_button)
                                row_id = get_racers(wait, writer, row_id, event_id)

                            # if all code succeeds, exit? Only want to parse on course per event
                            break


            except Exception as e:
                print(e)
                success_status = 0

            finally:
                # Always gets to finally even if Exception occurs
                driver.quit()
                return success_status, event_id


def get_racers(wait, writer, row_id, event_id):
    racers = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//*[@class='athName athName-display']")
        )
    )
    for i, racer in enumerate(racers):
        racer_url = racer.get_attribute("href")
        writer.writerow({"id":row_id+i, "event_id":event_id, "racer_url":racer_url})
    return row_id+len(racers)


def process_racer_files():

    racer_filepaths = list(glob.iglob('./data/racer_url_files/*.csv'))
    #subset_filepaths = racer_filepaths[0:100]

    with Pool(3) as p:
        run_results = p.map(get_racer_data, racer_filepaths)


def get_racer_data(racer_urls_filepath):

    with open(racer_urls_filepath, 'r') as input_f:
        reader = csv.DictReader(f=input_f)
        racer_data_filename = os.path.basename(os.path.splitext(racer_urls_filepath)[0])+'_data.csv'
        racer_data_filepath = os.path.join('/Users/jacobgoffin/Documents/GitHub/triathlon/data/racer_data_files', racer_data_filename)

        if not os.path.exists(racer_data_filepath) or os.stat(racer_data_filepath).st_size == 0:
            with open(racer_data_filepath, 'w') as output_f:
                headers = ['id', 'event_id', 'racer_url', 'event_name', 'distance', 'weather', 'course_name',
                           'swim_time', 't1', 'bike_time', 't2', 'run_time', 'full_time', 'ageGender', 'location']
                writer = csv.DictWriter(f=output_f, fieldnames=headers)
                writer.writeheader()

                driver = webdriver.Chrome(options=options)
                wait = WebDriverWait(driver, 10)

                row_count = sum(1 for row in reader)
                input_f.seek(0)
                reader = csv.DictReader(f=input_f)
                rows_processed = 0

                for row in reader:
                    driver.get(row['racer_url'])

                    try:
                        event_name_element = wait.until(
                            EC.presence_of_element_located(
                                (By.ID, "event-name")
                            )
                        )
                        event_name = event_name_element.text
                    except Exception as e:
                        event_name = None
                    try:
                        ageGender_element = wait.until(
                            EC.presence_of_element_located(
                                (By.ID, "ageGender")
                            )
                        )
                        ageGender = ageGender_element.text
                    except Exception as e:
                        ageGender = None

                    try:
                        location_element = wait.until(
                            EC.presence_of_element_located(
                                (By.ID, "IRPUserLocation")
                            )
                        )
                        location = location_element.text
                    except Exception as e:
                        location = None

                    try:
                        distance_element = wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//*[contains(text(), 'Miles')]/..")
                            )
                        )
                        distance_string = distance_element.text
                        distance = float(re.search(r'[-+]?([0-9]*\.[0-9]+|[0-9]+)', distance_string).group())
                        # if you find one racer that's not olympic distance, means whole race is so quit
                        if distance < 31.0 or distance > 33.0:
                            return 0, racer_urls_filepath

                    except Exception as e:
                        distance = None
                    try:
                        weather_element = wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//*[contains(text(), 'Weather')]/..")
                            )
                        )
                        weather = weather_element.text
                    except Exception as e:
                        weather = None

                    try:
                        course_name_element = wait.until(
                            EC.presence_of_element_located(
                                (By.ID, "irp-race-name")
                            )
                        )
                        course_name = course_name_element.text
                    except Exception as e:
                        course_name = None

                    try:
                        swim_time_element = wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//*[text()='Swim']/../div[4]")
                            )
                        )
                        swim_time = swim_time_element.text
                    except Exception as e:
                        swim_time = None

                    try:
                        bike_time_element = wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//*[text()='Bike/Cycle']/../div[4]")
                            )
                        )
                        bike_time = bike_time_element.text
                    except Exception as e:
                        bike_time = None

                    try:
                        run_time_element = wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//*[text()='Run']/../div[4]")
                            )
                        )
                        run_time = run_time_element.text
                    except Exception as e:
                        run_time = None

                    try:
                        transition_time_elements = wait.until(
                            EC.presence_of_all_elements_located(
                                (By.XPATH, "//*[text()='Transition']/../div[4]")
                            )
                        )

                        for i, element in enumerate(transition_time_elements):
                            if i == 0:
                                transition1_time = element.text
                            else:
                                transition2_time = element.text

                    except Exception as e:
                        transition1_time, transition2_time = None, None

                    try:
                        full_time_element = wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//*[text()='Full Course']/../div[4]")
                            )
                        )
                        full_time = full_time_element.text
                    except Exception as e:
                        full_time = None

                    writer.writerow({'id':row['id'], 'event_id':row['event_id'], 'racer_url':row['racer_url'] ,
                                      'event_name':event_name, 'distance':distance, 'weather':weather, 'course_name':course_name,
                                      'swim_time':swim_time, 't1':transition1_time, 'bike_time':bike_time,
                                      't2':transition2_time, 'run_time':run_time, 'full_time':full_time,
                                      'ageGender':ageGender, 'location':location,
                                     })
                    rows_processed += 1
                    print(f"{racer_data_filename}: {rows_processed}/{row_count} rows complete")

    return 1, racer_urls_filepath


def interactive_scrape():
    # Loads in and writers headers to file. Use object to writer every subsequent complaint row in csv
    writer = classes.Writer(name='test')

    driver = webdriver.Chrome()
    user_input = 'print()'
    while True:
        print('Enter selenium code (or type "exit") to leave program:')
        user_input = input()
        if user_input == 'exit':
            break
        else:
            try:
                exec(user_input)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    process_racer_files()