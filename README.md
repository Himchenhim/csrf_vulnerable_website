<h1>It is a simple project, which demonstrates CSRF-vulnerabiity. </h1>

for running it, you must:
1) install all libraries, which are in the file 'requirements.txt'
2) install 'uvicorn' on your machine
3) run command 'uvicorn server:app --reload' and visit localhost, which is located on http://127.0.0.1:8000
4) use one of the passwords in file 'passwords.txt' ( it's better choose user 'Bob', because you will see how CSRF vulnerability exploiting)
5) open the file 'exploiting_csrf.html'
6) click on the link
7) Money are transferred from your account to Angelina's account
