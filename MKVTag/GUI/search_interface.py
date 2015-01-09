__author__ = 'Odd'

import tkinter as tk
import OddTools.modulelist
from OddTools.GUI import Listbox
from OddTools.GUI import tkSimpleDialog
import Scrapers.themoviedb
import requests
from PIL import ImageTk
from PIL import Image
import io


class _SearchDialog(tkSimpleDialog.Dialog):
    def __init__(self, parent, title="Scraper search", module=None, return_data=False):
        self.scraper = module
        self.return_data = return_data
        tkSimpleDialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        search_frame = tk.Frame(self)
        entry = self.search_text = tk.Entry(search_frame)
        entry.grid(row=0, column=0)
        search_button = tk.Button(search_frame, text="Search", command=self.start_search)
        search_button.grid(row=0, column=1)
        if self.scraper is None:
            module_list = OddTools.modulelist.get_modulenames(Scrapers)
            self.scraperString = tk.StringVar()
            self.scraperString.set(module_list[0])
            options = tk.OptionMenu(search_frame, self.scraperString, *module_list)
            options.grid(row=0, column=2)
        search_frame.pack()
        self.results_frame = self.results_frame = tk.Frame(self)
        self.results_frame.pack()

    def start_search(self):
        if self.scraper is None:
            self.scraper = __import__("Scrapers.%s" % self.scraperString.get(), fromlist="Scrapers")
            print(self.scraper.__file__)
        result = self.resultlist = self.scraper.search(self.search_text.get())
        items = list()
        image_list = list()
        for item in result:
            #TODO just in time download of image and caching
            items.append(item['title'])
            if "http" in item['thumbnail']:
                request = requests.get(item['thumbnail'])
                pilimg = Image.open(io.BytesIO(request.content))
                image_list.append(ImageTk.PhotoImage(pilimg))
            else:
                image_list.append(None)

        listbox = self.listbox = Listbox.Listbox(items, self.results_frame, orderable=False)
        listbox.add_data(items)
        listbox.grid(row=0, column=0, sticky=tk.N)
        imagebox = tk.Frame(self.results_frame)
        imagebox.grid(row=0,column=1)

        def show_image(event):
            if len(imagebox.winfo_children()) > 0:
                imagebox.winfo_children()[0].destroy()
            if image_list[listbox.get_selected()[0]] is not None:
                label = tk.Label(imagebox, image=image_list[listbox.get_selected()[0]])
                label.pack()
            else:
                label = tk.Label(imagebox, text="No image")
                label.pack()

        self.listbox.add_onclick(show_image)

    def apply(self):
        selected = self.listbox.get_selected()
        for item in self.resultlist:
            if item['title'] == self.listbox.get_items()[selected[0]]:
                self.result = item['id']
                if self.return_data:
                    self.result = self.scraper.get_info(self.result)

    def validate(self):
        if self.listbox is not None and len(self.listbox.get_selected()) > 0:
            return 1
        else:
            return 0


def search_title(module=None, parent=None, return_data=False):
    if parent is None:
        parent = tk.Tk()
    app = _SearchDialog(parent, module=module, return_data=return_data)
    return app.result

if __name__ == "__main__":
    print(search_title())