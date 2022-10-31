from django.forms import Textarea
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from markdown2 import Markdown
from random import choice
from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title", max_length=25, min_length=1)
    content = forms.CharField(label="Page Content", widget=Textarea)

class EditEntryForm(forms.Form):
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


def new(request):
    #Initializes form
    form = NewEntryForm()
    entryExists = False
    
    #Execute the following after "submit"
    if request.method == "POST":
        form = NewEntryForm(request.POST)

        if form.is_valid():

            #Grab title and content from form
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]


            #Look for title in existing entries, if entry already exists, error will populate below submit button
            entries = util.list_entries()
            lower_entries = [entry.casefold() for entry in entries]
            
            if title.casefold() in lower_entries:
                    entryExists = True

            #If entry does not exist create page and redirect
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={"title": title}))

    #Renders initial page
    return render(request, "encyclopedia/new_page.html", {
        "form": NewEntryForm(), "entryExists": entryExists
    })

def edit(request, title):
    #Initializes values and sets default text area value to content of page
    error = False
    title = title.capitalize()
    content = util.get_entry(title)
    form = EditEntryForm(initial={"content": content})

    #If saving the edit, update the content and save the entry
    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("entry", kwargs={"title": title}))
        else:
            error = True
    
    return render(request, "encyclopedia/edit.html", {
        "form": form, "error": error, "title":title, "content":content
    })

def random(request):
    #Gets all available entries,
    #uses random function to choose one,
    #then redirects to entry url for the randomly chosen entry
    entries = util.list_entries()
    randomEntry = choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={"title": randomEntry}))