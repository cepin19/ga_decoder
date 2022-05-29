sed 's/|||/\t/g' $1 > $1.tabs
cut -f2 $1.tabs | /home/big_maggie/usr/nmt_scripts/factored-segmenter/bin/Release/netcoreapp3.1/linux-x64/publish//factored-segmenter decode  --model /home/large/data/models/marian/encs.20210214/corp/encs.fsm  > $1.trans
cut -f4 $1.tabs > $1.scores
