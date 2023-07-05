#!/usr/bin/env python3

import json
import re
from logging import info, warning, debug
import logging
import pandas as pd
import argparse
import os
DESCRIPTION =""" 
    This Program colors the taxa of a Tree according to a Clustering-Object in a file.

    Requirements: Pandas
"""
# def dir_path(path):
#     if os.path.isdir(path):
#         return path
#     else: 
#         raise argparse.ArgumentTypeError(f"{path} is invalid path")

def parseCommandline():
    """ parse Commandline to cfg"""
    parser = argparse.ArgumentParser(description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    inputg = parser.add_mutually_exclusive_group(required = True)
    inputg.add_argument('-t','--treefile', metavar = 'PATH', type = str,
                        help='treefile to be colored')
    inputg.add_argument('-a','--annotations', metavar = 'PATH', type = str,
                        help='path to save annotationsfile')
    clustg = parser.add_mutually_exclusive_group(required = True) # Cluster-Object
    clustg.add_argument("--hivtrace",'-j', type = str, metavar='PATH',
                        help = 'Json-File created by hivtrace')
    clustg.add_argument('--csv', '-c', type = str, metavar='PATH',
                        help='Get clustering-Data from a CSV-File with two coloumns: cluster,Sequence-Name ')
    parser.add_argument('--branches', '-b', action = 'store_true',
                        help = 'If specified Color Branches as well as nodes')
    parser.add_argument('--outpath', '-o', metavar='PATH',
                        help='Output path for colored treefile')
    parser.add_argument('--verbose', '-v',  type=int, nargs='?', const=1, default=0,
                        help='verbose')
    parser.add_argument('--log', '-l', type=str, metavar='LOG-FILENAME',
                        help='logfile')
    args = parser.parse_args()  

    # Create Logger
    log_fn = args.log
    if args.log: logging.basicConfig(filename=log_fn)

    logger = logging.getLogger()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter('%(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return args


def partNexusBy(string, sep):
    split1 = re.split(pattern = "begin " +sep, string = string,maxsplit=1, flags=re.IGNORECASE) 
    split2 = re.split(pattern = "end;", string = split1[1],maxsplit=1, flags=re.IGNORECASE)
    before = split1[0]
    after = split2[1]
    mid = "begin "+sep + split2[0] + "end;"

    return before, mid, after

#RANDOM_COLORS = ['a52a2a', 'da8a67', '138808', '417dc1', 'b76e79', 'a9a9a9', 'a4dded', '7fff00', '00ffff', 'f7e98e', '6f4e37', '195905', 'c19a6b', 'aec6cf', 'a99a86', 'e08d3c', 'b38b6d', 'ff0028', 'fbcce7', '8f00ff', 'f56991', '367588', '2a52be', 'c8a2c8', 'ff55a3', 'b2ffff', 'e3dac9', 'b666d2', '5d8aa8', 'ff9933', '00ff7f', 'cfb53b', 'bdb76b', 'ffbd88', 'fefe22', 'ffff66', 'ffe4c4', 'cd5700', '50c878', 'e52b50', 'e6e6fa', '93ccea', 'e6e6fa', 'c4c3d0', '6082b6', 'f5f5f5', '9d81ba', 'e30b5d', '979aaa', '800020', 'f5deb3', 'c04000', 'b39eb5', '006600', 'ee82ee', 'ccff00', 'fff700', '8a2be2', '654321', 'c90016', '8db600', '120a8f', 'ffbcd9', '9f8170', '7cfc00', '89cff0', 'ffebcd', '7b1113', 'c41e3a', 'f0e130', 'fff5ee', 'b03060', 'e34234', 'eedc82', '23297a', 'ff007f', '4b5320', '006a4e', 'ab4e52', 'cd5b45', 'edc9af', 'cc0000', 'afeeee', '007aa5', '66ff00', '808000', '7b68ee', 'f0fff0', 'fcc200', 'faebd7', 'cf71af', '801818', '32127a', '002fa7', '00a86b', 'd70a53', 'fffafa', '536895', '4d5d53', 'bfff00', 'fe28a2', '76ff7a', 'fe4eda', '00ced1', '013220', 'ff6fff', '85bb65', 'ffc40c', '0f0f0f', 'fadadd', 'ffb7c5', 'fbceb1', 'ff8f00', 'e1ad21', 'daa520', 'fb607f', '1dacd6', '324ab2', '48d1cc', '21421e', 'f4c2c2', 'fada5e', '003399', 'e2725b', '36454f', '000080', 'fad6a5', '682860', 'deb887', '002e63', 'fc8eac', '2c1608', 'ffba00', '98817b', '1e90ff', 'ff033e', '008000', 'cd7f32', 'ffc1cc', '006d5b', 'aa98a9', 'fad6a5', 'fdbcb4', 'ffbf00', '800000', 'ffb6c1', '8a795d', '3d2b1f', 'cf1020', 'ff8c00', 'ffdab9', '003153', 'fff8dc', 'a7fc00', 'e49b0f', '0abab5', '1034a6', 'e18e96', 'd40000', 'ffd1dc', 'b31b1b', '9bc4e2', '990000', 'ecebbd', 'aaf0d1', 'e0115f', 'ace5ee', 'ff6347', '087830', '30ba8f', 'ff2052', 'faebd7', '00ff00', 'ef3038', 'a2a2d0', 'ff9966', 'a67b5b', 'ed872d', '9370db', 'ff355e', 'c2b280', '996666', 'a67b5b', 'f4f0ec', 'ffff99', '98fb98', 'd3d3d3', 'eee600', 'e48400', 'fdee00', '9966cc', '000f89', 'ff0000', 'ffa700', '808080', '654321', 'ff4500', 'ffa812', '00ff00', 'ff00ff', '0f52ba', '8a2be2', 'd2691e', 'ff2800', 'd1e231', 'ff7f50', '87a96b', '40826d', 'da1d81', 'ffbf00', '6699cc', 'add8e6', '00ffff', 'cd9575', 'f5fffa', 'e03c31', '273be2', '177245', '2e8b57', 'b94e48', 'e9692c', '191970', '967117', 'bc8f8f', 'f8de7e', 'ff8c69', '0f4d92', 'ffae42', 'eb4c42', 'c3b091', '8b008b', 'ffe5b4', 'e3256b', 'f4c430', '808080', 'fba0e3', 'f75394', 'ff4040', '4f7942', '45cea2', 'ff5a36', '006994', '004b49', 'faf0e6', 'cba135', '87cefa', 'f8f4ff', 'ffefd5', 'ff9f00', '008b8b', 'a0d6b4', 'cfcfc4', '4682b4', 'f3e5ab', 'ae0c00', 'fd5e53', 'bcd4e6', 'a3c1ad', 'd3003f', '30d5c8', 'fdf5e6', 'fcf75e', 'ff33cc', '738678', 'b57281', '555555', 'cc4e5c', '003366', '007474', '004953', 'de5d83', 'ccccff', '43b3ae', 'ffcc00', 'c2b280', '006b3c', '99badd', '800080', 'ffc87c', 'fc6c85', '009e60', '7851a9', 'e4d96f', '9457eb', '2f4f4f', 'bb6528', 'f8d568', 'fbaed2', 'ccccff', 'f78fa7', 'ffd700', '6f00ff', 'ee82ee', 'b19cd9', '004242', '49796b', '746cc0', 'bb3385', '0000cd', 'c19a6b', '6c541e', '8fbc8f', '414a4c', 'b0e0e6', '96c8a2', 'ffdb58', '008080', '86608e', '9932cc', '71bc78', 'dda0dd', 'd2b48c', 'ff8243', 'e5b73b', 'e8000d', 'ffff00', 'b8860b', '8b4513', 'ce2029', '8a496b', 'ace1af', 'ff9999', 'eae0c8', 'dc143c', '0000ff', '6495ed', '9acd32', '78866b', 'ffa089', '465945', '66023c', '933d41', '722f37', '9f1d35', 'dbd7d2', '91a3b0', 'bfff00', '059033', '8a3324', '32cd32', 'ff1493', 'da3287', 'a1caf1', '93c572', 'ec3b83', 'e7feff', '1560bd', '00ffef', '483d8b', 'ddadaf', 'fffaf0', '708090', 'b31b1b', 'e32636', 'ff00ff', 'e5e4e2', 'f0dc82', '967117', 'fe6f5e', 'e2062c', '39ff14', 'ff69b4', 'ff6700', 'ecd540', '3f00ff', '66424d', '9bddff', 'ff66cc', 'c9dc87', 'e66771', 'df73ff', '74c365', 'a9ba9d', 'ff3800', 'b5651d', 'e0ffff', 'cc7722', 'ff00ff', 'f400a1', 'dda0dd', '73a9c2', 'bcd4e6', 'f3e5ab', 'f8f8ff', 'f94d00', 'fffff0', 'b2ec5d', '915c83', 'e9d66b', 'deaa88', 'cc3333', 'eee8aa', 'b22222', 'c9a0dc', '5f9ea0', '00755e', '50c878', 'f77fbe', 'ff5349', '79443b', 'cc6666', '00cc99', 'da70d6', 'e7accf', '73c2fb', '9aceeb', 'dcdcdc', '004225', 'a020f0', '004040', 'db7093', '8878c3', '483c32', '836953', '80461b', '007fff', 'ff0038', '6e7f80', 'fbec5d', 'b87333', 'c80815', 'f4c2c2', 'f5f5dc', 'faf0be', 'e4d00a', '915f6d', '3cd070', 'd8bfd8', 'd6cadd', 'c71585', '0bda51', '123524', '4166f5', '0038a8', 'fff0f5', 'af4035', '8c92ac', '355e3b', 'a9203e', 'c5b358', '003399', 'cd5c5c', '5a4fcf', '6b8e23', '035096', 'e6e200', 'f4bbff', 'f984ef', '536878', '673147', 'cc00cc', '674846', 'ffa07a', '990000', '8b8589', '96ded1', 'ffef00', 'ba55d3', '0067a5', '08e8de', 'f88379', 'ffcba4', '483c32', '796878', 'f4bbff', 'f0ead6', 'af4035', '1c352d', 'c154c1', '4b3621', '1164b4', '996515', '21abcd', 'ff7518', '20b2aa', '922724', 'ff0040', 'ffff31', 'd99058', 'ffc0cb', '967117', 'ed9121', '6a5acd', '0072bb', '614051', '88d8c0', 'efdecd', '4b0082', 'b7410e', '0095b6', '321414', '00fa9a', '00008b', 'e75480', 'c9c0bb', '5218fa', 'fadfad', 'ff6961', '507d2a', 'e30022', 'ffb300', 'ffff00', '734f96', 'f400a1', 'ffcc33', 'c32148', 'ff77ff', '704214', 'ffdf00', 'ffd800', 'a0785a', 'cb410b', '9ab973', '26619c', 'e0b0ff', 'e5aa70', '014421', 'de3163', '009000', '5d8aa8', '9678b6', 'e25098', 'e6e8fa', '00bfff', 'ffffed', '1fcecb', '635147', 'ffb347', '915f6d', 'ccff00', 'fffdd0', 'c08081', '5b92e5', 'be0032', '65000b', '0054b4', '674c47', '007ba7', 'e68fac', 'f0e68c', '704241', '536872', '702963', 'f49ac2', '9400d3', 'c0c0c0', '967bb6', 'b06500', '00563f', '701c1c', 'd19fe8', 'a52a2a', '779ecb', '0014a8', 'c54b8c', '98777b', '3fff00', '9f00ff', '800080', '4169e1', 'ff2400', 'f08080', '78184a', 'fae7b5', 'bf00ff', 'da9100', 'f4a460', 'addfad', 'e97451', 'd2691e', '0d98ba', 'cc5500', 'bf94e4', 'cb4154', 'bdda57', '534b4f', '00009c', '3eb489', '5d3954', 'fff600', '6050dc', '7df9ff', 'a50b5e', '08457e', 'ffe4e1', 'e34234', 'f9429e', '002147', '0fc0fc', '882d17', 'fafad2', '808000', 'bc987e', '645452', '967117', '90ee90', 'e6be8a', 'bab86c', '0892d0', '990000', 'ca2c92', 'c19a6b', 'e62020', '98ff98', '778899', 'd73b3e', '00693e', '2a8000', '0047ab', 'a81c07', 'fc74fd', 'e9d66b', 'b5a642', '9955bb', 'e1a95f', 'ff43a4', 'fad6a5', '18453b', 'ffcc00', 'de6fa1', 'fdfd96', '87ceeb', 'c71585', '100c08', 'ff007f', 'a52a2a', 'a40000', 'd9004c', 'fc89ac', '03c03c', 'fbec5d', 'dda0dd', '483c32', 'd71868', '918151', '848482', 'f0ffff', 'fdd5b1', '8b0000', 'e4717a', '1e4d2b', '987654', 'a2add0', '663854', 'ff6e4a', 'fff8e7', 'db7093', '69359c', '00ff7f', 'e25822', 'e9967a', 'b3446c', '986960', '000000', '318ce7', 'ae2029', '997a8d', '872657', '696969', 'de3163', 'df00ff', 'b53389', 'b78727', 'ff1dce', 'ffa500', 'cb99c9', 'fc0fc0', '1ca9c9', 'fe59c2', '4997d0', '00ffff', '1a2421', '560319', 'f0f8ff', 'c19a6b', '873260', 'd0f0c0', '50404d', '008080', '0077be', '3cb371', 'e32636', 'e3a857', 'ff1493', 'f984e5', '446ccf', 'cc8899', 'ffe135', '4cbb17', 'c23b22', 'fddde6', 'f2f3f4', '66ddaa', '905d5d', 'fffacd', '77dd77', '3c1414', '00ffff', 'ef98aa', '592720', 'bd33a4', 'adff2f', 'd70040', 'f6adc6', 'abcdef', 'df00ff', 'ffdead', '0070ff', 'fff44f', 'a8e4a0', 'dcd0ff', '1c39bb', 'b2beb5', '414833', 'ffa343', 'fada5e', 'ff004f', '008000', 'fd0e35', 'ff4f00', 'ff003f', '480607', '893f45', 'f64a8a', '536878', '228b22', '966fd6', 'cd5c5c', 'a4c639', '0073cf', 'f2f3f4', 'd68a59', 'd2691e', '556b2f', '01796f', 'fada5e', '7fffd4', 'ff0800', 'ffa6c9', '29ab87', '00bfff', 'ff91a4', '0033aa', 'b784a7', 'f28500']
# print(len(RANDOM_COLORS)) = 746

def get_colors():
    """docstring for get_colors"""
    debug("file directory: {}".format(os.path.dirname(__file__)))
    file_path = os.path.join(os.path.dirname(__file__), "2000colors.txt")
    with open(file_path) as fh:
        return [line.strip() for line in fh]

def compute_colors(node_df, sequences, num_clusters, cluster_sizes):
    RANDOM_COLORS = get_colors()
    # print(len(RANDOM_COLORS))
    """ Computes Colors for every node in node_list 
    """
    res = ""
    info("Start coloring Taxa")

    excluded = 0
    exclude_small_clusters = False
    n = 1
    # print(cluster_sizes)
    while num_clusters >= len(RANDOM_COLORS) : 


        n += 1
        #warning("More Clusters than colors")
        exclude_small_clusters = True
        excluded = len([1 for x in cluster_sizes if x <= n and x > n-1])


        warning("There are more Clusters than colors: {} Clusters were excluded for being smaller than {}".format(excluded, n))
        num_clusters -= excluded
    factor = len(RANDOM_COLORS) // num_clusters 
    debug("Factor: {} Clusters: {} Colors: {} Min Cluster size: {}".format(factor, num_clusters,len(RANDOM_COLORS),  n+1))
    for seq in sequences:
        seq_s = seq[0:8] # Beachte nur Scount
        if seq_s in node_df.index:
            if exclude_small_clusters:
                if node_df.loc[seq_s,'cluster'] > num_clusters or node_df.loc[seq_s,'cluster-size'] <= n:


                    #res += "    {elem}+sc\n".format(elem = seq) # Singletons and Small clusters are black
                    res += "    {elem}\n".format(elem = seq) # Singletons and Small clusters are black
                else:
                    #res += "    {elem}+{clusternum}[&!color={color}]\n".format(elem=seq, color=RANDOM_COLORS[factor*node_df.loc[seq_s, 'cluster']-1].lower(), clusternum = node_df.loc[seq_s, 'cluster'])
                    res += "    {elem}[&!color={color}]\n".format(elem=seq, color=RANDOM_COLORS[factor*node_df.loc[seq_s, 'cluster']-1].lower())
                    # print("    {elem}+{clusternum}[&!color={color}]\n".format(elem=seq, color=RANDOM_COLORS[factor*node_df.loc[seq_s, 'cluster']-1].lower(), clusternum = node_df.loc[seq_s, 'cluster']))
                    # print("Found", seq_s, "in", node_df.loc[seq_s, 'cluster'])
            else:
                #res += "    {elem}+{clusternum}[&!color={color}]\n".format(elem=seq, color=RANDOM_COLORS[factor*node_df.loc[seq_s, 'cluster']-1].lower(), clusternum = node_df.loc[seq_s, 'cluster'])
                res += "    {elem}[&!color={color}]\n".format(elem=seq, color=RANDOM_COLORS[factor*node_df.loc[seq_s, 'cluster']-1].lower(), clusternum = node_df.loc[seq_s, 'cluster'])
                # print("Found", seq_s, "in", node_df.loc[seq_s, 'cluster'])
        else:
            # res += "    {elem}+nc[&!color=#8d8d8d]\n".format(elem = seq) # Taxa not in any Hivtrace-Computation are white
            res += "    {elem}[&!color=#8d8d8d]\n".format(elem = seq) # Taxa not in any Hivtrace-Computation are white
    info("Finished Coloring")
    return res

def compute_colors_branches(node_df, sequences, newick_str, num_clusters, cluster_sizes):
    RANDOM_COLORS = get_colors()
    """ Computes Colors for every node in node_list 
    """
    res = ""
    newick_res = newick_str
    info("Start coloring Taxa and branches")
    excluded = 0
    exclude_small_clusters = False
    n = 1
    
    # print(cluster_sizes)
    while num_clusters >= len(RANDOM_COLORS) : 


        n += 1
        #warning("More Clusters than colors")
        exclude_small_clusters = True
        excluded = len([1 for x in cluster_sizes if x <= n and x > n-1])


        warning("There are more Clusters than colors: {} Clusters were excluded for being smaller than {}".format(excluded, n))
        num_clusters -= excluded
    factor = len(RANDOM_COLORS) // num_clusters 
    debug("Factor: {} Clusters: {} Colors: {} Min Cluster size: {}".format(factor, num_clusters,len(RANDOM_COLORS),  n+1))
    for seq in sequences:
        seq_s = seq[0:8] # Beachte nur Scount
        newick_pos = newick_res.find(seq) + len(seq)
        if seq_s in node_df.index:
            if exclude_small_clusters:
                if node_df.loc[seq_s,'cluster'] > num_clusters or node_df.loc[seq_s,'cluster-size'] <= n:


                    #res += "    {elem}+sc\n".format(elem = seq) # Singletons and Small clusters are black
                    res += "    {elem}\n".format(elem = seq) # Singletons and Small clusters are black
                else:
                    #res += "    {elem}+{clusternum}[&!color={color}]\n".format(elem=seq, color=RANDOM_COLORS[factor*node_df.loc[seq_s, 'cluster']-1].lower(), clusternum = node_df.loc[seq_s, 'cluster'])
                    res += "    {elem}_C{cluster}[&!color={color}]".format(color=RANDOM_COLORS[factor*node_df.loc[seq_s, 'cluster']-1].lower(), cluster = node_df.loc[seq_s, 'cluster'],elem=seq)
                    newick_res = newick_res[:newick_pos]+"_C{cluster}[&!color={color}]".format(color=RANDOM_COLORS[factor*node_df.loc[seq_s, 'cluster']-1].lower(), cluster = node_df.loc[seq_s, 'cluster'])+newick_res[newick_pos:]
                    # print("    {elem}+{clusternum}[&!color={color}]\n".format(elem=seq, color=RANDOM_COLORS[factor*node_df.loc[seq_s, 'cluster']-1].lower(), clusternum = node_df.loc[seq_s, 'cluster']))
                    # print("Found", seq_s, "in", node_df.loc[seq_s, 'cluster'])
            else:
                #res += "    {elem}+{clusternum}[&!color={color}]\n".format(elem=seq, color=RANDOM_COLORS[factor*node_df.loc[seq_s, 'cluster']-1].lower(), clusternum = node_df.loc[seq_s, 'cluster'])
                res += "    {elem}_C{cluster}[&!color={color}]".format(color=RANDOM_COLORS[factor*node_df.loc[seq_s, 'cluster']-1].lower(), cluster = node_df.loc[seq_s, 'cluster'],elem=seq)
                newick_res = newick_res[:newick_pos]+"_C{cluster}[&!color={color}]".format(color=RANDOM_COLORS[factor*node_df.loc[seq_s, 'cluster']-1].lower(), cluster = node_df.loc[seq_s, 'cluster'])+newick_res[newick_pos:]
                # print("Found", seq_s, "in", node_df.loc[seq_s, 'cluster'])
        else:
            # res += "    {elem}+nc[&!color=#8d8d8d]\n".format(elem = seq) # Taxa not in any Hivtrace-Computation are white
            res += "    {elem}[&!color=#8d8d8d]\n".format(elem = seq) # Taxa not in any Hivtrace-Computation are white
            newick_res = newick_res[:newick_pos]+"[&!color=#8d8d8d]"+newick_res[newick_pos:]
    info("Finished Coloring")
    return res, newick_res

if __name__ == "__main__":
    args = parseCommandline()

    if args.hivtrace:
        info("Read JSON-File")
        CLUSTER_INPUT_FN = args.hivtrace # "data/PWID/hivtrace/mafft_richtigeSeqPWID_allProjects_renamed_mitRefpanel200221.fas.results.json"
        with open(CLUSTER_INPUT_FN, 'r') as CLUSTER_INPUT_FH:
            #CLUSTER_INPUT = json.load(CLUSTER_INPUT_FH)["trace_results"] # for hivtrace json
            CLUSTER_INPUT = json.load(CLUSTER_INPUT_FH) # for csvnetwork json
        nodes = CLUSTER_INPUT["Nodes"]
        num_clusters = CLUSTER_INPUT["Network Summary"]["Clusters"]
        if isinstance(nodes, dict): 
            #nodes['cluster'] = nodes['cluster']["values"] # comment it for hivtrace json
            nodes['cluster'] = nodes['cluster']["values"] # use it for csv json
            NODES_DF = pd.DataFrame.from_dict(nodes).set_index('id')        
        else: NODES_DF = pd.DataFrame(nodes).set_index('id')
        #NODES_DF = pd.DataFrame(nodes).set_index('id')
        cluster_sizes = CLUSTER_INPUT['Cluster sizes']    
        NODES_DF['cluster-size'] = NODES_DF.apply(lambda row: cluster_sizes[row.cluster-1], axis = 1)
        print(NODES_DF)
    elif args.csv:
        info("Read CSV-File")
        # NODES_DF = pd.read_csv(args.csv, sep = '\t').set_index('SeqId')#.set_index('Sequence')
        NODES_DF = pd.read_csv(args.csv, sep = ',').set_index('SeqId')
        cluster_sizes = list(NODES_DF.groupby('ClusterNr').count())#.groupby('cluster').count())
        NODES_DF = NODES_DF.rename(columns = {"ClusterNr":'cluster'})
        num_clusters = NODES_DF['cluster'].max()
    else:
        raise ValueError("This should not have happened!")
    
    if args.treefile:
        TREE_INPUT_FN = args.treefile # "data/PWID/hivtrace/mafft_tree_colored.treefile"
        with open(TREE_INPUT_FN, 'r') as nexus_fh:
            NEXUS_STR = nexus_fh.read()
            
        before,sequences, after = partNexusBy(NEXUS_STR, sep = "taxa")
        # print(before)
        # print("------------------------")
        # print(sequences)
        debug("extracted TAXA")
        split1 = re.split("taxlabels\n", sequences, flags= re.IGNORECASE)
        before_s = split1[0]+"taxlabels\n"
        sequences = split1[1]
        split2 = re.split(";", sequences, flags= re.IGNORECASE)
        sequences = split2[0]
        after_s = ";"+split2[1]
        seq_lst = sequences.split('\n')
        # colored_regex = re.compile('\[&!color=#\w\w\w\w\w\w\]')
        seq_lst = [re.sub(r'\[&!color=#\w\w\w\w\w\w\]', '', seq).strip('\t') for seq in seq_lst if seq != '']
        if len(seq_lst) == 1:
            seq_lst = sequences.split('\n')
        
        info("{} Sequences have been read".format(len(seq_lst)))
        if not args.branches:
            colored_seqs = compute_colors(NODES_DF, seq_lst,num_clusters, cluster_sizes)
            OUT = before + before_s + colored_seqs + after_s +after
        
        if args.branches:
            before_trees,trees, after_trees = partNexusBy(after, sep = "trees")
            colored_seqs, colored_newick = compute_colors_branches(NODES_DF, seq_lst, trees,num_clusters, cluster_sizes)
            OUT = before + before_s + colored_seqs + after_s + before_trees+colored_newick+after_trees
        
        
        # print(OUT)
        OUT_FN = args.outpath or TREE_INPUT_FN+"-colored.treefile"
        with open(OUT_FN, 'w') as fh:
            fh.write(OUT)
        info("Wrote Output to {}".format(os.path.realpath(OUT_FN)))
    if args.annotations:
        NODES_DF.to_csv(args.annotations, sep = '\t')
