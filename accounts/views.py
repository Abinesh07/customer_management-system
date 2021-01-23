from django.shortcuts import render, redirect
from .models import *
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from .forms import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_user, admin_only
from django.contrib.auth.models import Group



@unauthenticated_user
def RegistrationPage(request):

	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			user_name = form.cleaned_data.get('username')

			group = Group.objects.get(name='customer')
			user.groups.add(group)
			Customer.objects.create(
				user=user,
				)

			messages.success(request, 'Account was created for ' + user_name )
			return redirect ('login')
		else:
			messages.info(request, 'wrong credentials')
	context = {'form': form}
	return render(request, 'accounts/registrationpage.html', context)

@unauthenticated_user
def LoginPage(request):

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('home')
	context = {}
	return render(request, 'accounts/loginpage.html', context)


def LogoutPage(request):
	logout(request)
	return redirect ('login')

@login_required(login_url='login')
@allowed_user(allowed_roles=['customer'])
def accountSettings(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)
	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES,instance=customer)
		if form.is_valid():
			form.save()

	context = {'form': form}
	return render(request, 'accounts/account_settings.html', context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['customer'])
def userpage(request):
	orders = request.user.customer.order_set.all()
	total_orders = orders.count()
	pending = orders.filter(status='Pending').count()
	delivered = orders.filter(status= 'Delivered').count()

	context = {'orders': orders, 'pending': pending,
	'delivered': delivered, 'total_orders': total_orders}

	return render(request, 'accounts/user_page.html', context)


@login_required(login_url='login')
@admin_only
def home(request):
	orders = Order.objects.all()
	customers = Customer.objects.all()
	total_customer = customers.count()

	total_orders = orders.count()
	pending = orders.filter(status='Pending').count()
	delivered = orders.filter(status= 'Delivered').count()
	context = {'orders': orders, 'customers':customers, 'pending': pending,
	'delivered': delivered, 'total_orders': total_orders }
	return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def products(request):
	products = Product.objects.all()
	return render(request, 'accounts/products.html', {'products': products})


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def customer(request, pk):
	customer = Customer.objects.get(id=pk)
	orders = customer.order_set.all()
	total_order = orders.count()
	total_customer = Customer.objects.all().count()

	myFilter = OrderFilter(request.GET, queryset=orders)
	orders = myFilter.qs

	context = {'customer': customer, 'orders': orders, 
	'total_customer': total_customer, 'total_order': total_order, 'myFilter': myFilter}
	
	return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def createOrder(request, pk):
	OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
	customer = Customer.objects.get(id=pk)
	formset = OrderFormSet( queryset=Order.objects.none(),instance=customer)
	# form = OrderForm(initial={'customer': customer})
	if request.method =='POST':
		formset = OrderFormSet( request.POST,instance=customer)
		# form=OrderForm(request.POST)
		if formset.is_valid():
			formset.save()
			return redirect('/')
	context = {'formset': formset}
	return render(request, 'accounts/order_form.html', context )


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def updateOrder(request, pk):
	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)
	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			return redirect('/')
	context = {'form': form}
	return render(request, 'accounts/order_form.html', context)



@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def deleteOrder(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == 'POST':
		order.delete()
		return redirect ('/')
	context = {'item': order}
	return render(request, 'accounts/delete_order.html' , context)