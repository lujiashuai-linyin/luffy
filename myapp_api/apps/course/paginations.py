from rest_framework.pagination import PageNumberPagination
class CoursePageNumberPagination(PageNumberPagination):
    """课程列表的分页器"""
    page_query_param = "page" # 地址上面代表页码的变量名，默认为page
    # page_size = 2  # 每一页显示的数据量，默认是10条， 没有设置页码，则不进行分页
    # # 允许客户端通过指定的参数名来设置每一页数据量的大小，默认是size
    page_size_query_param = "size"
    max_page_size = 20  # 限制每一页最大展示的数据量
