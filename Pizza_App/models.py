from django.db import models
import re,bcrypt

# Create your models here.
class UserManager(models.Manager):
    # Validate class User
    def validate(self,post_data):
        errors={}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        ZIPCODE_REGEX = re.compile(r'^[0-9]')
        if len(post_data['username']) < 2:
            errors['username']="Username must have at least 2 characters"
        username_validate=self.filter(username=post_data['username'])
        if username_validate:
            errors['username']="Username already taken, please type in different username."
        if len(post_data['fname']) < 2:
            errors['fname']="First name must have at least 2 characters"
        if len(post_data['lname']) < 2:
            errors['lname']="Last name must have at least 2 characters"            
        if len(post_data['email']) < 2:
            errors['email']="Email must have at least 2 characters"
        if not EMAIL_REGEX.match(post_data['email']):
            errors['email']="Invalid email address, please type correct email address"
        email_validate=self.filter(email=post_data['email'])
        if email_validate:
            errors['email']="Email's already in use. Please choose a different email"
        if len(post_data['city']) < 2:
            errors['city']="City must have at least 2 characters"
        if len(post_data['state']) != 2:
            errors['state']="Please choose your state"
        if len(post_data['zipcode']) !=5:
            errors['zipcode']="Please type in your zipcode"
        if not ZIPCODE_REGEX.match(post_data['zipcode']):
            errors['zipcode']="Please make sure your zipcode is valid"
        if len(post_data['password']) < 2:
            errors['password']="Password must have at least 8 characters"
        if post_data['password'] != post_data['cfpassword']:
            errors['password']="Password must match"
        return errors
    
    def register(self,post_data):
        encryptedPassword=bcrypt.hashpw(post_data['password'].encode(),bcrypt.gensalt()).decode()
        return self.create(
            username=post_data['username'],
            fname=post_data['fname'],
            lname=post_data['lname'],
            email=post_data['email'],
            address=post_data['address'],
            city=post_data['city'],
            state=post_data['state'],
            zipcode=post_data['zipcode'],
            password=encryptedPassword,
        )
        
    def authenticate(self, username, password):
        usersToCheck=self.filter(username=username)
        
        if not usersToCheck:
            return False
        user=usersToCheck[0]
        return bcrypt.checkpw(password.encode(),user.password.encode())


class User(models.Model):
    username=models.CharField(max_length=32)
    fname=models.CharField(max_length=32)
    lname=models.CharField(max_length=32)
    email=models.EmailField(max_length=255)
    address=models.CharField(max_length=255)
    city=models.CharField(max_length=50)
    state=models.CharField(max_length=2)
    zipcode=models.CharField(max_length=5)
    password=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects=UserManager()
    
    def __repr__(self):
        return f"{self.id} {self.fname} {self.lname}. Email: {self.email} Address: {self.address}, {self.city} {self.state}, {self.zipcode}"
    
class Order(models.Model):
    quantity=models.IntegerField(default=0)
    orderPrice=models.DecimalField(decimal_places=2,max_digits=5,default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    user=models.ForeignKey(User,related_name="Order",on_delete=models.CASCADE,null=True)
    # Order can have many pizzas, user can have many orders.

class Purchased_Order(models.Model):
    quantity=models.IntegerField(default=0)
    orderPrice=models.DecimalField(decimal_places=2,max_digits=5,default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    user=models.ForeignKey(User,related_name="Purchase_Order",on_delete=models.CASCADE)
    # this order only got created when actual purchase happened.

class Pizza(models.Model):
    size=models.CharField(max_length=10)
    crust=models.CharField(max_length=20)
    toppings=models.CharField(max_length=255) #in order to show previous order, should be a long string with all topping in there 
    price=models.DecimalField(decimal_places=2,max_digits=5)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    order=models.ForeignKey(Order, related_name="Pizza",on_delete=models.CASCADE,null=True)
    
class Purchased_Pizza(models.Model):
    size=models.CharField(max_length=10)
    crust=models.CharField(max_length=20)
    toppings=models.CharField(max_length=255)
    price=models.DecimalField(decimal_places=2,max_digits=5)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    order=models.ForeignKey(Purchased_Order, related_name="Pizza",on_delete=models.CASCADE,null=True)
    #same, this class only got created when actual purchase happen.


