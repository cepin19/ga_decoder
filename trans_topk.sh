model_dir=/home/large/data/models/marian/encs.20210214/
marian=/servers/translation-servers/marian-dev/build/marian-decoder
/home/big_maggie/usr/nmt_scripts/factored-segmenter/bin/Release/netcoreapp3.1/linux-x64/publish//factored-segmenter encode  --model $model_dir/corp/encs.fsm > tmp_input
for i in {0..19}
do
$marian -m /home/large/data/models/marian/encs.20210214/model/model_transformer_big_mixed.npz.best-ce-mean-words.npz -b 1 -d 1 2  --mini-batch 32 --output-sampling topk 100  -v /home/large/data/models/marian/encs.20210214/corp/vocab.fsv  $model_dir/corp/vocab.fsv  --n-best -n 1 -i tmp_input  > tmp_sample_out_$i # | /home/big_maggie/usr/nmt_scripts/factored-segmenter/bin/Release/netcoreapp3.1/linux-x64/publish//factored-segmenter decode  --model /home/large/data/models/marian/encs.20210214/corp/encs.fsm  |  perl /home/big_maggie/usr/nmt_scripts/fix-cs-quotes-etc.pl  
done
paste -d '\n' tmp_sample_out_* > sampled_n20
rm tmp_sample_out_*
