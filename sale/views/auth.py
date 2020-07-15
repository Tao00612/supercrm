from django.shortcuts import render,redirect
from sale import models
from sale.utils.hashlib_func import set_md5
from django.http import JsonResponse
from sale.myforms import RegisterForm
from sale import views


# 注册
def register(request):
    if request.method == 'GET':
        register_form_obj = RegisterForm()
        return render(request,'register.html',{'register_form_obj':register_form_obj})
    else:
        register_form_obj = RegisterForm(request.POST)
        if register_form_obj.is_valid():
            register_form_obj.cleaned_data.pop('r_password')
            # 对密码进行加密
            password = register_form_obj.cleaned_data.pop('password')
            password = set_md5(password)
            register_form_obj.cleaned_data.update({'password': password})
            models.UserInfo.objects.create(
                **register_form_obj.cleaned_data
            )
            return redirect('login')
        else:
            return render(request,'register.html',{'register_form_obj':register_form_obj})


# 登录
def login(request):
    if request.method == 'GET':
        return render(request,'login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_ret = models.UserInfo.objects.filter(
            username=username,
            password=set_md5(password),
        ).first()
        print(user_ret.id)
        if user_ret:
            ret = {'code':0,'msg':'/crm/home/'}
            request.session['is_login'] = '1'
            request.session['user_id'] = user_ret.id
            # 将用户信息保存到session
            return JsonResponse(ret)
        else:
            ret = {'code': 3, 'msg': '账号密码错误'}
            return JsonResponse(ret)