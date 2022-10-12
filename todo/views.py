from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def home(request):
    if request.user.is_authenticated:
        return redirect('currenttodos')
    return render(request, 'todo/home.html')


def loginuser(request):
    if request.method == "GET":
        return render(request, 'todo/loginuser.html', {'form':   AuthenticationForm()})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'Invalid login/password'})
        else:
            login(request, user)
            return redirect('currenttodos')


def signupuser(request):
    if request.method == "GET":
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            if len(request.POST['password1']) < 6:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Length of the password has to be at least 6 symbols'})
            if len(request.POST['username']) < 3:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Length of the username should be at least 3 symbols'})
            try:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'That username has already been taken'})
        else:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Passwords did not match'})


@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)

    paginator = Paginator(todos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'todo/currenttodos.html', {'todos': page_obj, 'currenttodos': True, 'todos_total': len(todos), 'ndefault': True})


@login_required
def completedtodos(request):
    todos = Todo.objects.filter(
        user=request.user, datecompleted__isnull=False).order_by('-datecompleted')

    paginator = Paginator(todos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'todo/completedtodos.html', {'todos': page_obj, 'completedtodos': True, 'todos_total': len(todos), 'ndefault': True})


@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError as e:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': e.__str__})


@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': TodoForm(), 'createtodo': True, })
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('currenttodos')
        except ValueError as e:
            return render(request, 'todo/createtodo.html', {'form': TodoForm(), 'error': e.__str__})


@login_required
def logoutuser(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')
