# Connect4 GUI
## PS. You're welcome.

# Requirements
* npm (https://www.npmjs.com/get-npm)
* pipenv (`brew install pipenv`)

# Installation
You should be able to go to naviate to connect4/ and run `pipenv install`, and be good to go. I might have missed a package, in which case it'll tell you in the next step and you should just install it with pip or whatever.

There's definitely a correct way to share frontend stuff on Github, but that is not this. If you start getting random weird npm errors like
```bash
npm ERR! This is probably not a problem with npm. There is likely additional logging output above.

npm ERR! A complete log of this run can be found in:
npm ERR!    
```
then delete `connect4/frontend/package-lock.json`, navigate to `frontend`, and run `npm install` again.

# Usage
To get going, navigate to connect4/ and run `pipenv shell`, then run `python manage.py runserver`. In your browser, navigate to "https://localhost:8000" and make sure you see an API. Then, open a new terminal and navigate to `connect4/frontend`. Run `npm start`, and a window should open in your browser going to "https://localhost:3000".

To insert your own fancy machine learning model, go to `connect4/ai/views.py`. The function `get_move` stores an array with 0s, -1s, and 1s as a board. You should output the desired move (an integer between 0 and 7, noninclusive).

