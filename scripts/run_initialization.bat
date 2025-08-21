@echo off

echo 初始化角色和权限数据...

echo 确保已激活虚拟环境...
call .venv\Scripts\activate.bat

if %ERRORLEVEL% NEQ 0 (
    echo 激活虚拟环境失败，请手动激活后运行脚本。
    pause
    exit /b 1
)

python initialize_roles_permissions.py

if %ERRORLEVEL% EQU 0 (
    echo 初始化成功！
) else (
    echo 初始化失败，请查看错误信息。
)

pause