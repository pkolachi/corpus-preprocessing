
# Script to read in Catib dependency treebank and produce a PCFG

use strict;

# Todo: print out rules by LHS symbol.
# Todo: print out bigram adjunction rules.

# Arguments

die "Usage: perl extract-grammar-from-dep-onefile.perl <catibFile> (<lexspec?> <maxLexSpec>)\n" if (($#ARGV != 0) && ($#ARGV !=2));

my $depFile = shift; # a single file
my $lexFile = 0;      # should there be lexical specialization?
$lexFile = shift;
my $lexFileMax = shift;  # how many words to specialize?


# Should digits in lecial specialization be replaced by 8, and the decimal point by c?
my $DIGITCONVERSION = 1;  


my $SEPCHAR = "\t";  # What char separates stag from original line in stagged version of corpus?  Space or tab, typically.

my $depsCount = 0; # counter for dependencies read




#my $ARGTYPES = "#SBJ#OBJ#TMZ#";  # what is an argument?
#my $ARGTYPES = "#SBJ#";  # what is an argument?
#my $ARGTYPES = "#SBJ#OBJ#PRD#";  # what is an argument?

# Relations in the French Treebank:

#aff
#a_obj
#arg
#ato
#ats
#aux_caus
#aux_pass
#aux_tps
#comp
#coord
#de_obj
#dep
#dep_coord
#det
#missinghead
#mod
#mod_rel
#obj
#obj1
#p_obj
#ponct
#root
#suj



my $ARGTYPES = "#SUJ#OBJ#A_OBJ#DE_OBJ#P_OBJ#";  # what is an argument?


#my $ARGTYPES = "";  # what is an argument?
my $SPECIALDEPRELTYPES = ""; # what rel becomes part of stag of dependent?
#my $SPECIALDEPRELTYPES = "#IDF#"; # what rel becomes part of stag of dependent?
#my $SPECIALDEPRELTYPES = "#IDF#MOD#TMZ#TPC#---#"; # what rel becomes part of stag of dependent?
my $SPECIALDEPRELTYPESDETAIL = "";  # more precisely, what rel becomes part of stag of dependent with which simple POS?
#my $SPECIALDEPRELTYPESDETAIL = "#NOM~IDF#NOM~MOD#PROP~IDF#PROP~MOD#";  # more precisely, what rel becomes part of stag of dependent with which simple POS?
my $FORMAT = "p7";  # catib or xml
#my $FORMAT = "catib";  # catib or xml
#my $FORMAT = "xml";  # catib or xml

my $INCLUDEGOVCAT = 1;  # Should stag include the cat of the governor?
my $INCLUDEDIR = 1;     # Should stag include the direction of attachment to gov?

# Tables used to record overall facts

my %sigTable = ();
# keys for sig table:
# 1. signature
# 2. word or 'total'
# value: number of times word occurs

my %adjTable = ();
# keys for adj table:
# 1. signature
# 2. segment number
# 3. sequence of adjs
# value: count

my %bigramTable = ();
# keys for bigram table:
# 1. sig
# 2. segNb
# 3. previous adjunct (POS)
# 4. next adjunct (POS) or 'total'
# value: count
# Note: special BOS and EOS markers for beginning of sequence/end of sequence 

my %lhsTable = ();
# Count frequency of LHS symbols

my %rhsTable = ();
# Record rhs symbols to check lhs symbols
# keys for sig table:
# 1. signature
# 2. word or 'total'
# value: number of times word occurs

my %rootTable = ();
# Count frequency of lhs used in root
# keys:
# 1. root symbol


my %lexTable = (); 
# Record words to be specialized for passive valency
# keys:
# 1. word
# value: boolean if on list


# First, read in word lists
my $lexCounter = 0;

if ($lexFile) {
    open(LEX,$lexFile) or die "$lexFile not found.\n";
    while (<LEX>) {
	last if ($lexCounter == $lexFileMax);
	next if (!/\S/);
	chomp;
	s/^\s*\d*\s*//;
	s/\s*$//;
	s|\~|Ptilde|g;
	s|\-|Phyphen|;
	$lexTable{$_} = 1;
	print "Added |$_| to lexTable\n";
	$lexCounter++;
    }
    close LEX;
    print "Read $lexFileMax words from $lexFile.\n";
}



# Tables used for each sentence



my %depsTable = ();
my %wordTable = ();
my @catTable = ();   # Record category of each word (to use later in composing stag)
my @govTable = ();  # Record governor of each node (arg: index)
my %lineTable = ();

# sig = the signature (head and subst nodes)
# alldeps = list of all dependents




my $inTree = 0;
my $count = 0;
my $rootCount = 0;

#my @files = `ls $depFiles`;
#print "ls $depFiles\n";

my $inTree = 1 if ($FORMAT eq "catib");
$inTree = 1 if ($FORMAT eq "p7");

my $fileStem = $depFile;
$fileStem =~ s/^.*\/(.*)$/$1/;

# foreach my $file (@files) {

#    chomp $file;
#    next if ($file =~ m/.*stag$/);
#    next if ($file =~ m/.*staggertrain$/);
print "Reading file $depFile\n";
open(IN,"$depFile") or die "-->No such file: |$depFile|\n";
my $outfile = "$fileStem";
$outfile .= ".DEPREL$ARGTYPES" if ($ARGTYPES ne "");
$outfile .= ".GOVREL$SPECIALDEPRELTYPESDETAIL" if ($SPECIALDEPRELTYPES ne "");
$outfile .= ".lexmax$lexFileMax" if ($lexFile ne "0");
$outfile .= ".stag";
open(OUT,">$outfile") or die "No such file: $outfile\n";

while (<IN>) {

    $inTree = 1 if (/<dependency>/);
    if ((($FORMAT eq "xml") && (/<\/dependency>/))
	|| (($FORMAT eq "catib") && (!/\S/))
	|| (($FORMAT eq "p7") && (!/\S/))) {

	# Save info from this sentence

	foreach (my $i=1; $i<=$count; $i++) {

	    my $thisSig = $depsTable{$i}{'sig'};
	    if ($INCLUDEGOVCAT) {
		$thisSig =~ s/(HEAD\+[A-Za-z]+\+[A-Za-z-]+)/$1\+$catTable[$govTable[$i]]/;
	    }
	    if ($INCLUDEDIR) {
		my $modDir = "L";
		$modDir = "R" if ($govTable[$i] > $i);
		$thisSig =~ s/(HEAD\+[A-Za-z]+\+[A-Za-z-]+)/$1\+$modDir/;
	    }
	    my $thisRHS = $depsTable{$i}{'rhs'};

	    $sigTable{$thisSig}{$wordTable{$i}}++;
	    $sigTable{$thisSig}{'total'}++;
	    $rhsTable{$thisRHS}{$wordTable{$i}}++;
	    $rhsTable{$thisRHS}{'total'}++;
	    $rhsTable{$thisRHS}{'sig'} = $thisSig;
	    for (my $j=0; $j<=$depsTable{$i}{'maxDepSeg'}; $j++) {
		$adjTable{$thisSig}{$j}{$depsTable{$i}{'depsPerSeg'}{$j}}++;
	    }

	    $thisSig =~ s/^~//;
	    print OUT $lineTable{$i};
	    print OUT "$SEPCHAR$thisSig\n";

	}

	print OUT "...EOS...//...EOS...//...EOS...\n";
	print OUT "...EOS...//...EOS...//...EOS...\n";

	%wordTable = ();
	@govTable = ();
	@catTable = ();
	%depsTable = ();
	%lineTable= ();
	$inTree = 0 if ($FORMAT eq "xml");
	$count = 0;

	


	
    }
    elsif ($inTree) {
	chomp;
	s/\+/PLUS/g;  # The plus sign interferes with the conventions used in the generated grammar; the French treebank uses it in POS tags


	my $depIndex;
	my $depWord;
	my $depLemma;
	my $depPos;
	my $headIndex;
	my $rel;
	my $feats;
	my $depWordCleaned;
	my $depPosCoarse;
	my $depPosSimple;
	my $depPosSimplePure;
	my $depPosLex;
	if ((($FORMAT eq "xml") && (m|\s*<dep>\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\S+)\s+()<\/dep>|))
	    || (($FORMAT eq "catib") && (m|^(\d+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\S+)\s+(.*)$|))){
	    $depsCount++;
	    $depIndex = $1;
	    $depWord = $2;
	    $depLemma = $2;
	    $depPos = uc($3);
	    $headIndex = $4;
	    $rel = uc($5);
	    $feats = $6;
	    $depWord =~ s|\~|Ptilde|g;
	    $depPos =~ s|\-|Phyphen|g;
	    $depWordCleaned = &cleanWord($depWord);

	    $govTable[$depIndex] = $headIndex;

	    # Do cleaning for Yuval variants
	    # Note: maybe keep these in depPosSimple, but remove from depPosSimplePure
	    # verbs
	    $depPos =~ s/Phyphen$//;
	    $depPos =~ s/PhyphenS$//;
	    # nouns
#		$depPos =~ s/PhyphenY$//;
	    # Cases for Yuval variations
	    $depPos =~ s/PhyphenA$//;
	    $depPos =~ s/PhyphenAN$//;
	    $depPos =~ s/PhyphenAT$//;
	    $depPos =~ s/PhyphenP$//;
	    $depPos =~ s/PhyphenY$//;
	    $depPos =~ s/PhyphenYN$//;
	    $depPos =~ s/PhyphenW$//;
	    $depPos =~ s/PhyphenWN$//;
	    $depPos =~ s/PhyphenPRON$//;
	    $depPos =~ s/PhyphenPREP$//;
	    $depPos =~ s/^ALPhyphen//;
	    $depPos =~ s/^NUM$/NOM/;
	    $depPos = "PROP" if ($depPos eq "NOMPhyphenPROP");
	    # Punctuation
	    $depPos = "PNX" if ($depPos =~ /^PNX/);

	    # And we do sometimes care about the word in the passive valency model (lhs)
	    $depPosLex = $depPos;
	    if ($lexFile && ($lexTable{"$depWordCleaned $depPos"})) {
#		    die "Dies: $depWord $depPos\n";
		$depPosLex .= "Y" . $depWordCleaned;

		
		# Look at passive valency (expressed as the lhs symbol in a rule)

		# In dependents (modeling passive valency, i.e., in the lhs
		# symbol), we do not care what the voice is (in head yes)
		$depPosSimple = $depPos;
#		if ($depPosSimple =~ /PASS/) { print "DepPosSimple: $depPosSimple\n" };
		$depPosSimple =~ s/PhyphenPASS$//;
		$depPosSimple =~ s/Phyphenpass$//;
		$depPosSimple =~ s/-pass$//;
		$depPosSimple =~ s/-PASS$//;
		$depPosSimplePure = $depPosSimple;
		# Do not distinguish PROP from NOM when looking at passive valency (lhs symbol)
		$depPosSimple =~ s/NOMPhyphenPROP/NOM/;  # new tag in new conversion
		$depPosSimple =~ s/PROP/NOM/;


	    }
	}

#p7 format
#1	Certes	certes	ADV	ADV	_	5	mod	_	_

	elsif (($FORMAT eq "p7") && (m|^(\d+)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+(\d+)\t+([^\t]+).*$|)){
	    $depsCount++;
	    $depIndex = $1;
	    $depWord = $2;
	    $depLemma = $3;
	    $depPosCoarse = uc($4);
	    $depPos = uc($5);
	    $feats = $6;
	    $headIndex = $7;
	    $rel = uc($8);
	    $depWordCleaned = &cleanWord($depWord);

	    $govTable[$depIndex] = $headIndex;

	    # And we do sometimes care about the word in the passive valency model (lhs)
	    $depPosLex = $depPos;
	    if ($lexFile && ($lexTable{"$depWordCleaned $depPos"})) {
#		    die "Dies: $depWord $depPos\n";
		$depPosLex .= "Y" . $depWordCleaned;
	    }

	    $depPosSimple = $depPos;
	    $depPosSimplePure = $depPos;

	}
	else{
	    die "wrong Treebank format\n";
	}


	# Common part starts here

	$catTable[$depIndex] = $depPosSimple;

#		if ($depPosSimple eq "PROP") {
#		    $depPosSimple = "NOM";
#		}
	# We do sometimes care about the relation in passive valency model (lhs)
	if  ($SPECIALDEPRELTYPES =~ "#$rel#") {
	    $depPosSimple .= $rel;
	}

	# And we do sometimes care about the word in the passive valency model (lhs)
	my $depPosSimpleLex = $depPosSimple;
	if ($lexFile && ($lexTable{"$depWordCleaned $depPos"})) {
#		    die "Dies: $depWord $depPos\n";
	    $depPosSimpleLex .= "Y" . $depWordCleaned;
	}
	

	# Now look at active valency

	# In heads (=stag), we do care about PROP vs NOM and voice
	my $depSig = "~HEAD+$depPosLex";
#		print "Deppossimple: $depPosSimplePure Rel: $rel\n";
	# Add passive valency to head if appropriate
	if ($SPECIALDEPRELTYPESDETAIL ne "") {
	    if  ($SPECIALDEPRELTYPESDETAIL =~ "#$depPosSimplePure~$rel#") {
		$depSig .= "+$rel";
	    }
	}
	elsif ($SPECIALDEPRELTYPES =~ "#$rel#") {
	    $depSig .= "+$rel";
	}

#		print "Depsig is $depSig\n";


	$lhsTable{$depPosSimpleLex}++;
	$wordTable{$depIndex} = $depWord;
#		$depsTable{$depIndex}{'pos'} = $depPos; not used
	$lineTable{$depIndex} = $_;
	
	# record info about head
	if ($headIndex == 0) {
	    # this is the root
	    $rootTable{$depPosSimpleLex}++;
	    $rootCount++;
	}
	else {
	    # record info about head
	    if ($ARGTYPES =~ "#$rel#") {
		# argument
		$depsTable{$headIndex}{'sig'} .= "~$rel+$depPosSimple";
		$depsTable{$headIndex}{'rhs'} .= "~$rel+$depPosSimpleLex";
		$depsTable{$headIndex}{'curDepSegt'}++;
		$depsTable{$headIndex}{'maxDepSeg'} = $depsTable{$headIndex}{'curDepSegt'};
	    }
	    else {
		#adjunct
		# need to set current dependents segment to 0 if not yet set
		$depsTable{$headIndex}{'curDepSegt'} = 0 
		    unless ($depsTable{$headIndex}{'curDepSegt'} > 0);
		$depsTable{$headIndex}{'depsPerSeg'}{$depsTable{$headIndex}{'curDepSegt'}} .= "~$rel+$depPosSimpleLex";
	    }
#		    $depsTable{$headIndex}{'alldeps'} .= "~$rel+$depPosSimple";
	}

	# record info about dependent (its head)
	$depsTable{$depIndex}{'sig'} .= $depSig;
	$depsTable{$depIndex}{'rhs'} .= $depSig;
#		$depsTable{$depIndex}{'alldeps'} .= $depSig;
	$depsTable{$depIndex}{'curDepSegt'}++;
	$depsTable{$depIndex}{'maxDepSeg'} = $depsTable{$depIndex}{'curDepSegt'};
	

	$count++;
#	    print "$depIndex $depWord $depPos $headIndex HeadWord HeadPos rel=$rel\n";
    }
}


close IN;
close OUT;

print "Wrote file $outfile\n";

#}

# Now print stuff

my $sigCounter = 1;

my $outfileSynt = "$ARGTYPES.synt";
my $outfileLex = "$ARGTYPES.lexicon";
my $outfileStag = "$ARGTYPES.stags";


if ($SPECIALDEPRELTYPES ne "") {
    $outfileSynt = "$ARGTYPES.$SPECIALDEPRELTYPES.synt";
    $outfileLex = "$ARGTYPES.$SPECIALDEPRELTYPES.lexicon";
    $outfileStag = "$ARGTYPES.$SPECIALDEPRELTYPES.stags";
}


if ($SPECIALDEPRELTYPESDETAIL ne "") {
    $outfileSynt = "$ARGTYPES.$SPECIALDEPRELTYPESDETAIL.synt";
    $outfileLex = "$ARGTYPES.$SPECIALDEPRELTYPESDETAIL.lexicon";
    $outfileStag = "$ARGTYPES.$SPECIALDEPRELTYPESDETAIL.stags";
}

if ($lexFile) {
    $outfileSynt = "$ARGTYPES.lexmax$lexFileMax.synt";
    $outfileLex = "$ARGTYPES.lexmax$lexFileMax.lexicon";
    $outfileStag = "$ARGTYPES.lexmax$lexFileMax.stags";
}

open(SYNT,">$outfileSynt");
open(LEX,">$outfileLex");
open(STAG,">$outfileStag");

foreach my $sig (sort { $sigTable{$b}{'total'} <=> $sigTable{$a}{'total'} } (keys %sigTable)) {

    print LEX "**** Signature $sigCounter: $sig (";
    print LEX $sigTable{$sig}{'total'};
    print LEX " occurrences)\n";
    print STAG "**** Signature $sigCounter: $sig (";
    print STAG $sigTable{$sig}{'total'};
    print STAG " occurrences)\n";
    print LEX "** Words: ";
    foreach my $word (sort (keys %{ $sigTable{$sig}})) {
	print LEX " $word:$sigTable{$sig}{$word}";
    }
    print LEX "\n";

    print SYNT "**** Signature $sigCounter: $sig (";
    print SYNT $sigTable{$sig}{'total'};
    print SYNT " occurrences)\n";
    print SYNT "** Adjuncts by Segment\n";
    foreach my $segNb (sort (keys %{ $adjTable{$sig}})) {
	print SYNT "* Segment $segNb\n";
	foreach my $adjSequence (sort (keys %{ $adjTable{$sig}{$segNb}})) {
	    printf SYNT "%6d ", $adjTable{$sig}{$segNb}{$adjSequence};
	    print SYNT "$adjSequence\n";

	    # Now record bigrams in table
	    my @adjSeqParts = split '\~', $adjSequence;
	    push @adjSeqParts, "EOA";
	    my $prevAdj = "BOA";

	    foreach my $adjPart (@adjSeqParts) {
		next if ($adjPart !~ /\w/);
		$bigramTable{$sig}{$segNb}{$prevAdj}{$adjPart} += $adjTable{$sig}{$segNb}{$adjSequence}; 
		$bigramTable{$sig}{$segNb}{$prevAdj}{'total'} += $adjTable{$sig}{$segNb}{$adjSequence}; 
		$prevAdj = $adjPart;
	    }

	}
    }
    print SYNT "\n\n";

    $sigCounter++;


}

close SYNT;
close LEX;
close STAG;

print "Read $depsCount dependency relations in $rootCount sentence units.\n";



# Now print grammar

my $outfileGram = "$ARGTYPES.bnf";

if ($SPECIALDEPRELTYPES ne "") {
    $outfileGram = "$ARGTYPES.$SPECIALDEPRELTYPES.bnf";
}


if ($SPECIALDEPRELTYPESDETAIL ne "") {
    $outfileGram = "$ARGTYPES.$SPECIALDEPRELTYPESDETAIL.bnf";
}


if ($lexFile) {
    $outfileGram = "$ARGTYPES.lexmax$lexFileMax.bnf";
}


open(GRAM,">$outfileGram");

print GRAM "*** Axioms\n\n";

foreach my $rootSymbol (keys %rootTable) {

    print GRAM "<AXIOM> = <" . &purifySig($rootSymbol) . "> ; ";
    print GRAM $rootTable{$rootSymbol}/$rootCount;
    print GRAM "\n";

}


print GRAM "\n*** Signatures\n\n";

foreach my $rhs (sort { $rhsTable{$b}{'total'} <=> $rhsTable{$a}{'total'} } (keys %rhsTable)) {

    my $prettySig = $rhsTable{$rhs}{'sig'};
    $prettySig =~ s/^~//;
    my $prettySigPure = &purifySig($prettySig);

    my $lhs = &cleanSig($rhs);         # gets at head, then strips it of detail
    my $lhsPure = &purifySig($lhs);
    
    # Now construct right-hand side of rule
    my $rhsString = " <$prettySigPure-0*BOA>";
    my @sigParts = split '~', $rhs;
    my $i = 1;
    foreach my $rhsPart (@sigParts) {
	next if $rhsPart eq "";
	my @info = split '\+', $rhsPart;
	my $label = $info[0];
	my $pos = $info[1];
	if ($label eq "HEAD") {
	    $rhsString .= " $prettySigPure <$prettySigPure-$i*BOA>";
	    $i++;
	}
	else {
	    my $posPure = &purifySig($pos);
	    $rhsString .= " <$posPure> <$prettySigPure-$i*BOA>";
	    $i++;
	}

    }
    print GRAM "* SIG: $prettySig ($rhsTable{$rhs}{'total'} of $lhsTable{$lhs})\n";
    print GRAM "<$lhsPure> = $rhsString ; ";
    if ($lhsTable{$lhs} == 0) {
	print "$lhs has zero occurrences, this should not happen!\n";
    }
    else {
	print GRAM $rhsTable{$rhs}{'total'}/$lhsTable{$lhs};
    }
    print GRAM "\n";

}


print GRAM "\n*** Modifier Bigrams\n\n";

foreach my $sig (sort { $sigTable{$b}{'total'} <=> $sigTable{$a}{'total'} } (keys %sigTable)) {
    my $prettySig = $sig;
    $prettySig =~ s/^~//;
    my $prettySigPure = &purifySig($prettySig);
    print GRAM "** Signature: $prettySig\n";
    foreach my $segNb (sort (keys %{ $adjTable{$sig}})) {
	print GRAM "* Segment $segNb\n";
	foreach my $prevAdj (sort (keys %{ $bigramTable{$sig}{$segNb}})) {
	    my $prevAdjPure = &purifySig($prevAdj);
	    foreach my $adjPart (sort (keys %{ $bigramTable{$sig}{$segNb}{$prevAdj}})) {
		next if ($adjPart eq "total");
		print GRAM "<$prettySigPure-$segNb*$prevAdjPure> = ";
		if ($adjPart ne "EOA") {
		    my $adjCat = $adjPart;
		    $adjCat =~ s/^[^\+]+\+([^\+]+)$/$1/;
		    my $adjCatPure = &purifySig($adjCat);
		    my $adjPartPure = &purifySig($adjPart);
		    print GRAM " <$adjCatPure> <$prettySigPure-$segNb*$adjPartPure> ";
		}
		print GRAM "; ";
		print GRAM $bigramTable{$sig}{$segNb}{$prevAdj}{$adjPart} /
		    $bigramTable{$sig}{$segNb}{$prevAdj}{'total'} ;
		print GRAM "\n";
	    }
	}
    }
}


close GRAM;



print "Wrote pcfg info into file $outfileGram and lexicon into file $outfileLex.\n";


# Modify left-hand side nonterminal -- this changes the way the
# grammar is modeled!

sub cleanSig {

    my $lhs = shift;

    $lhs =~ s/^.*~HEAD\+([^~]+).*/$1/;
    $lhs =~ s/PhyphenPASS//;
    $lhs =~ s/\-PASS//;
    $lhs =~ s/PROP/NOM/;

    return $lhs;

}

sub purifySig {

    my $expr = shift;
    $expr =~ s/\+/X/g;
    $expr =~ s/~/Z/g;
    $expr =~ s/\./Pperiod/;
    $expr =~ s/\,/Pcomma/;
    $expr =~ s/\"/Pquote/;
    $expr =~ s/\:/Pcolon/;
    $expr =~ s/\-/Pdash/;
    $expr =~ s|\/|Pfslash|;
    $expr =~ s|\~|Ptilde|;  # this will not be used -- this is hardcoded above just for the word!
    $expr =~ s/\'/Lhamza/;
    $expr =~ s/\*/Ltha/;
    $expr =~ s/\</Lalifhamzaabove/;
    $expr =~ s/\>/Lalifhamzabelow/;
    $expr =~ s/\}/Lyahamzaabove/;
    return $expr;

}

sub purifySigRHS {

    my $expr = shift;
    if ($expr =~ /^<(.*)>$/) {
	my $middle= $1;
	return "<" . &purifySig($middle) . ">";
    }
    else {
	return &purifySig($expr);
    }
}



sub cleanWord {

    # Transform word to make it more general (or whatever)
    # So far, just deal with digits

    my $word = shift;

    if ($DIGITCONVERSION && (($word =~ /^\d[\d\.]*$/) || ($word =~ /^[\d\.]*\d$/))) {
	$word =~ s/\d/8/g;
	$word =~ s/\./c/g;
    }
    return $word;

}

