while true
do
	date +"%T"
	git fetch --all
	git reset --hard origin/master
	python process.py --notify
	sleep 3600 #60 minutes
done
