import click
from app import create_app
from app.models import User
from app import db
from werkzeug.security import generate_password_hash

app = create_app()


@click.command()
@click.option('--username', prompt='请输入用户名', help='用户登录名')
@click.option('--password', prompt='请输入密码', help='用户密码')
@click.option('--email', prompt='请输入邮箱', help='用户邮箱')
@click.option('--role', default='user', help='用户角色（默认: user）')
def register_user(username, password, email, role):
    """创建新用户（命令行工具）"""
    with app.app_context():
        try:
            # 检查用户名是否已存在
            if User.query.filter_by(username=username).first():
                click.echo(f"错误：用户名 '{username}' 已存在", err=True)
                return

            # 检查邮箱是否已存在
            if User.query.filter_by(email=email).first():
                click.echo(f"错误：邮箱 '{email}' 已被注册", err=True)
                return

            # 验证密码长度
            if len(password) < 6:
                click.echo("错误：密码长度至少需要6个字符", err=True)
                return

            # 创建新用户
            new_user = User(
                username=username,
                password=generate_password_hash(password),
                email=email,
                role=role,
                status=0
            )

            db.session.add(new_user)
            db.session.commit()

            click.echo(f"用户 '{username}' 创建成功！")

        except Exception as e:
            click.echo(f"发生错误：{str(e)}", err=True)
            db.session.rollback()  # 回滚事务


if __name__ == '__main__':
    register_user()