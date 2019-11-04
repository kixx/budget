# budget

A vue.js + Flask PoC app inspired by [testdriven.io](https://testdriven.io/blog/) articles

## Getting started

Install dependencies and run backend

```sh
cd backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python3 app.py
```

Install dependencies and run frontend

```sh
cd frontend
npm install
echo "" > .env.development
npm run serve
```

Application is running on port 8080

## Built With

- vue.js
- bootstrap-vue
- vue2-datepicker
- flask
- flask-cors

## Authors

- Christian-Rolf Gruen

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details

## See also

- [Docker deployment](https://testdriven.io/blog/deploying-flask-to-heroku-with-docker-and-gitlab/)
- [vue.js / Flask development](https://testdriven.io/blog/developing-a-single-page-app-with-flask-and-vuejs/)
