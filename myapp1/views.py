from django.shortcuts import render, redirect
from django.db.models import Max, F
from .models import Product, ProductHistory
from .forms import newProdForm
import chromedriver_autoinstaller
import time
import pandas as pd
from selenium.webdriver.common.by import By 
from bs4 import BeautifulSoup
import seleniumwire.undetected_chromedriver as wd
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
        # 'http': 'http://username:password@p.webshare.io:80',
        # 'https': 'https://username:password@p.webshare.io:80'
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
		curr_item = Product.objects.filter(searchText=item["prod_name"]).first()
		item_history_obj = ProductHistory.objects.filter(url=item.url).first()
		if item_history_obj is None:
			product_history = ProductHistory( # need to split the price as a child table to product table
				product = curr_item,
				title=item["title"],
				url=item["url"],
				price = item["price"],
				priceChange = 0,
				dateAdded = timezone.now(),
			)
			product_history.save()
		else:
			latest_product_history_item = ProductHistory.objects.filter(url=item.url).order_by('-dateAdded').first()
			old_price = latest_product_history_item.price
			product_history = ProductHistory(
				product = curr_item,
				title=item["title"],
				url=item["url"],
				price = item["price"],
				priceChange = old_price - item["price"],
				dateAdded = timezone.now()
			)
			product_history.save()
		

# Create your views here.
			
def refreshProductPage(request):
	searchItemList = list(Product.objects.all().values_list('searchText', flat=True))
	scraped_items = search_items(searchItemList)
	addItemsToDB(scraped_items)
	return redirect('/index')

def addProduct(request):
	if request.method == "POST":
		form = newProdForm(request.POST)
		if form.is_valid():
			text = form.cleaned_data['searchText']
			# check if this product already exists in table
			item = Product.objects.filter(searchText = text)
			if(item.count()==0):
				newProd = Product(searchText = text)
				newProd.save()
			else:
				print("item already exists!")
	return redirect('/index')

def index(request):
	allProd = Product.objects.all()
	allProdHist = ProductHistory.objects.all()

	newForm = newProdForm()
	return render(
		request = request,
		template_name = "index.html",
		context = {
			"allProd" : allProd,
			"allProdHist" : allProdHist,
			"newProdForm" : newForm,
		}
	)
