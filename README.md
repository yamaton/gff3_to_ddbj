# GFF3-to-DDBJ
日本語版は[こちら](https://github.com/yamaton/gff3toddbj/blob/main/README-ja.md)。


[TOC]

## What is this?

GFF3-to-DDBJ creates [DDBJ's annotation file](https://www.ddbj.nig.ac.jp/ddbj/file-format-e.html#annotation) from GFF3 and FASTA files. It also works from FASTA alone.




## Initial setup

### [NOT available yet] Install via bioconda

```shell
# Create a conda environment named "ddbj", and install relevant packages from bioconda channel
$ conda create -n ddbj -c bioconda gff3toddbj

# Activate the environment "ddbj"
$ conda activate ddbj
```



### Install from the source

```shell
# Download
$ wget https://github.com/yamaton/gff3_to_ddbj/archive/refs/heads/main.zip

# Extract, rename, and change directory
$ unzip main.zip && mv gff3toddbj-main gff3toddbj && cd gff3toddbj

# Create a conda environment named "ddbj"
$ conda create -n ddbj

# Activate the environment "ddbj"
$ conda activate ddbj

# Install dependencies to "ddbj"
$ conda install -c bioconda -c conda-forge biopython bcbio-gff

# Install gff3-to-ddbj and extra tools
$ python setup.py install
```



## Create DDBJ annotation from GFF3 and FASTA



### 3. Run `gff3-to-ddbj`

Let's run the main program to get some ideas. Here is the options.

* `--gff3 <FILE>` takes GFF3 file
* `--fasta <FILE>` takes FASTA file

* `--config <FILE>` takes the configuration file in TOML
* `--locus_tag_prefix <STRING>` takes the prefix of locus tag [obtained from BioSample](https://www.ddbj.nig.ac.jp/ddbj/file-format-e.html#locus_tag). You can skip this for now.
* `--transl_table <INT>`: Choose appropriate one from [The Genetic Codes](https://www.ddbj.nig.ac.jp/ddbj/geneticcode-e.html). The default value is 1 ("standard").
* `--output <FILE>` sets the path the annotation output.

```shell
gff3-to-ddbj
  --gff3 myfile.gff3 \                # produces the minimum without this line
  --fasta myfile.fa \                 # <<REQUIRED>>
  --config config.toml \              # produces the minimum without this line
  --locus_tag_prefix MYOWNPREFIX_ \   # set to "LOCUSTAGPREFIX_" without this line
  --transl_table 1 \                  # set to 1 without this line
  --output myawesome_output.ann       # standard output without this line
```



## Customize the behavior

### Edit `config.toml`

You need to edit a configuration file in TOML, say `config.toml`. Take a look at [the sample TOML file with COMMON](https://raw.githubusercontent.com/yamaton/gff3toddbj/main/gff3toddbj/config.toml), or [the one without COMMON](https://raw.githubusercontent.com/yamaton/gff3toddbj/main/gff3toddbj/config_without_COMMON.toml). The configuration contains following items. They are all optional, and **GFF3-to-DDBJ works even without `config.toml`.**

* Basic features in COMMON

* "meta-description" in COMMON

  * DDBJ annotation supports features under COMMON that are inserted to each of repeatedly-occurring features in the resulting flat file.

  * Here is an example.

    ```toml
    [COMMON.assembly_gap]
    estimated_length = "unknown"
    gap_type = "within scaffold"
    linkage_evidence = "paired-ends"
    ```

* Feature-Qualifier information inserted to each occurrence by done GFF3-to-DDBJ

  * This should work effectively the same purpose as the "meta-description" item above. But this repeated insertions are done by GFF3-to-DDBJ, and appears in the annotation output. **This configuration is mutually exclusive with the "metadata-description" configuration.** I'm keeping both simply because I'm undecided yet.

  * Here is an example: Difference from the previous one is only at `[assembly_gap]` as opposed to`[COMMON.assembly_gap]`.

    ```toml
    [assembly_gap]
    estimated_length = "unknown"   # Set it "<COMPUTE>" to count the number of N's
    gap_type = "within scaffold"
    linkage_evidence = "paired-ends"
    ```





### [advanced] Edit translation table

GFF3 and DDBJ annotation have rough correspondence as follows:

1. GFF3 column 3 --> DDBJ annotation column 2 as "Feature"
2. GFF3 column 9 --> DDBJ annotation column 4 and 5 as "Qualifier key", and "Qualifier value"

but nomenclatures in GFF3 often do not conform the INSDC definitions. Furthermore, DDBJ lists up the [feature-qualifier pairs they accepts](https://docs.google.com/spreadsheets/d/1qosakEKo-y9JjwUO_OFcmGCUfssxhbFAm5NXUAnT3eM/edit#gid=0), which is stricter than INSDC.

To satisfy requirement, I have prepared translation tables for features and qualifiers, and GFF3-to-DDBJ uses the table. For example, GFF3 may contain `five_prime_UTR` in the column 2, but `5'UTR` is the translated name in the outcome. You can edit the translation tables and feed them with

* `--translate_feature <file>` for feature translation
* `--translate_qualifeirs <file>` for qualifier translation

And here is an example call.

```shell
gff3-to-ddbj
  --gff3 myfile.gff3 \
  --fasta myfile.fa \
  --config config.toml \
  --locus_tag_prefix MYOWNPREFIX_ \
  --transl_table 1 \
  --translate_features translate_features.toml \
  --translate_qualifiers translate_qualifiers.toml \
  --output myawesome_output.ann
```





## Troubleshooting

### Validate GFF3

It might be a good practice to validate your GFF3 files. [GFF3 online validator](http://genometools.org/cgi-bin/gff3validator.cgi) is useful though the file size is limited to 50MB.



### Split FASTA from GFF3 (if needed)

GFF3_to_DDBJ does not work when GFF3 contains FASTA information inside with `##FASTA` directive. Attached tool under `split-fasta` reads a GFF3 file and saves GFF3 (without FASTA info) and FASTA.

```shell
split-fasta path/to/myfile.gff3 --suffix "_modified"
```

This creates two files, `myfile_modified.gff3` and `myfile_modified.fa`.



### Fix entry names (if needed)

Letters like `=|>" []` are not allowed in the 1st column (= "Entry") of the DDBJ annotation.  So, you need to rename the 1st column (= "SeqID") of your GFF3 and headers in your FASTA. Attached tool `rename-ids` might be useful. This program converts an ID like `ERS324955|SC|contig000013` into `ERS324955:SC:contig000013`.

```shell
rename-ids \
  --gff3=path/to/foo.gff3 \
  --fasta=path/to/bar.fasta \
  --suffix="_renamed_ids"
```

This command saves two files, `foo_renamed_ids.gff3` and `bar_renamed_ids.fasta` *if* the invalid letters are found. Otherwise, you'll see no output.



fo

## Under the Hood

Here is the list of operations done by `gff3-to-ddbj`.

* Rename Feature / Qualifiers keys using the translation tables

* Search for `assembly_gap` s in FASTA

* Add `/transl_table` to each CDS

* Insert information from configuration fie

* Merge `CDS`s having the same parent with `join` notation

* Merge `mRNA` and `exon` in GFF3 and create `mRNA` feature with `join` notation

* Check start codon consistency. (Except for `/codon_start=1`  for now)

* Let CDS have a single `/product` value. Move the rest to `/note`.

  * This is to conform the [instruction](https://www.ddbj.nig.ac.jp/ddbj/qualifiers-e.html#product) on `/product`.

    > * Even if there are multiple general names for the same product, do  not enter multiple names in 'product'. Do not use needless symbolic  letters as delimiter for multiple names. If you would like to describe  more than two names, please enter one of the most representative name in /product qualifier, and other(s) in /[note](https://www.ddbj.nig.ac.jp/ddbj/qualifiers-e.html#note) qualifier.
    >
    > * If the name and function are not known, we recommend to describe as "hypothetical protein".

* Remove duplicates in qualifier values
* Sort lines in annotation
* Filter out Feature-Qualifier pairs following [the table](https://www.ddbj.nig.ac.jp/assets/files/pdf/ddbj/fq-e.pdf).
