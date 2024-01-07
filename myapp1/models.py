from django.db import models

# Create your models here.

class Product(models.Model):
	def __str__(self):
		return self.title
	title = models.CharField(max_length = 200)
	searchText = models.CharField(max_length = 200)
	url = models.URLField()

class ProductHistory(models.Model):
	def __str__(self):
		return self.product.title
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	price = models.FloatField()
	priceChange = models.FloatField()
	dateAdded = models.DateTimeField()
