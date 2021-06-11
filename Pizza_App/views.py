from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import decimal
# Create your views here.
states=["AK","AL","AR","AS","CA","AZ","CO","CT","DC","DE","FL","GA","GU","HI","IA","ID","IL","IN","KS","KY","LA","MA","MD","ME","MI","MN","MO","MS","MT","NC","ND","NE","NH","NJ","NM","NV","NY","OH","OK","OR","PA","PR","RI","SC","SD","TN","TX","UT","VA","VI","VT","WA","WI","WV","WY"]
size=["Small","Medium","Large"]
crust=["Hand Toss","Thin Crust"]
topping=['Italian Sausage','Beef','Chicken','Pepperoni','Mushroom','Pineapple','Spinach']
price={
    'size': {
        'Small': 7.99,
        'Medium': 8.99,
        'Large': 9.99,
    },
    'topping':{
        'Italian Sausage': 0.99,
        'Beef': 0.99,
        'Chicken': 0.99,
        'Pepperoni': 0.49,
        'Mushroom': 0.49,
        'Pineapple': 0.99,
        'Spinach': 0.99,
    }
}
def index(request):
    # make it redirect to main 
    return redirect('/main')

def main(request):
    # render main used for register and log in
    context={
        'states':states,
    }
    return render(request,"main.html",context)


def register(request):
    #register user into database. flush session before doing that, validate users to make sure its unique. if errors, show messages
    request.session.flush()
    errors=User.objects.validate(request.POST)
    if errors:
        for key, val in errors.items():
            messages.error(request,val)
        return redirect('/')
    newUser=User.objects.register(request.POST) #create new user, add to database
    request.session['userID']=newUser.id #making new user's ID to be current session's userid.
    return redirect('/order') #now, go to order page

def login(request):
    request.session.flush() #flush session before login
    if not User.objects.authenticate(request.POST['username'], request.POST['password']): #if username not match, back to main
        messages.error(request,"Invalid Username/Password. Please enter again!")
        return redirect('/')
    currentUser=User.objects.get(username=request.POST['username']) 
    request.session['userID']=currentUser.id
    return redirect('/order')

def order(request):
    # Order Page
    if 'userID' not in request.session:
        return redirect('/')
    user=User.objects.get(id=request.session['userID']) #get the current user in order for model to work, pulling by id.
    if 'orderID' not in request.session: #have to create new order, since the foreign key in pizza require order to be made first
        newOrder=Order.objects.create( #similarly, user has to be presented for order to be made.
            user=user
        )
        request.session['orderID']=newOrder.id #make new orderID session to be this new order's ID.
    context={
        'order':Order.objects.get(id=request.session['orderID']), #this is to show order quantity on navbar.
        'user': user,
        'sizes': size,
        'crusts': crust,
        'toppings': topping,
        'prices': price
    }
    return render(request, 'order.html',context)


def purchase(request): # this is execute when click on "Add to order"
    # When click purchase, make the pizza with all info needed(size, crust, topping, price), then add that pizza to order. pizza price will be added to order total price.
    sizePrice=price['size'][request.POST['size']] #price depending on pizza size
    toppingChecked=request.POST.getlist('topping') #group everything with the name"topping" that has been checked.
    toppingPrice=0
    toppingList=[]
    for i in toppingChecked:
        toppingList.append(i)
    toppinglist=", ".join(toppingList) #Put all the toppings into 1 long string in order to add to toppings in pizza
    for topping in toppingChecked:
        toppingPrice+=price['topping'][f"{topping}"]
    totalPrice=sizePrice+toppingPrice
    order=Order.objects.get(id=request.session['orderID'])
    pizza=Pizza.objects.create(
        size=request.POST['size'],
        crust=request.POST['crust'],
        toppings=toppinglist,
        price=round(totalPrice,2),
        order=order
    )
    # update orderPrice and quantity, this one should be updated everytime "Add to order" is executed.
    order.orderPrice+=decimal.Decimal(pizza.price)
    order.quantity+=1
    order.save()
    return redirect('/checkout')

def logout(request):
    request.session.flush()
    return redirect('/')

def account(request):
    if 'userID' not in request.session:
        return redirect('/')
    user=User.objects.get(id=request.session['userID'])
    context={
        'previouspizzas': Purchased_Pizza.objects.all(),
        'pizzas': Purchased_Order.objects.get(id=request.session['orderID']).Pizza.all(),
        'orders': Purchased_Order.objects.all(),
        'order':Order.objects.get(id=request.session['orderID']),
        'user': user,
        'states':states,
    }
    return render(request, 'account.html', context)

def update(request):
    updatedUser = User.objects.get(id=request.session['userID'])
    if request.POST['fname']:
        updatedUser.fname=request.POST['fname']
    if request.POST['lname']:
        updatedUser.lname=request.POST['lname']
    if request.POST['email']:
        updatedUser.email=request.POST['email']
    if request.POST['address']:
        updatedUser.address=request.POST['address']
    if request.POST['city']:
        updatedUser.city=request.POST['city']
    if request.POST['zipcode']:
        updatedUser.zipcode=request.POST['zipcode']
    if request.POST['password'] and request.POST['password'] == request.POST['cfpassword']:
        encryptedPassword=bcrypt.hashpw(request.POST['password'].encode(),bcrypt.gensalt()).decode()
        updatedUser.password=encryptedPassword
    updatedUser.save()
    return redirect('/account')

def checkout(request):
    if 'userID' not in request.session:
        return redirect('/')
    context={
        'order':Order.objects.get(id=request.session['orderID']),
        'user': User.objects.get(id=request.session['userID']),
        'pizzas': Order.objects.get(id=request.session['orderID']).Pizza.all(),
        'orders': Order.objects.all()
    }
    return render(request, 'checkout.html',context)


def reorder(request):
    #adding previous pizzas into current order and redirect to order page.
    order=Order.objects.get(id=request.session['orderID'])
    reorderPizza=Pizza.objects.create(
        size=request.POST.get('size'),
        crust=request.POST.get('crust'),
        toppings=request.POST['toppings'],
        price=request.POST['price'],
        order=order,
        )
    order.orderPrice+=decimal.Decimal(reorderPizza.price)
    order.quantity+=1
    order.save()
    return redirect('/checkout')

def cancel(request):
    #cancel current order, go back to order page
    order_ID_To_Cancel=request.POST['orderID']
    order_To_Cancel=Order.objects.get(id=order_ID_To_Cancel)
    order_To_Cancel.delete()
    del request.session['orderID']
    return redirect('/order')

def submitorder(request):
    #Purchase action. Save all orders and pizzas to more permanent class (Purchased_Order and Purchased_Pizza), then proceed to delete the object from Order and Pizza.
    PurchaseOrder_ID=request.POST['orderID']
    PurchaseOrder=Order.objects.get(id=PurchaseOrder_ID)
    SaveOrder=Purchased_Order.objects.create(
        user=User.objects.get(id=request.session['userID']),
        orderPrice=PurchaseOrder.orderPrice,
        quantity=PurchaseOrder.quantity,
    )
    Pizza_list_to_save=Pizza.objects.filter(order=PurchaseOrder)
    for pizza in Pizza_list_to_save:
        Purchased_Pizza.objects.create(
            size=pizza.size,
            crust=pizza.crust,
            toppings=pizza.toppings,
            price=pizza.price,
            order=SaveOrder,
        )
    Pizza.objects.all().delete()        
    Order.objects.all().delete()
    newOrder=Order.objects.create( #similarly, user has to be presented for order to be made.
        user=User.objects.get(id=request.session['userID'])
    )
    context={
        'order': Purchased_Order.objects.last()
    }
    request.session['orderID']=newOrder.id    
    return render(request,"thankyou.html",context)