import click
from app import create_app
from app.models import User
from app import db
from werkzeug.security import generate_password_hash
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = create_app()


@click.command()
@click.option('--username', prompt='请输入用户名', help='需要修改密码的用户')
@click.option('--new_password', prompt='请输入新密码', confirmation_prompt=True, help='新密码')
def change_password(username, new_password):
    """修改用户密码（命令行工具）"""
    with app.app_context():
        try:
            logging.info(f"开始修改用户 '{username}' 的密码")

            # 查找用户
            user = User.query.filter_by(username=username).first()
            if not user:
                click.echo(f"错误：用户 '{username}' 不存在", err=True)
                logging.warning(f"用户 '{username}' 不存在")
                return

            logging.info(f"找到用户 ID: {user.id}")

            # 验证新密码强度（可选）
            if len(new_password) < 6:
                click.echo("错误：密码长度至少需要6个字符", err=True)
                logging.warning("密码长度不足")
                return

            # 更新密码
            logging.info("正在生成密码哈希...")
            user.set_password(new_password)
            logging.info("密码哈希生成成功")

            # 提交事务
            logging.info("正在提交数据库事务...")
            db.session.commit()
            logging.info("数据库事务提交成功")

            click.echo(f"用户 '{username}' 的密码已更新！")

        except Exception as e:
            click.echo(f"发生错误：{str(e)}", err=True)
            logging.error(f"修改密码失败: {str(e)}")
            db.session.rollback()  # 回滚事务


if __name__ == '__main__':
    change_password()