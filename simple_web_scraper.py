import time
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Define our data structures
class WeatherDatum:
    def __init__(self, date: str, min_temp: int, max_temp: int, summary: str,
                 rain_amount: float, rain_prob: int, wind_speed: float,
                 wind_dir: str, pressure: int, humidity: int, uv: int,
                 dew_point: int):
        self.date = date
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.summary = summary
        self.rain_amount = rain_amount
        self.rain_prob = rain_prob
        self.wind_speed = wind_speed
        self.wind_dir = wind_dir
        self.pressure = pressure
        self.humidity = humidity
        self.uv = uv
        self.dew_point = dew_point

# Entrypoint to the program
def main():
    # Sydney weather
    url = 'https://openweathermap.org/city/2147714'
    driver = get_driver()
    # Wait for pages and elements to load
    driver.implicitly_wait(3)
    driver.get(url)
    weather_data = scrape_weather_website(driver)
    # Not needed
    exit(0)

def get_driver():
    chrome_service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    # Arguments that I have found useful across websites
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1920x1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--remote-debugging-port=9230')
    chrome_options.add_argument('disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('prefs',  {
        'download.default_directory': '.',
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'plugins.always_open_pdf_externally': True,
        # Keep the window from being opened
        'detach': True
    })
    desired_capabilities = DesiredCapabilities.CHROME.copy() 
    desired_capabilities['acceptInsecureCerts'] = True
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options, desired_capabilities=desired_capabilities)
    # Make the driver stealthy
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver

def scrape_weather_website(driver):
    weather_data = []
    time.sleep(3)
    for i in range(8):
        date = driver.find_element(By.XPATH, f'//ul[@class="day-list"]/li[{i+1}]/span').text
        min_max = driver.find_element(By.XPATH, f'//ul[@class="day-list"]/li[{i+1}]/div/div').text
        # min_max looks like 27 / 19°C
        min_max = min_max.replace('°C', '').strip().split('/')
        min_temp = int(min_max[0].strip())
        max_temp = int(min_max[1].strip())
        # Click on the element to get more weather detail
        time.sleep(10)
        driver.find_element(By.XPATH, f'//ul[@class="day-list"]/li[{i+1}]/span').click()
        summary = driver.find_element(By.XPATH, f'//div[@class="top-section"]/div/p[1]').text
        rain_amount = float(driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[1]/span[1]').text.replace('mm',''))
        rain_prob = int(driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[1]/span[2]').text.replace('(','').replace('%)',''))
        wind_data = driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[2]/div').text
        wind_speed = float(wind_data.split(' ')[0].replace('m/s',''))
        wind_dir = wind_data.split(' ')[1].strip()
        pressure = int(driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[3]').text.replace('hPa',''))
        humidity = int(driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[4]').text.split('\n')[1].replace('%',''))
        uv = int(driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[5]').text.split('\n')[1])
        dew_point = int(driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[6]').text.split('\n')[1].replace('°C',''))
        weather_datum = WeatherDatum(date, min_temp, max_temp, summary, rain_amount, rain_prob,
                                     wind_speed, wind_dir, pressure, humidity, uv, dew_point)
        weather_data.append(weather_datum)
        driver.find_element(By.XPATH, f'//div[@class="scrolling-container-header"]/span').click()
        # Incase they have scraper detection
        time.sleep(1)
    return weather_data

if __name__ == "__main__":
    main()