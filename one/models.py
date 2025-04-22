
from django.db import models
from django.contrib.auth.models import User

class One(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=240)
    photo = models.ImageField(upload_to="photos/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    quantity = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0) 
    price=models.PositiveIntegerField(default=0)
    def __str__(self):
        return f'{self.user.username} - {self.text}'

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            total = sum(r.value for r in ratings)
            return round(total / ratings.count(), 2)
        return 0
    def update_quantity(self, purchased_quantity):
        """Update the quantity of the product when a purchase is made."""
        if purchased_quantity <= self.quantity:
            self.quantity -= purchased_quantity
            self.save()
        else:
            raise ValueError("Not enough stock available.")

class Rating(models.Model):
    post = models.ForeignKey(One, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField() 
   
    class Meta:
        unique_together = ('user', 'post') 
    def __str__(self):
        return f'{self.user.username} rated {self.value} for {self.post}'
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_paid=models.BooleanField(default=False)
class Cartitems(models.Model):
    cart=models.ForeignKey(Cart, related_name='cartitems',on_delete=models.CASCADE)
    product=models.ForeignKey(One, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price=models.IntegerField(default=0)
# class Jazzcah(models.Model):
#     user=models
#     amount=models.PositiveBigIntegerField(default=0)
