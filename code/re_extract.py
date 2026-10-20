import os, pymupdf, glob
STAGE='E:/Research-Staging/14-fintech-emissions-meta/pdfs/'; TXT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data','fulltext')
n=0
for f in glob.glob(STAGE+'*.pdf'):
    name=os.path.basename(f)[:-4]
    try:
        d=pymupdf.open(f); t=''
        for i,p in enumerate(d): t+=f'\n\n=====PAGE {i+1}=====\n'+p.get_text()
        open(os.path.join(TXT,name+'.txt'),'w',encoding='utf-8').write(t); n+=1
    except Exception as e: print('fail',name,e)
print('re-extracted',n)
