#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pickle, os,sys
if __name__ == "__main__":    
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from benchmark.avg_res import ft, curves, types, steps, dataPath

if os.path.isfile(dataPath + '/results.ser.txt'):
    with open(dataPath + '/results.ser.txt', 'rb') as f:
        results = pickle.load(f)
else:
    print("no results.ser.txt ... exiting")
    exit()

#curves = [ 'SS512', 'MNT159'] 
#curves = [ 'SS512', 'MNT159', 'SS1024', 'MNT201', 'MNT224']
#types = ['bsw07', 'lw08', 'waters09', 'rw12', 'ot12']
#steps = [1, 10, 50, 100, 500, 1000]    


for curve in curves:
    for tp in types:
        print('Curve ', curve, 'Type ', tp)
        for i in steps:
            k = 'm' + str(i)
            if k in results[curve][tp]:
                print(k + ": ", tp, ' Setup: ', ft(results[curve][tp][k]['stp']), ' Keygen: ', ft(results[curve][tp][k]['kgn']), ' Encrypt: ', ft(results[curve][tp][k]['enc']), ' Decrypt: ', ft(results[curve][tp][k]['dec']) )
                t = 't' + str(i)    
                print(t + ": ", tp, ' Setup: ', ft(results[curve][tp][t]['stp']), ' Keygen: ', ft(results[curve][tp][t]['kgn']), ' Encrypt: ', ft(results[curve][tp][t]['enc']), ' Decrypt: ', ft(results[curve][tp][t]['dec']) )
            else:
                print("missing key:", curve, tp, k, " - won't print")
                exit()


#### defs
def writeTableMT(f, results, title, label):
    methods = ['kgn', 'enc', 'dec']
    lSteps = len(steps)       
    for curve in curves:
        f.write(r'\begin{table}[ht]\centering\resizebox{\textwidth}{!}{\begin{tabular}{|c|c|r|r|r|r|r|r|} \hline')
        f.write('\\multirow{2}{*}{Scheme} & \\multirow{2}{*}{\\#attr} & \\multicolumn{2}{c|}{$\\mathsf{KeyGen}$} & \\multicolumn{2}{c|}{$\\mathsf{Encrypt}$} & \\multicolumn{2}{c|}{$\\mathsf{Decrypt}$}\\\\ \\cline{3-8} \n')
        f.write('&& M & T & M & T & M & T  \\\\ ')                
        f.write('\\hline\n')
        for tp in types:
            f.write('\\multirow{' + str(lSteps) + '}{*}{' + tp + '} ')        
            for i in steps:
                f.write('&' + str(i))
                k = 'm' + str(i)
                t = 't' + str(i)    
                for meth in methods:
                    f.write('&' + ft(results[curve][tp][k][meth]))
                    f.write('&' + ft(round(results[curve][tp][t][meth], 4)))
                f.write(' \\\\\n')
            f.write('\\hline\n')
            #f.write('\\cline{2-9}\n')
                
        f.write(r'\end{tabular}}\caption{' + str("Curve: " + curve + ". " + title) + '}\label{table:' + str(label + "_" + curve) + '} \end{table} ' + '\n')
def writeTableTK(f, results, title, label):
    methods = ['kgn', 'enc', 'dec']
    mems = ['sk', 'ct']
    lSteps = len(steps)
            
    for curve in curves:
        f.write(r'\begin{table}[ht]\centering\resizebox{\textwidth}{!}{\begin{tabular}{|c|c|r|r|r|r|r|} \hline')
        f.write('\n$\\mathsf{Scheme}$ & $\\mathsf{\\#attr}$ & $\\mathsf{SK\\ [KB]}$ & $\\mathsf{CT\\ [KB]}$ & $\\mathsf{KeyGen\\ [s]}$ & $\\mathsf{Encrypt\\ [s]}$ & $\\mathsf{Decrypt\\ [s]}$ \\\\ \n')
        f.write('\\hline\n')

        for tp in types:
            f.write('\\multirow{' + str(lSteps) + '}{*}{' + tp + '} ')        
            for i in steps:
                f.write('&' + str(i))
                k = 'm' + str(i)
                t = 't' + str(i)    
                for m in mems:
                    f.write('&' + ft(round(results[curve][tp][k][m]/1000.0,4)))
                for meth in methods:                    
                    f.write('&' + ft(round(results[curve][tp][t][meth], 4)))
                f.write(' \\\\\n')
            f.write('\\hline\n')
            #f.write('\\cline{2-8}\n')
                
        f.write(r'\end{tabular}}\caption{' + str("Curve: " + curve + ". " + title) + '}\label{table:' + str(label + "_" + curve) + '} \end{table} ' + '\n')    
def writeTableSetup(f, results, title, label):
    f.write(r'\begin{table}[ht]\centering\resizebox{\textwidth}{!}{\begin{tabular}{|c|c|r|r|r|r|r|} \hline')
    f.write('\n$\\mathsf{Curve}$ & $\\mathsf{Scheme}$ & $\\mathsf{PP}\\ [KB]$ & $\\mathsf{MK}\\ [KB]$ & $\\mathsf{Setup\\ [KB]}$ & $\\mathsf{Setup\\ [s]}$ \\\\ \n')
        
    lTypes = len(types)
    for curve in curves:
        f.write('\\hline\n')
        f.write('\\multirow{' + str(lTypes) + '}{*}{' + curve + '}')
        for tp in types:
            k = 'm1'
            t = 't1'    

            f.write('& ' + tp)            
            f.write('&' + ft(round(results[curve][tp][k]['pp']/1000.0,4)))
            f.write('&' + ft(round(results[curve][tp][k]['mk']/1000.0,4)))
                           
            f.write('&' + ft(results[curve][tp][k]['stp']))
            f.write('&' + ft(round(results[curve][tp][t]['stp'], 4)) + ' \\\\\n')            
            f.write('\\cline{2-6}\n')
            #f.write('\\hline\n')
                
        f.write('\\hline\n')
    f.write(r'\end{tabular}}\caption{' + str(title) + '}\label{table:' + str(label) + '} \end{table} ' + '\n')    
#### end defs


# writing results in a latex file 
f = open(dataPath + '/results.tex','w')

f.write(r'''        
\documentclass[twoside,11pt,titlepage,a4paper,english,bibliography=totocnumbered,listof=numbered]{scrbook}

% Template Style
\include{style}


\usepackage[utf8]{inputenc}
\usepackage{amsfonts,amsmath,amssymb,amsthm}
\usepackage{wrapfig}
\usepackage{selinput}
\usepackage{makecell}
\usepackage{graphicx}
\usepackage{hyperref}

\begin{document}
\center
{\Large Results!}\\
''')

writeTableSetup(f, results, r'Encryption-types comparison in memory consumption PP, MK, setup() and runtime vor setup().', 'abe_setup')
writeTableMT(f, results, r'Encryption-types comparison in memory consumption and runtime. M in [KB], T in [s]', 'abe_mem_run')
writeTableTK(f, results, r'Encryption-types comparison in runtime and key-size.', 'abe_run')

f.write('\\end{document}\n')
f.close()
print('./results.tex updated')
