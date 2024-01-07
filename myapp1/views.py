from django.shortcuts import render
from .models import Product, ProductHistory
import chromedriver_autoinstaller
import time
import pandas as pd
from selenium.webdriver.common.by import By 
from bs4 import BeautifulSoup
import seleniumwire.undetected_chromedriver.v2 as wd
from django.utils import timezone

def makeResultList(driver, productname):
	url = "https://www.amazon.in/gp/new-releases/?ref_=nav_em_cs_newreleases_0_1_1_3"
	req = driver.get(url)
	time.sleep(8)
	search_bar = driver.find_element(By.ID, "twotabsearchtextbox")
	search_bar.send_keys(productname)
	search_ok_button = driver.find_element(By.ID, "nav-search-submit-button")
	search_ok_button.click()
	soup = BeautifulSoup(driver.page_source)
	data_list = []
	pages = 1
	while(pages > 0):
		pages -= 1
		results = soup.findAll("div", {"data-component-type" : "s-search-result"})
		results

		for result in results:
			title = result.find("span", {"class" : "a-text-normal"})
			price = result.find("span", {"class" : "a-price-whole"})
			url = result.find("a", {"class": "a-link-normal"}, href = True)
		
			if price is not None:
				data_list.append([title.text, price.text, "https://www.amazon.in/"+url['href'], productname])
				

		
		nextPageLink = driver.find_element(By.CLASS_NAME, "s-pagination-next")
		time.sleep(2)
		nextPageCSSLinks = nextPageLink.get_attribute("class").split()
		if not "s-pagination-disabled" in nextPageCSSLinks:
			nextPageLink.click()
			time.sleep(5)
		else:
			print("End of page")
			break
	# scraped_data_df = pd.DataFrame(data_list, columns=["title","price","url"])
	# return scraped_data_df
	df = pd.DataFrame(data_list, columns=["title","price","url","prod_name"])
	df['title'] = df['title'].str.lower()
	df = df[df['title'].str.contains(productname)]
	return df

def search_items(productnamelist):
	chromedriver_autoinstaller.install()  
	options = {
		'proxy': {
        # 'http': 'http://username:password@host:port',
        # 'https': 'https://username:password@host:port'
    }
	}
	driver = wd.Chrome(seleniumwire_options = options)
	time.sleep(8)	
	all_items_df = pd.DataFrame(columns=["title","price","url","prod_name"])
	for item in productnamelist:
		data_df = makeResultList(driver, item)
		all_items_df = pd.concat([all_items_df, data_df], ignore_index=True)

	scraped_data_df = all_items_df
	#converting price column to int
	scraped_data_df['price'] = scraped_data_df['price'].str.replace(',','').astype(float)

	return scraped_data_df

def addItemsToDB(scrapedItems):
	for index, item in scrapedItems.iterrows():
		existing_product = Product.objects.filter(searchText=item["prod_name"]).first()
		if existing_product is None:
            # Product doesn't exist, create a new one
			new_product = Product(
				title=item["title"],
				searchText=item["prod_name"],
				url=item["url"],
			)
			new_product.save()
			curr_item = new_product
		else:
			curr_item = existing_product

		item_history_obj = ProductHistory.objects.filter(product__title=item.title).first()
		if item_history_obj is None:
			product_history = ProductHistory(
				product = curr_item,
				price = item["price"],
				priceChange = 0,
				dateAdded = timezone.now(),
			)
			product_history.save()
		else:
			latest_product_history_item = ProductHistory.objects.filter(product__title=item.title).order_by('-dateAdded').first()
			old_price = latest_product_history_item.price
			product_history = ProductHistory(
				product = curr_item,
				price = item["price"],
				priceChange = old_price - item["price"],
				dateAdded = timezone.now()
			)
			product_history.save()
		

# Create your views here.
def index(request):
	scraped_items = search_items(["zephyrus g14", "oneplus 11 5g"])
	addItemsToDB(scraped_items)
	allProd = Product.objects.all()
	allProdHist = ProductHistory.objects.all()
	return render(
		request = request,
		template_name = "index.html",
		context = {
			"allProd" : allProd,
			"allProdHist" : allProdHist,
		}
	)
