# READINGLIST (31 DEC 2022)
#### Video Demo:  [YOUTUBE](https://youtu.be/6F37pL4LeHM)
#### Description:
##### Overview:
This is a web app that lets you track books that you want to read. It includes a login feature for unique users. The app will track when you added the book to your reading list and to your completed books list. There is also a feature that suggests books from the New York Times hardcover fiction bestsellers list, from which you can also add to your reading list.

##### Design:
This app is meant to be a simple book list tracker. I chose not to use an API to check each user's books against some library database, simply because there are too many books to search through, and the API could either not be expansive enough to cover each book, since there are books that have multiple editions, or with the same titles. Because I do not have enough time to carefully craft something that could properly check a user's input for validity, I leave it up to the user to know which book they are trying to input.

For the New York Times recommendations, I kept it simple by using just the hardcover fiction bestsellers list. There are certainly many other lists, but I would not have had enough time to put them all in. If I were to continue working on this project, I would have a selection on the web app to allow a user to decide which list they want to see, and allow them to add whichever book to their reading list.

I designed the app to be simple and straightforward so that it can be quick to navigate through and easy to manage.

I did not include a way for the user to delete or edit their entry, but if I were to have the time, I would have wanted to include this as an additional feature.

##### Application.py:
This file is the main script for this project. It contains the features for each of the pages. There is a global variable that will access the New York Times Books API to collect data from their most recent hardcover fiction bestsellers list. The register, login, and logout functions are based on the functions from the latest problem set. Book list data is stored in the SQL database called "books", and is called for loading the lists on the Index, Read, and Recommends pages. The Add page allows the user to fill out a form of the title and author to add a book to their reading list. There is a Time variable that records the date the user adds books to each respective list.

##### books.db:
This is a SQLite3 database that contains all the data for each user's book lists.

##### helpers.py:
This is a file of helper functions, based on the functions from the latest problem set.

