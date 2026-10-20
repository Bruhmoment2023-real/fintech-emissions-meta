import sys,os,re; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from netcache import get
Q=['meta-analysis fintech carbon emissions','meta-analysis digital finance carbon emissions','meta-regression financial development carbon emissions','meta-analysis financial inclusion carbon emissions',
 'systematic review fintech environmental sustainability empirical evidence','meta-analysis green finance carbon emissions','meta-analysis digital economy carbon emissions','publication bias environmental Kuznets curve meta-analysis',
 'systematic review digital inclusive finance carbon','meta-analysis financial technology environmental quality']
for q in Q:
    s,j=get('https://api.crossref.org/works',params={'query.bibliographic':q,'rows':8,'filter':'from-pub-date:2015-01-01','select':'DOI,title,issued,container-title,author,type'})
    print('##',q)
    for i in (j['message']['items'] if s==200 else []):
        print('  ',i['DOI'],'|',(i.get('title') or [''])[0][:120],'|',(i.get('issued',{}).get('date-parts') or [[None]])[0][0],'|',(i.get('container-title') or [''])[0][:30])
