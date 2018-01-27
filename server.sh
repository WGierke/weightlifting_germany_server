date +"%T"
git fetch --all
git reset --hard origin/master
python process.py --notify
