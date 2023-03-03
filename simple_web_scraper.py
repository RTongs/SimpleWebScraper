import boto3, uuid, time, logging
from decimal import Decimal
from botocore.config import Config
from botocore.exceptions import ClientError
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Define our data structures
class WeatherDatum:
    def __init__(self, city: str, date: str, min_temp: int, max_temp: int, summary: str,
                 rain_amount: Decimal, rain_prob: int, wind_speed: Decimal,
                 wind_dir: str, pressure: int, humidity: int, uv: int,
                 dew_point: int):
        self.city = city
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

    def __str__(self):
        return f'City: {self.city}\n' +\
        f'Date: {self.date}\n' +\
        f'Minimum Temperature: {self.min_temp}\n' +\
        f'Maximum Temperature: {self.max_temp}\n' +\
        f'Summary: {self.summary}\n' +\
        f'Rain Amount: {self.rain_amount}\n' +\
        f'Rain Probability: {self.rain_prob}\n' +\
        f'Wind Speed: {self.wind_speed}\n' +\
        f'Wind Direction: {self.wind_dir}\n' +\
        f'Pressure: {self.pressure}\n' +\
        f'Humidity: {self.humidity}\n' +\
        f'UV: {self.humidity}\n' +\
        f'Dew Point: {self.uv}\n'

class CityInfo:
    def __init__(self, name, URL):
        self.name = name
        self.URL = URL

# Can toggle on and off to demonstrate
CLOUD = False

REGION_CONFIG = Config(
            region_name = 'ap-southeast-2',
            retries = {
                'max_attempts': 10,
                'mode': 'standard'
            }
)
CITY_TABLE_NAME = 'City'
WEATHER_TABLE_NAME = 'Weather'

# Entrypoint to the program
def main():
    # Automatically picks up credentials for our AWS from our environment variables passed into container
    dynamo_db_client = boto3.resource('dynamodb',
                       config = REGION_CONFIG)
    city_infos = None
    if CLOUD:
        city_infos = get_city_infos_cloud(dynamo_db_client)
    else:
        city_infos = get_city_infos()
    driver = get_driver()
    # Add some delays between operations to make us less suspicious
    driver.implicitly_wait(3)
    for count, city_info in enumerate(city_infos):
        driver.get(city_info.URL)
        weather_data = scrape_weather_website(driver, city_info.name)
        if CLOUD:
            write_to_dynamo_db(dynamo_db_client, weather_data)
        else:
            print_weather_data(weather_data)
    # Not needed
    exit(0)

def get_city_infos():
    city_infos = []
    city_infos.append(CityInfo('Sydney', 'https://openweathermap.org/city/2147714'))
    city_infos.append(CityInfo('Brisbane', 'https://openweathermap.org/city/2174003'))
    city_infos.append(CityInfo('Melbourne', 'https://openweathermap.org/city/2158177'))
    return city_infos

def get_driver():
    """
    DO
    """
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

def scrape_weather_website(driver, city):
    """
    Collect key weather data

    Parameters
    ----------
    driver: WebDriver
        selenium web driver that is already hooked up to our desired website

    Returns
    -------
    List containing populated WeatherDatum instances
    """
    weather_data = []
    time.sleep(3)
    for i in range(8):
        date = driver.find_element(By.XPATH, f'//ul[@class="day-list"]/li[{i+1}]/span').text
        min_max = driver.find_element(By.XPATH, f'//ul[@class="day-list"]/li[{i+1}]/div/div').text
        # min_max looks like 27 / 19°C
        min_max = min_max.replace('°C', '').strip().split('/')
        min_temp = int(min_max[1].strip())
        max_temp = int(min_max[0].strip())
        # Can increase the sleep time if website not loading in time (depends on CPU and network speed)
        time.sleep(5)
        # Click on the element to get more weather detail
        driver.find_element(By.XPATH, f'//ul[@class="day-list"]/li[{i+1}]/span').click()
        summary = driver.find_element(By.XPATH, f'//div[@class="top-section"]/div/p[1]').text
        # If there is no rain amount, then only rain probability is given so need to be careful
        rain_amount = driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[1]/span[1]').text
        if '%' in rain_amount:
            rain_prob = int(rain_amount.replace('%',''))
            rain_amount = Decimal(0)
        else:
            rain_amount = Decimal(rain_amount.replace('mm',''))
            rain_prob = int(driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[1]/span[2]').text.replace('(','').replace('%)',''))
        wind_data = driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[2]/div').text
        wind_speed = Decimal(wind_data.split(' ')[0].replace('m/s',''))
        wind_dir = wind_data.split(' ')[1].strip()
        pressure = int(driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[3]').text.replace('hPa',''))
        humidity = int(driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[4]').text.split('\n')[1].replace('%',''))
        uv = int(driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[5]').text.split('\n')[1])
        dew_point = int(driver.find_element(By.XPATH, f'//div[@class="daily-detail-container"]/ul/li[6]').text.split('\n')[1].replace('°C',''))
        weather_datum = WeatherDatum(city, date, min_temp, max_temp, summary, rain_amount, rain_prob,
                                     wind_speed, wind_dir, pressure, humidity, uv, dew_point)
        weather_data.append(weather_datum)
        driver.find_element(By.XPATH, f'//div[@class="scrolling-container-header"]/span').click()
        # Incase they have scraper detection
        time.sleep(1)
    return weather_data

def print_weather_data(weather_data):
    for count, weather_datum in enumerate(weather_data):
        print(f'{count} days from date')
        print(str(weather_datum))

def get_city_infos_cloud(dynamo_db_client):
    """
    DO
    """
    configuration_table = dynamo_db_client.Table(CITY_TABLE_NAME)
    # Scan can only return 1MB of data, fine for us
    response = configuration_table.scan()
    city_infos = []
    if len(response['Items']) != 0:
        all_city_info = response['Items']
        for i in range(len(all_city_info)):
            city_infos.append(CityInfo(all_city_info[i]['Name'], all_city_info[i]['URL']))
    return city_infos

def write_to_dynamo_db(dynamo_db_client, weather_data):
    """
    DO (assume ordering of dates!)
    """
    city_table = dynamo_db_client.Table(WEATHER_TABLE_NAME)
    try:
        for day_count, weather_datum in enumerate(weather_data):
            city_table.put_item(
                Item={
                    'Id': str(uuid.uuid4()),
                    'City': weather_datum.city,
                    'Date': weather_datum.date,
                    'DaysFromDate': day_count,
                    'MinTemp': weather_datum.min_temp,
                    'MaxTemp': weather_datum.max_temp,
                    'Summary': weather_datum.summary,
                    'RainAmount': weather_datum.rain_amount,
                    'RainProbability': weather_datum.rain_prob,
                    'WindSpeed': weather_datum.wind_speed,
                    'WindDirection': weather_datum.wind_dir,
                    'Pressure': weather_datum.pressure,
                    'Humidity': weather_datum.humidity,
                    'UV': weather_datum.uv,
                    'DewPoint': weather_datum.dew_point
                })
    except ClientError as err:
        # Log the error: err.response['Error']['Code'], err.response['Error']['Message']
        raise

if __name__ == "__main__":
    main()