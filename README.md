# Live Demo
To see the app in action, go to [Library API Demo](https://teamgoat.herokuapp.com/)

# Background
I have an enormous collection of books; I'm also really particular about keeping them organized and discoverable. I want to be able to lend them to people for some period of time, know where they are and remind people to return them to me on time. I need a way to help me find books by author, subject, time period and even be able to possibly add some personal notes about the book.

# Use Cases
As a user, I want to be able to:

* Add, remove, and update books in my library
* Find books by a particular author
* Find all books published in a given date range
* Find books on a certain subject or genre (i.e scientific books, sci-fi, horror, reference)
* Group books together into lists (i.e "my favorite sci-fi books of 2016")
* Combine any of the above to create a more complex search query (i.e all horror books published by Stephen Hawking between 1815 and 1820)
* Mark a book as "loaned out" to an individual
* Remind the individual I loaned my book to that they need to return it by some date I've chosen
* Add, remove or update notes about a particular book for later reference
* See which books are loaned out and to whom; also see whether they have returned them on time or not

# Tools and Technologies
* Python
* Flask (simple web framework)
* PostgreSQL (for data storage)
* Heroku (for deployments)
* Github (for source control)
* Swagger (for API documentation)
* JSON (for API interoperability)
