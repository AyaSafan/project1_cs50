#project1_cs50

Web Programming with Python and JavaScript

First page of my website is an intro page that redirects to either a login or sign up page.

Users are be able to register providing a unique username and password. Users, once registered, are be able to log in website with their username and password.

Loged in Users are directed to a search page to search for desired books. A side dropdown icon provides a log out option, an option to view user's rated and reviewed books, and an option to go to back to search page from any other page. 

Search: Users are be able to type in the ISBN number of a book, the title of a book, or the author of a book. 
After performing the search, the website displays a list of possible matching results, or error message if there were no matches.
If the user typed in only part of a title, ISBN, or author name, the search page finds matches for those as well!

Book Page: When users click on a book from the results of the search page, they are be taken to a book page, with details about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book on your website.

Review Submission: On the book page, users are be able to  give rating on a scale of 1 to 5, as well as a text component to the review where the user can write their opinion about a book. 
Users are not be able to submit multiple reviews for the same book. However, they can edit and delete reviews.

API Access: If users click (Our Reviews json) button or make a GET request to the website’s /api/<isbn> route, where <isbn> is an ISBN number, the website returns a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score.
