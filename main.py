import tkinter as tk
from tkinter import ttk  # 导入内部包
from tkinter import filedialog, messagebox
import webbrowser

from spider_main import SpiderMain

class MainWindows(tk.Tk):
    def __init__(self):
        super().__init__()  # 初始化基类
        self.title("Dhgate数据采集")
        try:
            self.iconbitmap('dhgate.ico')
        except:
            pass  # Ignore if icon file is not found
        self.resizable(False, False)  # 禁止窗口放大
        self.ini_ui()
        self.spider = SpiderMain()
        self.bind("<Configure>", self.on_resize)  # Bind the resize event
        self.images = {}  # Store images to prevent garbage collection

    def ini_ui(self):
        # 设置顶部区域
        self.top_frame = tk.Frame(width=800, height=200, bg='#303030')
        self.bottom_frame = tk.Frame(width=800, height=400, bg='#303030')

        # 定义顶部区域
        self.lb1 = tk.Label(self.top_frame,
                            text='输入关键词',
                            font=('Hack', 15, 'bold'),
                            bg='#303030',
                            fg='white')
        self.lb2 = tk.Label(self.top_frame,
                            text='页数',
                            font=('Hack', 15, 'bold'),
                            bg='#303030',
                            fg='white')
        self.keyword = tk.Entry(self.top_frame)
        self.num = tk.Spinbox(self.top_frame, from_=1, to=100, width=5)  # Change the Entry widget to a Spinbox for numeric input
        self.lb3 = tk.Label(self.top_frame,
                            text='',
                            font=('Hack', 15, 'bold'),
                            bg='#303030',
                            fg='white')
        self.btn1 = tk.Button(self.top_frame, text='开始', command=self.scrapy)
        self.btn2 = tk.Button(self.top_frame,
                              text='清空',
                              command=self.clear_entry_value)
        self.btn3 = tk.Button(self.top_frame,
                              text='导出Excel',
                              command=self.save_data)

        self.lb1.grid(row=0, column=0, padx=10, pady=10)
        self.keyword.grid(row=0, column=1, padx=10, pady=10)
        self.lb2.grid(row=1, column=0, padx=10, pady=10)
        self.num.grid(row=1, column=1, padx=10, pady=10)
        self.lb3.grid(row=3, column=0, columnspan=5)
        self.btn1.grid(row=0, column=5)
        self.btn2.grid(row=1, column=5)
        self.btn3.grid(row=0, column=6)

        # 定义底部区域
        self.tree = ttk.Treeview(self.bottom_frame,
                                 show="headings",
                                 height=20,
                                 columns=("编号", "列表链接", "标题", "产品链接", "最低价",
                                          "最高价", "起订量", "销量", "好评数", "卖家",
                                          "店铺链接"))  # 表格
        self.vbar = ttk.Scrollbar(self.bottom_frame,
                                  orient='vertical',
                                  command=self.tree.yview)
        # 定义树形结构与滚动条
        self.tree.configure(yscrollcommand=self.vbar.set)

        for head in self.tree['columns']:
            self.tree.heading(head, text=head)  # 显示表头

        self.tree.grid(row=0, column=0, sticky='nsew', padx=(10, 0))
        self.vbar.grid(row=0, column=1, sticky='ns')
        self.bottom_frame.grid_rowconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_item_double_click)

        # 整体布局
        self.top_frame.grid(row=0, column=0, sticky='ew')
        self.bottom_frame.grid(row=1, column=0, sticky='nsew')
        self.top_frame.grid_propagate(0)
        self.bottom_frame.grid_propagate(0)

    def on_resize(self, event):
        # Adjust column widths based on window size
        total_width = self.bottom_frame.winfo_width() - 20  # Subtract some margin
        num_columns = len(self.tree['columns'])
        column_width = total_width // num_columns

        for head in self.tree['columns']:
            self.tree.column(head, width=column_width)

    def scrapy(self):
        self.clear_result()
        keyword = self.keyword.get()
        page_num = self.num.get()
        
        if keyword == '':
            messagebox.showinfo(message="关键字不能为空")
            return
        if page_num == '':
            messagebox.showinfo(message="页数不能为空") 
            return
        
        obj_spider = self.spider
        total_pages = int(page_num)
        
        for current_page in range(total_pages):
            self.lb3.config(text=f"正在采集{keyword} - 第{current_page + 1}/{total_pages}页")
            self.update()  # 更新GUI显示
            
        datas = obj_spider.craw(keyword, page_num)
        self.lb3.config(text=f"采集完毕 - 共获取{len(datas)}条数据")
        self.show_result(datas)

    # 清空文本输入框的值
    def clear_entry_value(self):
        self.keyword.delete(0, tk.END)
        self.num.delete(0, tk.END)
        self.keyword.focus_set()  # 对第一个文本输入框设置光标焦点
        self.clear_result()

    def clear_result(self):
        child_item = self.tree.get_children()
        for item in child_item:
            self.tree.delete(item)

    def show_result(self, datas):
        for i, data in enumerate(datas):
            # Remove image loading and processing
            # Insert data into the table without image
            self.tree.insert("",
                             i,
                             text=f"line{i+1}",
                             values=(i + 1, data['page_url'], data['title'], data['product_url'],
                                     data['min_price'], data['max_price'], data['min_order'],
                                     data['order'], data['feedback'], data['seller'],
                                     data['store_url']))

    def save_data(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:  # Check if a path was selected
            out = self.spider.outputer
            out.to_csv(path)

    def on_item_double_click(self, event):
        # Get selected item
        item = self.tree.selection()[0]
        # Get product link from the selected item
        product_link = self.tree.item(item, "values")[3]  # Assuming "产品链接" is the 4th column
        # Open the link in a web browser
        webbrowser.open(product_link)


if __name__ == '__main__':
    app = MainWindows()
    app.mainloop()
