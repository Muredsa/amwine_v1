import datetime
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import scrapy




class AmwineSpider(scrapy.Spider):
    name = "amwine"
    driver_path = r'C:\Users\dliba\PycharmProjects\amwine\webdriver\chromedriver.exe'
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-login-animations")
    start_urls = (
        #'https://amwine.ru/catalog/krepkie_napitki/viski/',
        'https://amwine.ru/catalog/krepkie_napitki/konyak/',
    )


    def start_requests(self):
        driver = Chrome(executable_path=self.driver_path, options=self.options)
        driver
        for url in self.start_urls:
            driver.get(url)
            pages = driver.find_element_by_css_selector('ul.catalog-pagination').find_elements_by_css_selector('li')[-1].text
            for page in range(int(pages)):
                url_page = url+f"?page={page+1}"
                yield scrapy.Request(url=url_page ,callback=self.parse_pages)
            driver.quit()


    def parse_pages(self, response):
        driver = Chrome(executable_path=self.driver_path, options=self.options)
        driver.get(response.url)
        link_products = driver.find_elements_by_css_selector('a.catalog-list-item__title')
        for link in link_products:
            link_rel = link.get_attribute('href')
            yield scrapy.Request(url=link_rel, callback=self.parse_product)
        driver.quit()


    def parse_product(self, response):
        driver = Chrome(executable_path=self.driver_path, options=self.options)
        for url in response.url:
            driver.get(response.url)
            timestamp = datetime.datetime.now().timestamp()
            url = response.url

            try:
                rpc = driver.find_element_by_xpath('//*[@id="catalog-element-main"]/div[2]/div/div[1]/div/div[5]/div[1]/span').text.replace('Артикул : ','')
            except:
                rpc = driver.find_element_by_xpath('//*[@id="catalog-element-main"]/div[2]/div/div[1]/div/div[4]/div[1]/span').text.replace('Артикул : ','')

            title = driver.find_element_by_css_selector('div.catalog-element-info__title').find_element_by_css_selector('h1').text

            marketing_tags = []

            brand = driver.find_element_by_css_selector('div.about-wine-top').find_element_by_css_selector('h2').text.replace('Подробнее о ','')

            sections = driver.find_element_by_css_selector('div.breadcrumbs').find_elements_by_css_selector('a.breadcrumbs__link')

            new_sections = []
            for section in sections:
                new_sections.append(section.text)

            try:
                current_price = float(driver.find_element_by_xpath('//*[@id="catalog-element-main"]/div[2]/div/div[1]/div/div[5]/div/span').text.replace('₽','').replace(' ',''))
            except:
                current_price = float(driver.find_element_by_xpath('//*[@id="catalog-element-main"]/div[2]/div/div[1]/div/div[5]/span[2]').text.replace('₽','').replace(' ',''))

            try:
                main_image = driver.find_element_by_xpath('//*[@id="catalog-element-main"]/div[2]/div/div[1]/div/div[4]/div[3]/div[2]/div/div/div').value_of_css_property('background').replace('rgba(0, 0, 0, 0) url(\"','').replace('\") no-repeat scroll 50% 50% / contain padding-box border-box','')
            except:
                main_image = self.allowed_domains[0]+driver.find_element_by_xpath('//*[@id="catalog-element-main"]/div[2]/div/div[1]/div/div[1]/img').get_attribute('src')
            country = driver.find_element_by_xpath('//*[@id="about-drink"]/div/div[1]/div[1]/span[2]/a').text
            about_wine_body_div_count = len(driver.find_element_by_css_selector('div.about-wine__block_params').find_elements_by_css_selector('div'))
            volume = driver.find_element_by_xpath('//*[@id="about-drink"]/div/div[1]/div[2]/span[2]').text
            manufacturer = driver.find_element_by_xpath('//*[@id="about-drink"]/div/div[1]/div[3]/span[2]/a').text

            if about_wine_body_div_count == 5:
                fortress = driver.find_element_by_xpath('//*[@id="about-drink"]/div/div[1]/div[4]/span[2]').text
                excerpt = driver.find_element_by_xpath('//*[@id="about-drink"]/div/div[1]/div[5]/span[2]').text
            elif about_wine_body_div_count == 6:
                fortress = driver.find_element_by_xpath('//*[@id="about-drink"]/div/div[1]/div[5]/span[2]').text
                excerpt = driver.find_element_by_xpath('//*[@id="about-drink"]/div/div[1]/div[6]/span[2]').text
            else:
                fortress = driver.find_element_by_xpath('//*[@id="about-drink"]/div/div[1]/div[4]/span[2]').text
                excerpt = ""

            main_block_of_additional_parameters = driver.find_elements_by_css_selector('div.about-wine__block')
            description = main_block_of_additional_parameters[0].find_element_by_css_selector('p').text
            if len(main_block_of_additional_parameters) == 5:
                color = main_block_of_additional_parameters[1].find_element_by_css_selector('p').text
                aroma = main_block_of_additional_parameters[2].find_element_by_css_selector('p').text
                taste = main_block_of_additional_parameters[3].find_element_by_css_selector('p').text
                gastronomic_combinations = main_block_of_additional_parameters[4].find_element_by_css_selector('p').text
                about_manufacturers = ""
            elif len(main_block_of_additional_parameters) == 6:
                color = main_block_of_additional_parameters[2].find_element_by_css_selector('p').text
                aroma = main_block_of_additional_parameters[3].find_element_by_css_selector('p').text
                taste = main_block_of_additional_parameters[1].find_element_by_css_selector('p').text
                gastronomic_combinations = main_block_of_additional_parameters[4].find_element_by_css_selector('p').text
                about_manufacturers = main_block_of_additional_parameters[5].find_element_by_css_selector('p').text

            try:
                original = float(driver.find_element_by_xpath('//*[@id="catalog-element-main"]/div[2]/div/div[1]/div/div[6]/div/div/span').text.replace('₽','').replace(' ',''))
                sale_tag = f"Скидка {(str(int(100 - (current_price / original * 100))))}%"
                in_stock_element = driver.find_element_by_xpath('//*[@id="catalog-element-main"]/div[2]/div/div[1]/div/div[10]/div[3]/span').text.replace(' ','')
                if in_stock_element == set(in_stock_element.split()) & "В наличии на складе":
                    in_stock = True
            except:
                in_stock = False
                original = current_price
                sale_tag = ""
            yield {
                    "timestamp":timestamp,
                    "RPC":rpc,
                    "url":url,
                    "title":title,
                    "marketing_tags":marketing_tags,
                    "brand":brand,
                    "section":new_sections,
                    "price_data":{
                        "current":current_price,
                        "original":original,
                        "sale_tag":sale_tag
                    },
                    "stock":{
                       "in_stock":in_stock,
                       "count":0
                    },
                    "assets":{
                       "main_image":str(main_image),
                       "set_images":str(main_image),
                       "view360":[],
                       "video":[]
                    },
                    "metadata":{
                        "__description":description,
                        "АРТИКУЛ":str(rpc),
                        "СТРАНА ПРОИЗВОДИТЕЛЬ":country,
                        "ОБЪЁМ":volume,
                        "БРЕНД": brand,
                        "ПРОИЗВОДИТЕЛЬ": manufacturer,
                        "КРЕПОСТЬ": fortress,
                        "ВЫДЕРЖКА": excerpt,
                        "ВКУС": taste,
                        "ЦВЕТ": color,
                        "АРОМАТ": aroma,
                        "ГАСТРОНОМИЧЕСКИЕ СОЧЕТАНИЯ": gastronomic_combinations,
                        "О ПРОИЗВОДИТЕЛЕ": about_manufacturers,
                    },
                    "variants":1
                    }
            driver.quit()




