git clone https://github.com/techno-yogi/django-portal.git
cd django-portal
python -m install virtualenv
python -m venv env
call .\env\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt