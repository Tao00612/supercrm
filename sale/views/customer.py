from django.shortcuts import render,redirect,HttpResponse
from sale import models
from sale.utils.page import MyPagenation
from django.db.models import Q
from django.urls import reverse
from django.views import View
from sale.myforms import CustomerForm,ConsultRecordForm,EnrollForm
from django.db import transaction
from django import forms
from django.forms.models import modelformset_factory


# 首页
def home(request):

    return render(request, 'saleshtml/home.html')


# 公户私户信息展示
class CustomersView(View):
     
    def get(self,request):
        current_request_path = request.path
        # 公户
        if current_request_path == reverse('customers'):
            tag = '1'
            customer_list = models.Customer.objects.filter(consultant__isnull=True)
        else:
            # 私户
            tag = '2'
            user_obj = request.user_obj
            customer_list = models.Customer.objects.filter(consultant=user_obj)
        get_data = request.GET.copy()  # get数据
        search_field = request.GET.get('search_field')  # 查询字段
        kew_word = request.GET.get('kw')  # 查询关键字
        page_num = request.GET.get('page')  # 当前页数
        if kew_word:
            kew_word = kew_word.strip()
            q_obj = Q()
            q_obj.children.append((search_field, kew_word))
            customer_list = customer_list.filter(q_obj)
        else:
            customer_list = customer_list
        customers_count = customer_list.count()  # 总数据
        per_page_num = 10  # 每页生成多少条
        page_num_show = 7  # 生成可点击页面数
        base_url = request.path  # 访问的路径
        page_obj = MyPagenation(page_num, customers_count, base_url, get_data, per_page_num, page_num_show)
        page_html = page_obj.page_hmtl()
        customers_obj = customer_list.reverse()[page_obj.start_data_num:page_obj.end_data_num]
        return render(request, 'saleshtml/customers.html', {'customers_obj': customers_obj, 'page_html': page_html, 'tag':tag})

    def post(self,request):
        action = request.POST.get('action')
        cids = request.POST.getlist('cids')
        if hasattr(self,action):
            ret = getattr(self,action)(request,cids)
            if ret:
                return ret

            return redirect(request.path)

    # 公转私
    def reverse_gs(self,request,cids):

        with transaction.atomic():
            customers = models.Customer.objects.filter(pk__in=cids,consultant__isnull=True).select_for_update()
        if customers.count() != len(cids):
            return HttpResponse('回家练手速吧！！')
        customers.update(consultant_id=request.session.get('user_id'))

    # 私转公
    def reverse_sg(self,request,cids):
        customers = models.Customer.objects.filter(pk__in=cids, consultant=request.user_obj)
        customers.update(consultant_id=None)


# 添加编辑客户
def add_edit_customer(request,cid=None):
    """
    添加客户和编辑客户
    :param request:
    :param cid:   客户记录id
    :return:
    """
    label = '编辑客户' if cid else '添加客户'
    customer_obj = models.Customer.objects.filter(pk=cid).first()
    if request.method == 'GET':
        customer_form = CustomerForm(instance=customer_obj)
        return render(request, 'saleshtml/edit_customer.html', {'customer_form':customer_form, 'label':label})

    else:
        next_url = request.GET.get('next')
        customer_form = CustomerForm(request.POST,instance=customer_obj)
        if customer_form.is_valid():
            customer_form.save()
            return redirect(next_url)
        else:
            return render(request, 'saleshtml/edit_customer.html', {'customer_form':customer_form, 'label':label})


# 删除客户
def del_customer(request,cid):
    models.Customer.objects.get(pk=cid).delete()
    return redirect('customers')


# 跟进记录管理
class ConsultRecordView(View):

    def get(self, request):
        # 当前登录用户的未删除的客户跟进记录
        cid = request.GET.get('cid')
        # 如果存在cid，那么找的是单个客户的跟进记录
        if cid:
            consult_list = models.ConsultRecord.objects.filter(consultant=request.user_obj, delete_status=False,customer_id=cid).order_by('-date')
        else:
            consult_list = models.ConsultRecord.objects.filter(consultant=request.user_obj,delete_status=False).order_by('-date')
        # 分页和搜索
        get_data = request.GET.copy()  # 将request.GET对象改成可修改的
        page_num = request.GET.get('page')  # 当前页码
        search_field = request.GET.get('search_field')  # 选择查询的字段,name
        kw = request.GET.get('kw')  # 查询关键字  #思宇
        if kw:
            kw = kw.strip()
            q_obj = Q()
            q_obj.children.append((search_field, kw))
            consult_list = consult_list.filter(q_obj)
        else:
            consult_list = consult_list
        base_url = request.path  # 访问的路径
        consult_count = consult_list.count()
        per_page_num = 10  # 每页显示多少条数据
        page_num_show = 7  # 显示的页码数
        page_obj = MyPagenation(page_num, consult_count, base_url, get_data, per_page_num, page_num_show, )
        page_html = page_obj.page_hmtl()
        consult_objs = consult_list.reverse()[page_obj.start_data_num:page_obj.end_data_num]
        return render(request, 'saleshtml/consultrecord.html',{'consult_list': consult_objs, 'page_html': page_html})

    def post(self,request):
        action = request.POST.get('action')
        cids = request.POST.getlist('cids')
        if hasattr(self,action):
            consults = models.ConsultRecord.objects.filter(pk__in=cids)
            getattr(self,action)(request,consults)
            return redirect(request.path)

    # 公转私
    def bulk_delete(self,request,consults):
        consults.update(delete_status=True)


class AddEditConsultView(View):

    def get(self,request,cid=None):

        """
            添加客户和编辑客户
            :param request:
            :param cid:   客户记录id
            :return:
            """
        label = '编辑跟进记录' if cid else '添加跟进记录'
        consult_obj = models.ConsultRecord.objects.filter(pk=cid).first()

        if request.method == 'GET':
            consult_form = ConsultRecordForm(request,instance=consult_obj)
            return render(request, 'saleshtml/add_edit_consult.html', {'consult_form': consult_form, 'label': label})

    def post(self,request,cid=None):
        consult_obj = models.ConsultRecord.objects.filter(pk=cid).first()
        next_url = request.GET.get('next')
        if not next_url:
            next_url = reverse('consult_record')
        consult_form = ConsultRecordForm(request,request.POST, instance=consult_obj)
        if consult_form.is_valid():
            consult_form.save()
            return redirect(next_url)
        else:
            return render(request, 'saleshtml/edit_customer.html', {'consult_form': consult_form,})


class EnrollmentView(View):
    def get(self,request):

        enrolls = models.Enrollment.objects.filter(customer__consultant=request.user_obj,delete_status=False)
        print(enrolls)
        return render(request,'saleshtml/enrollments.html',{'enrolls':enrolls})


class AddEditEnrollView(View):

    def get(self,request,cid=None):

        label = '编辑报名记录' if cid else '添加报名记录'
        enroll_obj = models.Enrollment.objects.filter(pk=cid).first()

        if request.method == 'GET':
            enroll_form = EnrollForm(request,instance=enroll_obj)
            return render(request, 'saleshtml/add_edit_enroll.html', {'enroll_form': enroll_form, 'label': label})

    def post(self,request,cid=None):
        enroll_obj = models.Enrollment.objects.filter(pk=cid).first()
        next_url = request.GET.get('next')
        if not next_url:
            next_url = reverse('consult_record')
        enroll_form = EnrollForm(request,request.POST, instance=enroll_obj)
        if enroll_form.is_valid():
            enroll_form.save()

            return redirect(next_url)
        else:
            return render(request, 'saleshtml/edit_customer.html', {'enroll_form': enroll_form,})


# 课程记录
class CourseRecordView(View):

    def get(self,request):
        course_obj = models.CourseRecord.objects.all()
        return render(request,'saleshtml/courserecord.html',{'course_obj':course_obj})

    def post(self,request):
        action = request.POST.get('action')
        cids = request.POST.getlist('cids')
        if hasattr(self,action):
            getattr(self,action)(request,cids)
        return HttpResponse('ok')

    def bulk_create_srecord(self,request,cids):
        # 批量生成
        l1= []
        for cid in cids:
            course_record_obj = models.CourseRecord.objects.filter(pk=cid).first()
            students = course_record_obj.re_class.customer_set.filter(status='studying')
            for i in students:
                obj = models.StudyRecord(
                    course_record_id=cid,
                    student=i
                )
                l1.append(obj)
            models.StudyRecord.objects.bulk_create(l1)


class StudyRecordModelForm(forms.ModelForm):

    class Meta:
        model = models.StudyRecord
        fields = "__all__"


class StudyRecordView(View):

    def get(self, request, course_record_id):
        print(course_record_id)
        formset_cls = modelformset_factory(model=models.StudyRecord, form=StudyRecordModelForm, extra=0)
        study_records = models.StudyRecord.objects.filter(course_record_id=course_record_id)
        formset = formset_cls(queryset=study_records)
        # formset = formset
        # queryset = models.StudyRecord.objects.filter(course_record_id=course_record_id)

        return render(request, 'saleshtml/studyrecord.html', {'formset': formset})

    def post(self, request, course_record_id):
        formset_cls = modelformset_factory(model=models.StudyRecord, form=StudyRecordModelForm, extra=0)
        formset = formset_cls(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect(request.path)
        else:
            return render(request, 'saleshtml/studyrecord.html', {'formset': formset})


