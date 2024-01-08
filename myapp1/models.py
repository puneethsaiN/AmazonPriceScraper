from django.db import models

# Create your models here.

class Product(models.Model):
	def __str__(self):
		return self.searchText
	searchText = models.CharField(max_length = 200)

class ProductHistory(models.Model):
	def __str__(self):
		return self.title
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	url = models.URLField()
	title = models.CharField(max_length = 200)
	price = models.FloatField()
	priceChange = models.FloatField()
	dateAdded = models.DateTimeField()
