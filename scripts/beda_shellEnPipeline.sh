#!/usr/bin/env bash
#PBS -A C3SE102-13-5
#PBS -q beda
#PBS -N ENpipe_wikipedia_monolingual
#PBS -l nodes=1:ppn=8
#PBS -l walltime=12:00:00

#PBS -o wiki_output.stdout
#PBS -e wiki_output.stderr

# Load Java environment - subsequently what ever other dependencies for the application
module load java/1.6/0_24
module add java/1.6/0_24

#source /beda/sw/share/Bash/run-p-shells.sh
#for i in $(seq 0 3);
#do
#cat <<EOF
#	sh $PBS_O_WORKDIR/stanford_corenlp-on_wiki_data.sh "$PBS_O_WORKDIR/wiki-files-list-AB-rest.${i}" $TMPDIR
#	rpdcp $TMPDIR/* Documents/chalmers-work/corpus-preprocessing/corpora-resources/wikipedia/en-parsed_wikipedia-11Apr2014/stanford-corenlp-xml/AB/
#+++
#EOF
#done | run_in_parallel -n 4 -s '+++'
#cat $PBS_O_WORKDIR/commandsList.sh | run_in_parallel -n 8 -s '++++'
sh $PBS_O_WORKDIR/stanford_corenlp-on_wiki_data.sh "$PBS_O_WORKDIR/wiki-files-list-AB-rest.txt" "Documents/chalmers-work/corpus-preprocessing/corpora-resources/wikipedia/en-parsed_wikipedia-11Apr2014/stanford-corenlp-xml/AB/"
#rpdcp $TMPDIR/* Documents/chalmers-work/corpus-preprocessing/corpora-resources/wikipedia/en-parsed_wikipedia-11Apr2014/stanford-corenlp-xml/AB/
#pdcp $TMPDIR/* Documents/chalmers-work/corpus-preprocessing/corpora-resources/wikipedia/en-parsed_wikipedia-11Apr2014/stanford-corenlp-xml/AB/
