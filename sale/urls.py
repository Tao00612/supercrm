"""superorm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from sale.views import customer
from sale.views import auth
urlpatterns = [
    # 登录
    url(r'^login/', auth.login,name='login'),
    # 注册
    url(r'^register/', auth.register,name='register'),
    # 主页
    url(r'^home/', customer.home,name='home'),
    # 客户信息展示
    url(r'^customers/', customer.CustomersView.as_view(),name='customers'),
    # 我的客户
    url(r'^mycustomers/', customer.CustomersView.as_view(),name='mycustomers'),
    # 添加客户
    # url(r'^add_customer/', views.add_customer,name='add_customer'),
    url(r'^add_customer/', customer.add_edit_customer,name='add_customer'),
    # 编辑客户
    # url(r'^edit_customer/(\d+)', views.edit_customer,name='edit_customer'),
    url(r'^edit_customer/(\d+)', customer.add_edit_customer,name='edit_customer'),
    # 删除客户
    url(r'^del_customer/(\d+)', customer.del_customer,name='del_customer'),
    # 跟进记录展示
    url(r'^consult_record/', customer.ConsultRecordView.as_view(),name='consult_record'),
    # 添加跟进记录
    url(r'^add_consult/', customer.AddEditConsultView.as_view(),name='add_consult'),
    # 编辑跟进记录
    url(r'^edit_consult/(\d+)', customer.AddEditConsultView.as_view(),name='edit_consult'),

    # 报名记录
    url(r'^enrollment/', customer.EnrollmentView.as_view(),name='enrollment'),
    # 添加报名记录
    url(r'^enroll_add/', customer.AddEditEnrollView.as_view(),name='enroll_add'),
    # 编辑报名
    url(r'^enroll_edit/(\d+)/', customer.AddEditEnrollView.as_view(),name='enroll_edit'),
    # 客户记录
    url(r'^course_record/', customer.CourseRecordView.as_view(),name='course_record'),
    # 查看学习记录
    url(r'^study_record/(\d+)', customer.StudyRecordView.as_view(),name='study_record'),

]
