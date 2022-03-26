pipenv run python ./scripts/amps.py
git add data/amps
git commit -m 'daily amps'
git push
pipenv run python data_fetcher.py
git add data/processed
git commit -m 'daily processed data'
git push