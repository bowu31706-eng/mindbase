@echo off
chcp 65001 > nul
cd /d "D:\求职全过程\MindBase\backend"
C:\Users\86195\AppData\Local\Python\pythoncore-3.14-64\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
