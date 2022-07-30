import os
import re
import requests
import time
import zipfile
from random import randint
from sys import platform
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def download_chrome_driver():
    """ Check the existence of the Chromedriver. If it doesn't exist, the function download the proper version
    depending on the os.
    """

    cwd = os.getcwd()
    folder_driver_path = os.path.join(cwd, "driver")
    driver_path = os.path.join(cwd, "driver", "chromedriver.exe")

    if platform == "linux" or platform == "linux2":
        chrome_type = "chromedriver_linux64"
    elif platform == "win32":
        chrome_type = "chromedriver_win32"

    if not os.path.exists(driver_path):
        if not os.path.isdir(folder_driver_path):
            os.mkdir("driver")
            if chrome_type == "chromedriver_win32":
                os.system('cmd /c "curl https://chromedriver.storage.googleapis.com/103.0.5060.134/{}.zip > '
                          '{}"'.format(chrome_type, (os.path.join(folder_driver_path, "chrome_driver.zip"))))
                with zipfile.ZipFile(os.path.join(folder_driver_path, "chrome_driver.zip"), 'r') as zip_ref:
                    zip_ref.extractall(folder_driver_path)
                os.remove(os.path.join(folder_driver_path, "chrome_driver.zip"))

            else:
                os.system("wget -N http://chromedriver.storage.googleapis.com/103.0.5060.134/chromedriver_linux64.zip")
                os.system("unzip chromedriver_linux64.zip")
                os.system("chmod +x chromedriver")
                os.system("mv -f chromedriver /usr/local/share/chromedriver")
                os.system("ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver")
                os.system("ln -s /usr/local/share/chromedriver /usr/bin/chromedriver")

    else:
        print("Chrome driver exists ! ")


def initialize_driver():
    """ Initialize the driver with appropriate options depending on the platform.

    Returns:
        driver

    """
    if platform == "linux" or platform == "linux2":
        options = webdriver.ChromeOptions()
        options.add_argument("--lang=en")
        options.binary_location = "/usr/bin/google-chrome"  # chrome binary location specified here
        options.add_argument("--start-maximized")  # open Browser in maximized mode
        options.add_argument('--headless')
        options.add_argument("--no-sandbox")  # bypass OS security model
        options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Chrome(r'/usr/local/share/chromedriver', options=options)
    else:
        cwd = os.getcwd()
        driver_path = os.path.join(cwd, "driver", "chromedriver.exe")
        options = webdriver.ChromeOptions()
        options.add_argument("--lang=en")
        options.add_argument('--headless')
        options.add_argument("--start-maximized")  # open Browser in maximized mode
        options.add_argument("--no-sandbox")  # bypass OS security model
        options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Chrome(driver_path, options=options)

    return driver


def get_full_path(name: str) -> str:
    """ Get the full URL of a facebook page.

    Args:
        name (str): the name of the facebook page.

    Returns:
        'str' : full URL of a facebook page.
    """
    return "https://facebook.com/{}".format(name)


def get_name(driver):
    """ Get the name of the actual facebook page opened by the driver

    Args:
        driver (selenium.webdriver.Chrome):

    Returns:
        str : a string containing the page name.
    """
    name = driver.find_element(By.TAG_NAME, "strong").get_attribute("textContent")
    return name


def close_error_popup(driver):
    """ Close the popup that appears when starting to scroll down.
    Notes: The pop-up appears with some facebook pages ex:"TED", "www.foot24.tn" ...
            and doesn't appear with others "santetunisie.rns.tn" ...
    Args:
        driver (selenium.webdriver.Chrome):

    Raises:
        WebDriverException: If the popup exist but the DOM is updated.
        ex : if the driver can't find the pop-up.
    """
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label=Close]")))
        driver.find_element(By.CSS_SELECTOR, "[aria-label=Close]").click()

    except WebDriverException as e:
        try:
            time.sleep(5)
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label=Close]")))
            driver.find_element(By.CSS_SELECTOR, "[aria-label=Close]").click()
        except WebDriverException as e:
            pass

    except Exception as ex:
        pass
        print("error at close_error_popup method : {}".format(ex))


def scroll_down_first(driver):
    """ Move to the middle of the page to see if the pop-up appears for the current page.

    Args:
        driver (selenium.webdriver.Chrome):
    """
    body = driver.find_element(By.CSS_SELECTOR, "body")
    for _ in range(randint(5, 6)):
        body.send_keys(Keys.PAGE_UP)
    for _ in range(randint(5, 8)):
        body.send_keys(Keys.PAGE_DOWN)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def check_timeout(start_time, current_time, timeout):
    """ Check if the scraper reached the timeout for scraping or not.

    Args:
        start_time (): Time when we start the scraping.
        current_time (): Actual time.
        timeout (int): Maximum time for scraping.

    Returns:
        bool: False if timeout reached. True otherwise.
    """
    return (current_time - start_time) > timeout


def scroll_to_bottom(driver, timeout):
    """ Scroll to the bottom of the current page opened by the driver.

    Args:
        driver ():
        timeout (int): Maximum time for scraping.

    Returns:
        bool : True if we reached the bottom of the page before timeout
                False if we reached the timeout.

    """
    old_position = 0
    new_position = None
    end_position = 0
    start_time = time.time()
    body = driver.find_element(By.CSS_SELECTOR, "body")

    while new_position != old_position and not check_timeout(start_time, time.time(), timeout):
        # Get old scroll position
        old_position = driver.execute_script(
            ("return (window.pageYOffset !== undefined) ?"
             " window.pageYOffset : (document.documentElement ||"
             " document.body.parentNode || document.body);"))
        # Sleep and Scroll
        time.sleep(1)
        driver.execute_script((
            "var scrollingElement = (document.scrollingElement ||"
            " document.body);scrollingElement.scrollTop ="
            " scrollingElement.scrollHeight;"))
        # Get new position
        new_position = driver.execute_script(
            ("return (window.pageYOffset !== undefined) ?"
             " window.pageYOffset : (document.documentElement ||"
             " document.body.parentNode || document.body);"))

        if end_position != new_position:
            for _ in range(randint(5, 6)):
                body.send_keys(Keys.PAGE_UP)
        end_position = new_position
    if new_position == old_position:
        return True
    else:
        return False


def get_text(post):
    """ Scrap the text of the current post.

    Returns:
        object: str if the post contain a text description.
                None if the post doesn't contain a text. (Only images/video/pdf ...)
    """
    try:
        div_text = post.find_element(By.CSS_SELECTOR, '[data-ad-comet-preview]')
        text = div_text.get_attribute('innerText')
    except:
        text = None
    return text


def get_shares_comments(post):
    """ Scrap the shares and comments of the current post.

    Returns:
        int: the number of shares of the current post.
        int: the number of comments of the current post.
    """

    elements = post.find_elements(By.CSS_SELECTOR, "div.gtad4xkn")
    shares = "0"
    comments = "0"
    for element in elements:
        text = element.get_attribute("innerText")
        if "Shares" in text:
            shares = re.findall("\d+", text)[0]

        if "Comments" in text:
            comments = re.findall("\d+", text)[0]

    return shares, comments


def get_reactions(post):
    """ Scrap the reactions of the current post.

    Returns:
        int: the number of reactions of the current post.
    """
    reactions = 0
    try:
        total_reactions = post.find_element(By.CSS_SELECTOR, 'span.ltmttdrg.gjzvkazv')
        reactions = total_reactions.get_attribute("innerText")
    except Exception as e:
        print(e)
    return reactions


def get_posted_time(post):
    """ Scrap the posted time of the current post.

    Returns:
        str : the posted time of the current post.
    """

    element = post.find_element(By.CSS_SELECTOR, "a.gpro0wi8.b1v8xokw")
    return element.get_attribute('innerText')


def get_images(post):
    """ Scrap all the images of the current post.

    Returns:
        list(str): links of all images of the current post.
    """

    list_of_images = []
    elements = post.find_elements(By.CSS_SELECTOR, 'div.do00u71z.ni8dbmo4.stjgntxs.l9j0dhe7 img.i09qtzwb')
    for element in elements:
        list_of_images.append(element.get_attribute('src'))
    return list_of_images


def get_link_video(post):
    """ Scrap the video of the current post.

    Returns:
        object: str: link of the video if the post contain a video.
                None if the post doesn't contain any video.
    """
    try:
        div_text = post.find_element(By.CSS_SELECTOR, "[aria-label='Enlarge']")
        text = div_text.get_attribute('href')
        text = text[:text.rfind("/")]
    except:
        text = None
    return text


def check_page_exists(name: str) -> bool:
    """ Check if a facebook page exists or not using the facebook graph.

    Args:
        name (str):  name of the facebook page.

    Returns:
        bool: True if the page exists.
              False otherwise.
    """

    url = "https://graph.facebook.com/" + name
    response = requests.get(url)

    if response.text.find("Unsupported get request") == -1:
        return True
    else:
        return False
