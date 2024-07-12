@echo off
REM 激活虚拟环境
call venv\Scripts\activate

REM 运行Python脚本
python batch_remove_metadata.py input ouput
REM 退出虚拟环境
deactivate