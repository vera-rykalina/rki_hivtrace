nextflow.enable.dsl = 2

projectDir = "/home/beast2/rki_hivtrace/Pipeline"


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

// ALternative
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
    path "${fastas[1].getBaseName()}_test_core.fasta"
  script:
  """
  cat ${fastas[0]} ${fastas[1]} > ${fastas[1].getBaseName()}_test_core.fasta
  """
}

process HIVTRACE {
  conda "${projectDir}/Environments/hivtrace.yml"
  publishDir "${params.outdir}/03_hivtrace", mode: "copy", overwrite: true
  
  input:
    path fasta
  output:
    path "${fasta.getBaseName().split("_")[0]}_user.tn93output.csv"
  script:
  """
    hivtrace \\
       -i ${fasta} \\
       -a resolve \\
       -r HXB2_prrt \\
       -t 0.015 \\
       -m 500 \\
       -g 0.05 \\
       -o ${fasta.getBaseName().split("_")[0]}_user.tn93output.csv
  """
}