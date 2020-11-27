from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from todo.forms import TodoForm
from todo.models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'todo/home.html')
    
def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('usertodos')
            except IntegrityError:
                error = 'The username has already existed. Please choose a new username.'
                return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':error})
        else:
            error = 'Passwords did not match.'
            return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':error})

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            error = 'Usernaem and password did not match'
            return render(request, 'todo/loginuser.html', {'form':AuthenticationForm(), 'error':error})
        else:
            login(request, user)
            return redirect('usertodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def usertodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo/usertodos.html', {'todos':todos})

@login_required
def posttodo(request):
    if request.method == 'GET':
        return render(request, 'todo/posttodo.html', {'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newTodo = form.save(commit=False)
            newTodo.user = request.user
            newTodo.save()
            return redirect('usertodos')
        except ValueError:
            print('fffffffffffffffffffffffffffffff')
            error = 'Bad data passed in.'
            return render(request, 'todo/posttodo.html', {'form':TodoForm(), 'error':error})

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos':todos})

@login_required
def tododetail(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/tododetail.html', {'todo':todo, 'form':form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('usertodos')
        except ValueError:
            error = 'Bad data passed in.'
            return render(request, 'todo/tododetail.html', {'todo':todo(), 'form':form, 'error':error})

@login_required        
def todocompleted(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('usertodos')
 
@login_required   
def tododelete(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('usertodos')