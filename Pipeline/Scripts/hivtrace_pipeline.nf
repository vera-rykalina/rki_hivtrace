nextflow.enable.dsl = 2

// HPC
projectDir = "/home/rykalinav/scratch/rki_hivtrace/Pipeline"
// Linux
//projectDir = "/home/beast2/rki_hivtrace/Pipeline"

// Run
/* nextflow Scripts/hivtrace_pipeline.nf 
   --outdir Results 
   -c Scripts/rki_profile.config 
   -profile rki_slurm,rki_mamba
*/

params.outdir = null
if (!params.outdir) {
  println "outdir: $params.outdir"
  error "Missing output directory!"
}

 
/***********************
----Sanity Commands-----
************************/
// Remove white space
//sed -i  '/>.*/s/\r//' file.fasta
// Add fake date, if needed
//sed -i 's/>.*/&|02022022/' file.fasta

// Alternative
/*
cat ${testfastas} | awk '{
        if (substr(\$0, 1, 1)==">") {filename=(substr(\$1,2) ".fasta")}
        print \$0 >> filename }' */



ch_core_refs = Channel.fromPath("${projectDir}/CoreSequences/*.fas")
ch_test_refs = Channel.fromPath("${projectDir}/TestSequences/*.fas")

workflow {
    ch_split_fasta  = SPLIT_FASTA(ch_test_refs)
    ch_core_test_list = ch_core_refs.combine(ch_split_fasta.flatten())
    ch_core_test_concatinated  = CONCAT_CORE_TEST(ch_core_test_list)
    ch_hivtrace = HIVTRACE(ch_core_test_concatinated)
    ch_network = HIVNETWORKCSV(ch_hivtrace.csv)
    ch_csv_join = JOIN_CSVNETWORK(ch_network.csvnetwork.collect())
}


process SPLIT_FASTA {
  conda "${projectDir}/Environments/fasplit.yml"
  publishDir "${params.outdir}/01_split_fastas", mode: "copy", overwrite: true
  
  input:
    path testfastas
  output:
    path "*.fasta"
  script:
  """
    faSplit byname ${testfastas} ./
    regex-rename '(\\d{2}-\\d{5})\\|\\d{2}\\d{2}\\d{4}.fa' '\\1.fasta' --rename
  """
}


process CONCAT_CORE_TEST {
  publishDir "${params.outdir}/02_ref_test", mode: "copy", overwrite: true
  
  input:
    path fastas
  output:
    path "${fastas[1].getBaseName()}.fas"
  script:
  """
  cat ${fastas[0]} ${fastas[1]} > ${fastas[1].getBaseName()}.fas
  """
}

process HIVTRACE {
  //conda "${projectDir}/Environments/hivtrace.yml"
  conda "/home/rykalinav/.conda/envs/hivtrace_training"
  publishDir "${params.outdir}/03_hivtrace", mode: "copy", overwrite: true
  
  input:
    path fasta
  output: 
    path "*_tn93.csv", emit: csv
    path "*.json", emit: json
   
  script:
  """
    hivtrace \\
       -i ${fasta} \\
       -a resolve \\
       -r HXB2_prrt \\
       -t 0.015 \\
       -m 500 \\
       -g 0.05 
    
    mv ${fasta}_user.tn93output.csv  ${fasta.getBaseName()}_tn93.csv
    mv ${fasta}.results.json  ${fasta.getBaseName()}.json
 
  """
}

process HIVNETWORKCSV {
  //conda "${projectDir}/Environments/hivtrace.yml"
  conda "/home/rykalinav/.conda/envs/hivtrace_training"
  publishDir "${params.outdir}/04_hivnetwork", mode: "copy", overwrite: true
  
  input:
    path csv
  output: 
    path "*.csv", emit: csvnetwork
    path "*.json", emit: jsonnetwork
  script:
  """
    hivnetworkcsv \\
      -i ${csv} \\
      -c ${csv.getBaseName().split("_")[0]}_network.csv \\
      -j \\
      -O ${csv.getBaseName().split("_")[0]}_network.json \\

  """
}

process JOIN_CSVNETWORK {
  conda "/home/rykalinav/.conda/envs/python3"
  publishDir "${params.outdir}/05_joined_csvnetwork", mode: "copy", overwrite: true
  
  input:
    path csvnetworkfiles
  output:
    path "joined_csvnetwork_tables.csv"
  script:
  """
    join_csvnetwork_tables.py ${csvnetworkfiles}
  """
}