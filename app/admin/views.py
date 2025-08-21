from flask_admin.contrib.sqla import ModelView
from app.models import User, Article
from app import admin

# 注册 User 模型到管理页面
class UserAdminView(ModelView):
    column_list = ('id', 'username', 'email', 'created_at')  # 管理页面显示的列
    form_columns = ('username', 'email', 'password')  # 编辑时显示的字段

admin.add_view(UserAdminView(User, name='User Management'))

# 注册 Article 模型到管理页面
class ArticleAdminView(ModelView):
    column_list = ('id', 'title', 'author', 'created_at')
    form_columns = ('title', 'content', 'author')

admin.add_view(ArticleAdminView(Article, name='Article Management'))