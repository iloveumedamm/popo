echo "Cloning Repo, Please Wait..."
git clone -b master https://github.com/kevinnadar22/Droplink-Movie-Finder-Bot.git /Droplink-Movie-Finder-Bot
cd /Droplink-Movie-Finder-Bot
echo "Installing Requirements..."
pip3 install -U -r requirements.txt
echo "Starting Bot, Please Wait..."
python3 bot.py
