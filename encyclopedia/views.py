from genericpath import exists
from django.forms import Textarea
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from markdown2 import Markdown
from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title", max_length=25, min_length=1)
    content = forms.CharField(label="Page Content", widget=Textarea)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    title = title.capitalize()
    entry = util.get_entry(title)

    if entry != None:
        content = Markdown().convert(entry)

    else:
        title = "Entry Not Found"
        content = "<p>The page you are looking for does not exist.</p>"

    return render(request, "encyclopedia/entry.html", {
        "title": title, "content": content
    })

def search(request):
    entries = []
    searchResults = []
    
    if request.method == "POST":
        searchTerm = request.POST.get("q")
        entries = util.list_entries()
        
        for entry in entries:
            if searchTerm.casefold() == entry.casefold():
                return HttpResponseRedirect(reverse("entry", kwargs={"title": str(searchTerm) }))
            elif searchTerm.casefold() in entry.casefold():
                searchResults.append(entry)
        return render(request, "encyclopedia/search.html", {
            "results": searchResults, "title": "Results"
        })

def new(request, title="", content="", edit=False):
    #Initializes form and sets default values for either edit or new
    form = NewEntryForm()
    form.title(default = title)
    form.content(default = content)
    
    #Allows for new function if this is an edit
    if title != "":
        edit=True

    #Execute the following if you're adding a new entry or editing an existing entry
    if request.method == "POST":
        form = form(request.POST)
        entryExists = False
        goToEntry = HttpResponseRedirect(reverse("entry", kwargs={"title": title}))

        if form.is_valid():

            #Grab title and content from form
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            #For edits:
            if edit == True:
                util.save_entry(title, content)
                return goToEntry

            #For new entries: Look for title in existing entries, if entry already exists, error will populate below submit button
            entries = util.list_entries()
            lower_entries = [entry.casefold() for entry in entries]
            
            if title.casefold() in lower_entries:
                    entryExists = True

            #If entry does not exist create page and redirect
            else:
                util.save_entry(title, content)
                return goToEntry

    #Renders initial page
    return render(request, "encyclopedia/new_page.html", {
        "form": NewEntryForm(), "entryExists": entryExists, "title":title
    })