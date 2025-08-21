from app import create_app
import os

# 创建应用实例
app = create_app()

# 将路由信息写入文件
output_file = 'routes_list.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("注册的路由:\n\n")
    for rule in app.url_map.iter_rules():
        methods = ', '.join(sorted(rule.methods))
        route_info = f"{rule.endpoint}: {rule.rule} ({methods})\n"
        f.write(route_info)
        print(route_info, end='')
    print(f"\n路由信息已保存到 {os.path.abspath(output_file)}")