pipenv run python ./scripts/amps.py
pipenv run python data_fetcher.py
git add data/
git commit -m 'new data'
git push
git push heroku main