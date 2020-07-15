
import re
from django.utils.safestring import mark_safe


class MyPagenation():

    def __init__(self,page_num,total_count,base_url,get_data=None,per_page_num=10,page_num_show=5):
        """
        :param page_num:   当前页
        :param total_count:  数据总数量
        :param base_url:   基本路径
        :param get_data:   QueryDict对象
        :param per_page_num:  每页显示多少条数据
        :param page_num_show:   显示的页码数
        """

        self.get_data = get_data  # 搜索条件
        self.per_page_num = per_page_num  # 每页显示10条
        # 页面生成页码的数量
        self.page_num_show = page_num_show  # 7      4 5 6 7 8
        self.base_url = base_url  # 7      4 5 6 7 8
        try:
            page_num = int(page_num)
        except Exception:
            page_num = 1
        self.page_num = page_num

        shang, yu = divmod(total_count, self.per_page_num)  # shang:商    yu：余数
        # 总页码数
        if yu:
            page_num_count = shang + 1
        else:
            page_num_count = shang
        self.page_num_count = page_num_count
        if page_num <= 0:
            page_num = 1
        elif page_num > page_num_count:
            page_num = page_num_count

        # 3 4 5 6 7    4 5 6 7 8 9 10
        half_show = self.page_num_show // 2  # 2
        if page_num - half_show <= 0:
            start_page_num = 1
            end_page_num = self.page_num_show + 1  # 9

        elif page_num + half_show > page_num_count:
            start_page_num = page_num_count - self.page_num_show + 1  # 26 - 5 = 21
            end_page_num = page_num_count + 1  # 27  [21,22,23,24,25,26]

        else:
            start_page_num = page_num - half_show  # 4  1
            end_page_num = page_num + half_show + 1  # 9  6

        # 如果总数据的页数小于设定的展示页码总数，那么就显示总数据的页数
        if page_num_count < self.page_num_show:
            start_page_num = 1
            end_page_num = page_num_count + 1

        self.start_page_num = start_page_num
        self.end_page_num = end_page_num

    @property
    def start_data_num(self):
        return (self.page_num - 1) * self.per_page_num

    @property
    def end_data_num(self):
        return self.page_num * self.per_page_num

    def page_hmtl(self):
        page_num_range = range(self.start_page_num, self.end_page_num)
        page_html = ''
        page_pre_html = '<nav aria-label="Page navigation"><ul class="pagination">'
        page_html += page_pre_html
        #首页页码标签
        self.get_data['page'] = 1
        first_page_html = '<li><a href="{1}?{0}" aria-label="Previous"><span aria-hidden="true">首页</span></a></li>'.format(self.get_data.urlencode(), self.base_url)
        page_html += first_page_html
        if self.page_num <= 1:
            pre_page = '<li class="disabled"><a href="javascript:void(0)" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(self.page_num - 1)
        else:
            self.get_data['page'] = self.page_num - 1
            pre_page = '<li><a href="{1}?{0}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(self.get_data.urlencode(),self.base_url)

        page_html += pre_page
        for i in page_num_range:
            if i == self.page_num:
                self.get_data['page'] = i
                page_html += '<li class="active"><a href="{1}?{2}">{0}</a></li>'.format(i, self.base_url, self.get_data.urlencode())
                # page_html += '<li class="active"><a href="{1}?page={0}">{0}</a></li>'.format(i,self.base_url)
            else:
                self.get_data['page'] = i
                page_html += '<li><a href="{1}?{2}">{0}</a></li>'.format(i, self.base_url,self.get_data.urlencode()) #search_field=qq__contains&kw=111&page=2
                # page_html += '<li><a href="{1}?page={0}">{0}</a></li>'.format(i, self.base_url) #search_field=qq__contains&kw=111&page=2
        if self.page_num >= self.page_num_count:
            page_next_html = '<li class="disabled"><a href="javascript:void(0)" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'.format(self.page_num + 1)
        else:
            self.get_data['page'] = self.page_num + 1
            page_next_html = '<li><a href="{1}?{0}" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'.format(self.get_data.urlencode(),self.base_url)
        page_html += page_next_html
        self.get_data['page'] = self.page_num_count
        last_page_html = '<li><a href="{1}?{0}" aria-label="Previous"><span aria-hidden="true">尾页</span></a></li>'.format(self.get_data.urlencode(), self.base_url)
        page_html += last_page_html
        end_html = '</ul></nav>'
        page_html += end_html

        return mark_safe(page_html)
