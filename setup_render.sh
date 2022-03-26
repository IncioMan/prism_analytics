mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
[theme]\n\
primaryColor=\"#202232\"\n\
backgroundColor=\"#202232\"\n\
secondaryBackgroundColor=\"#393a4f\"\n\
textColor=\"#FFFFFF\"\n\
font=\"sans serif\"\n\
\n\
" > ~/.streamlit/config.toml
pip install pipenv
pipenv install