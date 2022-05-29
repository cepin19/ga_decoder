marian=/servers/translation-servers/marian-dev/build/marian-decoder

cat news20.csen.cs.snt | /home/big_maggie/usr/nmt_scripts/factored-segmenter/bin/Release/netcoreapp3.1/linux-x64/publish//factored-segmenter encode  --model ../encz_ner_tests/corp/encs2.fsm  | $marian -m ../encz_ner_tests/czen_models/model_transformer_czen.base.fs2.block_40k.npz.best-translation.npz -d 1 2  --mini-batch 32 -b 20  -v ../encz_ner_tests//corp/vocab2.fsv  ../encz_ner_tests//corp/vocab2.fsv -n 1 | /home/big_maggie/usr/nmt_scripts/factored-segmenter/bin/Release/netcoreapp3.1/linux-x64/publish//factored-segmenter decode  --model ../encz_ner_tests/corp/encs2.fsm  |  perl /home/big_maggie/usr/nmt_scripts/fix-cs-quotes-etc.pl   > news20.csen.beam5.trans

cat news20.csen.cs.snt | /home/big_maggie/usr/nmt_scripts/factored-segmenter/bin/Release/netcoreapp3.1/linux-x64/publish//factored-segmenter encode  --model ../encz_ner_tests/corp/encs2.fsm  | $marian -m ../encz_ner_tests/czen_models/model_transformer_czen.base.fs2.block_40k.npz.best-translation.npz -d 1 2  --mini-batch 32 -b 20  -v ../encz_ner_tests//corp/vocab2.fsv  ../encz_ner_tests//corp/vocab2.fsv --n-best -n 1   > news20.csen.beam20.nbest


sed 's/|||/\t/g' news20.csen.beam20.nbest | cut -f2  | /home/big_maggie/usr/nmt_scripts/factored-segmenter/bin/Release/netcoreapp3.1/linux-x64/publish//factored-segmenter decode  --model ../encz_ner_tests/corp/encs2.fsm > news20.csen.beam20.trans

awk -v NUM=20 'NR % NUM == 1' news20.csen.beam20.trans > news20.csen.beam20.trans.first_prob





for i in {0..19}
do
/home/big_maggie/usr/nmt_scripts/factored-segmenter/bin/Release/netcoreapp3.1/linux-x64/publish//factored-segmenter encode  --model ../encz_ner_tests/corp/encs2.fsm  | $marian -m ../encz_ner_tests/czen_models/model_transformer_czen.base.fs2.block_40k.npz.best-translation.npz -d 1 2  --mini-batch 32 -b 1 --output-sampling full  -v ../encz_ner_tests//corp/vocab2.fsv  ../encz_ner_tests//corp/vocab2.fsv --n-best -n 1   > tmp_sample_out_$i # | /home/big_maggie/usr/nmt_scripts/factored-segmenter/bin/Release/netcoreapp3.1/linux-x64/publish//factored-segmenter decode  --model /home/large/data/models/marian/encs.20210214/corp/encs.fsm  |  perl /home/big_maggie/usr/nmt_scripts/fix-cs-quotes-etc.pl  
done
paste -d '\n' tmp_sample_out_* > news20.csen.sampled20.trans.nbest
rm tmp_sample_out_*

sed 's/|||/\t/g' news20.csen.sampled20.nbest | cut -f2  | /home/big_maggie/usr/nmt_scripts/factored-segmenter/bin/Release/netcoreapp3.1/linux-x64/publish//factored-segmenter decode  --model ../encz_ner_tests/corp/encs2.fsm > news20.csen.sampled20.trans



comet-mbr -s news20.csen.cs.snt -t news20.csen.beam20.trans  --num_samples 20 -o  news20.csen.beam20.mbr_reranked
comet-mbr -s news20.csen.cs.snt -t news20.csen.sampled20.trans  --num_samples 20 -o  news20.csen.sampled20.mbr_reranked

python simple_rerank.py news20.csen.cs.snt news20.csen.beam20.trans  news20.csen.en.snt > news20.csen.beam20.ref_reranked
python simple_rerank.py news20.csen.cs.snt news20.csen.sampled20.trans  news20.csen.en.snt > news20.csen.sampled20.ref_reranked


for f in news20.csen.beam5.trans news20.csen.beam20.trans.first_prob  news20.csen.beam20.mbr_reranked news20.csen.beam20.ref_reranked  news20.csen.sampled20.mbr_reranked news20.csen.sampled20.ref_reranked
do
comet-score -s news20.csen.cs.snt -t news20.csen.beam5.trans  -r news20.csen.en.snt > $f.comet
comet-score -s news20.csen.cs.snt -t news20.csen.beam5.trans  -r news20.csen.en.snt --model wmt21-cometinho-da > $f.comet_cometinho
comet-score -s news20.csen.cs.snt -t news20.csen.beam5.trans  -r news20.csen.en.snt --model wmt20-comet-qe-da-v2  > $f.comet_qe_v2


done


# | /home/big_maggie/usr/nmt_scripts/factored-segmenter/bin/Release/netcoreapp3.1/linux-x64/publish//factored-segmenter decode  --model /home/large/data/models/marian/encs.20210214/corp/encs.fsm  |  perl /home/big_maggie/usr/nmt_scripts/fix-cs-quotes-etc.pl  
 
