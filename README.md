## 项目简介
本项目基于 Django 框架，实现了工单信息的管理与审批流程，并支持根据预设的 Word 模板自动填充工单信息，生成对应的 PDF 文件供下载。  
主要面向高空作业、明火作业等多种作业类型的工单审批与归档。

## 功能说明
- 支持多种工单类型选择，如高空作业、明火作业等。
- 动态填写工单内容，包括作业时间、地点、负责人、作业人员、安全措施等。
- 支持多审批人顺序审批流程（需另行实现审批流程控制）。
- 自动从 Word 模板读取固定格式内容，填充工单数据。
- 生成填充完成的 PDF 文件，供用户下载存档。

## 技术栈
- Python 3.11.4
- Django 框架
- python-docx 用于 Word 模板读取与修改
- docx2pdf (或其他工具) 用于将 Word 转换为 PDF
- ReportLab（可选，用于直接PDF绘制）
- SQLite（或其他数据库）

## 注意事项
  - 在ticket_pdf函数中的"template_path"这个是word文件的路径，需要自己进行设置
  - 该项目一共有三个文件夹，accounts（管理用户信息）、tickets（工单流程）、workorder_system（主文件夹）
  - 如果需要实现多人审批，需要修改accounts文件夹下的模型，需要进行表的设计，还需要修改tickets文件夹下的模型，还需要对各自的forms文件进行修改

## 使用说明

### 1. 环境准备
- 安装依赖
```bash
pip install django python-docx docx2pdf
