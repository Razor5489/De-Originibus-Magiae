"""Build De Originibus Magiae from the editable course in content.json."""
import json, re, math, subprocess
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT=Path(__file__).parent
DATA=json.loads((ROOT/'content.json').read_text())
OUT=ROOT/'pages';OUT.mkdir(exist_ok=True)
ROMAN=['I','II','III','IV','V','VI','VII'];PAGES=[];CHAPTERS=[];SECTIONS=[]
BOOK_TITLE='DE ORIGINIBUS MAGIAE'
INK='#293342';GOLD='#ac9258';MUTED='#8e8a76';PAPER='#f8f4e8';GREEN='#243b56'

def text(x,y,s,size=12,fill=INK,weight='',anchor='',italic=False):
    return f'<text x="{x}" y="{y}" font-family="Georgia, Times New Roman, serif" font-size="{size}" fill="{fill}"'+(f' font-weight="{weight}"' if weight else '')+(f' text-anchor="{anchor}"' if anchor else '')+(' font-style="italic"' if italic else '')+'>'+escape(str(s))+'</text>'

def lines(s,size=12,width=479,bold=False):
    words=s.split();result=[];current=''
    for w in words:
        t=(current+' '+w).strip()
        # Slightly conservative for Georgia on browsers without the same font.
        if stringWidth(t,'Times-Bold' if bold else 'Times-Roman',size)*1.08>width and current:
            result.append(current);current=w
        else:current=t
    if current:result.append(current)
    return result

class Leaf:
    def __init__(self,section,title,subtitle='',kind='theory'):
        self.section=section;self.title=title;self.subtitle=subtitle;self.kind=kind;self.parts=[];self.plain=[section,title];self.y=109
        self.parts.append('<rect width="595" height="842" fill="'+PAPER+'"/><rect width="595" height="842" fill="url(#paper)" opacity=".17"/>')
        self.parts += [text(52,38,'DE ORIGINIBUS MAGIAE',7,MUTED),text(543,38,section.upper(),7,MUTED,anchor='end'),'<path d="M52 48H543" stroke="'+GOLD+'" stroke-width=".7"/>']
        for line in lines(title,26,480,True):self.parts.append(text(52,self.y,line,26,GREEN,'bold'));self.y+=31
        self.y+=1
        if subtitle:self.paragraph(subtitle,11,MUTED,True,16);self.y+=8
    def paragraph(self,s,size=12,fill=INK,italic=False,leading=18):
        self.plain.append(s)
        for line in lines(s,size):
            self.parts.append(text(52,self.y,line,size,fill,italic=italic));self.y+=leading
        self.y+=12
    def heading(self,s):
        self.plain.append(s);self.y+=7
        for line in lines(s,15,480,True):self.parts.append(text(52,self.y,line,15,GREEN,'bold'));self.y+=20
        self.y+=4
    def box(self,label,s):
        ls=lines(s,11,449);height=39+len(ls)*16
        self.parts.append(f'<rect x="52" y="{self.y-12}" width="491" height="{height}" fill="#eee9d8"/><path d="M52 {self.y-12}v{height}" stroke="{GOLD}" stroke-width="1.5"/>')
        self.parts.append(text(66,self.y+3,label.upper(),8,GREEN,'bold'));self.y+=24
        for line in ls:self.parts.append(text(66,self.y,line,11));self.y+=16
        self.y+=22;self.plain.extend([label,s])
    def row(self,left,right):
        self.parts.append('<!--ROW:'+str(len(self.plain))+'-->')
        for line in lines(left,11,417):self.parts.append(text(60,self.y,line,11));self.y+=16
        self.parts.append(text(536,self.y-16,right,10,MUTED,anchor='end'))
        self.parts.append(f'<path d="M60 {self.y-8}H536" stroke="#c3b89b" stroke-dasharray="1 3" stroke-width=".4"/>');self.y+=12
        self.plain.append(left+' '+str(right))
    def finish(self,folio):
        if self.y>758:raise ValueError(f'Overflow {self.title}: {self.y}')
        return svg(''.join(self.parts)+f'<path d="M52 789H543" stroke="#c3b89b" stroke-width=".45"/>'+text(52,804,'HISTORIA MAGIAE · HOGWARTS · MDCCCXC',6.5,MUTED)+text(543,804,folio,8,MUTED,anchor='end'))

def svg(body):
    return '<svg xmlns="http://www.w3.org/2000/svg" width="595" height="842" viewBox="0 0 595 842"><defs><filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter><pattern id="paper" width="595" height="842" patternUnits="userSpaceOnUse"><rect width="595" height="842" filter="url(#grain)" opacity=".17"/></pattern><linearGradient id="leather"><stop stop-color="#0c192c"/><stop offset=".12" stop-color="#294b73"/><stop offset=".6" stop-color="#183657"/><stop offset="1" stop-color="#081426"/></linearGradient></defs>'+body+'</svg>'

def add(leaf,chapter=None):
    idx=len(PAGES);folio=f'{idx+1:02}'
    if chapter:CHAPTERS.append({'title':chapter,'page':idx+1})
    artwork=leaf.finish(folio);name=f'page-{idx+1:02}.svg';(OUT/name).write_text(artwork)
    PAGES.append({'image':'pages/'+name,'text':'DE ORIGINIBUS MAGIAE\n'+'\n'.join(leaf.plain),'title':leaf.title,'folio':folio,'kind':leaf.kind})
    return idx

def cover(back=False):
    body='<rect width="595" height="842" fill="url(#leather)"/><rect width="595" height="842" fill="url(#paper)" opacity=".22"/>'
    for inset in [21,28,35]:body+=f'<rect x="{inset}" y="{inset}" width="{595-2*inset}" height="{842-2*inset}" fill="none" stroke="{GOLD}" stroke-width="{.8 if inset==21 else .4}"/>'
    for x in [35,560]:
        for y in [35,807]:body+=f'<circle cx="{x}" cy="{y}" r="2.5" fill="none" stroke="{GOLD}" stroke-width=".6"/>'
    body+=text(297.5,85,'HOGWARTS · HISTORIA MAGIAE',10,GOLD,anchor='middle')
    body+=text(297.5,171,'DE ORIGINIBUS',31,'#eee4c9','bold','middle')+text(297.5,216,'MAGIAE',43,'#eee4c9','bold','middle')
    body+=text(297.5,258,'Cronache, istituzioni e memoria',16,'#d9cda8',anchor='middle',italic=True)+'<path d="M205 283H390" stroke="'+GOLD+'" stroke-width=".6"/>'
    body+='<g fill="none" stroke="'+GOLD+'" stroke-width="1"><circle cx="297.5" cy="430" r="92"/><circle cx="297.5" cy="430" r="84"/><path d="M254 365h87M254 495h87M263 371c0 35 2 38 34 59-32 21-34 25-34 59M332 371c0 35-2 38-34 59 32 21 34 25 34 59M275 387h45M278 476l20-25 20 25z"/><path d="M233 428h-28m185 0h-28M297 336v-20m0 226v-20"/></g>'
    for y,num in [(361,'I'),(428,'IV'),(495,'VII')]:body+=text(405,y,num,11,GOLD,anchor='middle')
    if back:
        body+=text(297.5,604,'Ricordare è un inizio.',17,'#e1d6b9',anchor='middle',italic=True)+text(297.5,634,'Comprendere è il compito.',17,'#e1d6b9',anchor='middle',italic=True)+text(297.5,694,'THEOBALD AINSWORTH',14,'#e1d6b9',anchor='middle')
    else:
        body+=text(297.5,607,'AD USUM SCHOLASTICUM HOGVARTENSE',9,GOLD,anchor='middle')+text(297.5,675,'Professor Theobald Ainsworth',17,'#e1d6b9',anchor='middle')+text(297.5,746,'FONTI · CONFRONTO · GIUDIZIO',10,GOLD,anchor='middle')
    body+=text(297.5,790,'MDCCCXC',11,GOLD,anchor='middle')
    name=f'page-{len(PAGES)+1:02}.svg';(OUT/name).write_text(svg(body))
    PAGES.append(dict(image='pages/'+name,text=BOOK_TITLE+'\nTheobald Ainsworth\nHogwarts · 1890\nCronache, istituzioni e memoria',title='Quarta di copertina' if back else 'Copertina',folio='Quarta di copertina' if back else 'Copertina',kind='cover'))

cover();CHAPTERS.append(dict(title='Copertina',page=1))
p=Leaf('Praefatio','Il passato e le sue domande','Prefazione di Theobald Ainsworth')
p.paragraph('Il passato non è soltanto un insieme di date. È la storia di persone che agirono senza conoscere il seguito degli avvenimenti, di comunità che costruirono accordi e di istituzioni che cambiarono insieme ai problemi affrontati.')
p.paragraph('Questo libro accompagna sette annualità. Per ciascuna, due settimane comprendono quattro lezioni: due nella prima e due nella seconda. Ogni incontro unisce una spiegazione, alcune nozioni centrali e un lavoro di confronto da svolgere in aula.')
p.heading('Due domande inseparabili')
p.paragraph('Che cosa è accaduto? Su quali testimonianze possiamo sostenerlo? La prima domanda costruisce una ricostruzione; la seconda permette di valutarla. Una risposta prudente non è una risposta debole quando rende visibili i propri limiti.')
p.box('L’orizzonte del volume','Hogwarts, anno 1890. Gli avvenimenti successivi non fanno parte di queste pagine. Le vicende recenti restano aperte quando le fonti non permettono una conclusione.')
p.paragraph('Conservate le domande insieme agli appunti. Una buona lezione non riempie soltanto la memoria: insegna a riconoscere la differenza fra un fatto, un’interpretazione e un racconto.',11)
p.paragraph('Theobald Ainsworth',13,GREEN,True)
add(p,'Prefazione')
p=Leaf('Tabula Materiarum','Indice del volume','Sette annualità · Ventotto lezioni');add(p,'Indice del volume');SECTIONS.append(['Indice',2])
p=Leaf('Cursus Septem Annorum','Il percorso delle due settimane','Quattro incontri prima del passaggio all’anno successivo')
p.heading('Settimana I');p.paragraph('Lezione 1: introdurre il tema e riconoscere il problema storico. Lezione 2: sviluppare il confronto attraverso un caso o una prospettiva differente.')
p.heading('Settimana II');p.paragraph('Lezione 3: collegare gli argomenti a documenti, istituzioni e nozioni. Lezione 4: applicare il metodo e raccogliere il ripasso dell’annualità.')
p.box('Una lezione di quindici minuti','2 minuti: domanda iniziale. 5: spiegazione e nozioni. 5: confronto o attività. 3: domanda conclusiva e motivazione della risposta.')
p.heading('Tre pagine, un solo incontro');p.paragraph('La pagina di spiegazione, quella delle nozioni e la scheda per l’aula appartengono alla stessa lezione. Il numero delle pagine non aggiunge incontri al calendario.')
p.paragraph('Gli appunti permettono di riprendere i temi delle lezioni. Recuperi e verifiche seguono le disposizioni della scuola.',11)
add(p,'Il percorso delle due settimane')
p=Leaf('Methodus','Come si legge una fonte','Il metodo che accompagna tutte le annualità')
for h,t in [('Identificare','Chi ha prodotto la testimonianza, quando e per quale destinatario? Un’informazione sulla provenienza aiuta a comprendere il punto di vista.'),('Descrivere','Che cosa afferma davvero il testo o che cosa mostra il reperto? Prima dell’interpretazione, distinguere gli elementi osservabili.'),('Confrontare','Quali altre fonti offrono riscontri? Due testi dipendenti dalla stessa notizia non sono necessariamente due conferme autonome.'),('Concludere con misura','Separare ciò che è sostenuto dalle prove, ciò che rimane un’ipotesi e ciò che non sappiamo. Un limite dichiarato rende controllabile il ragionamento.')]:p.heading(h);p.paragraph(t,11.5,leading=17)
p.box('Autentico non significa infallibile','Un documento può essere realmente opera del suo autore e contenere errori, opinioni o informazioni incomplete.')
add(p,'Il metodo dello storico');SECTIONS.append(['Metodo',4])

ANNUAL=[];LESSON_POS={}
for yi,y in enumerate(DATA['years']):
    year=yi+1;annual=[l for l in DATA['lessons'] if l['year']==year]
    p=Leaf('Anno '+ROMAN[yi],y['name'],'Annus '+['Primus','Secundus','Tertius','Quartus','Quintus','Sextus','Septimus'][yi],kind='divider')
    p.y+=36;p.parts.append(text(297.5,p.y,ROMAN[yi],100,GREEN,anchor='middle'));p.y+=60
    p.paragraph(y['goal'],16,GREEN,True,24)
    p.box('L’annualità','Due settimane. Due lezioni ogni settimana. Quattro incontri, ciascuno con spiegazione, nozioni e lavoro in aula.')
    add(p,'Anno '+ROMAN[yi]+' · '+y['name']);SECTIONS.append([ROMAN[yi],len(PAGES)-1])
    ANNUAL.append((len(PAGES),year))
    add(Leaf('Anno '+ROMAN[yi],'Il programma dell’anno','Due settimane · Quattro lezioni'))
    for l in annual:
        section=f"Anno {ROMAN[yi]} · Settimana {ROMAN[l['week']-1]}"
        LESSON_POS[(year,l['meeting'])]=len(PAGES)+1
        p=Leaf(section,l['title'],l['subtitle'])
        p.parts.insert(3,text(52,72,f"LECTIO {l['meeting']} · SPIEGAZIONE",8,GOLD))
        for paragraph in l['theory']:p.paragraph(paragraph,12,leading=18)
        p.paragraph('Riferimento: '+l['source'],8.5,MUTED,False,12)
        add(p,f"{ROMAN[yi]}.{l['meeting']} · {l['title']}")
        p=Leaf(f"Anno {ROMAN[yi]} · Lectio {l['meeting']}",'Le nozioni da ricordare',l['title'])
        for label,body in l['notions']:p.heading(label);p.paragraph(body)
        p.box('Domanda da discutere',l['opening'])
        p.paragraph('Per motivare una risposta, collegare il concetto a un esempio della spiegazione. Un’opinione ragionata può essere discussa; una notizia nuova richiede una fonte.',11,MUTED)
        add(p);PAGES[-1]['title']=l['title']+' · Nozioni'
        p=Leaf(f"Anno {ROMAN[yi]} · Lectio {l['meeting']}",'Il confronto in aula',l['title']+' · Scheda della lezione')
        p.box('Apertura',l['opening'])
        for i,step in enumerate(l['steps']):p.paragraph(f'{i+1}. '+step,11.5,leading=17)
        p.heading('Domanda di ripasso');p.paragraph(l['question'],11.5,leading=17)
        p.heading('Risposta ragionata');p.paragraph(l['answer'],11,leading=16)
        if l['meeting']==4:p.paragraph('Concluso il ciclo di due settimane. '+('Si prosegue con l’anno '+ROMAN[year]+'.' if year<7 else 'Il percorso dei sette anni è concluso.'),9,GOLD)
        add(p);PAGES[-1]['title']=l['title']+' · Attività e ripasso'

TIMELINE=[('382','Patto di Caer Daran: obblighi comuni.'),('417','Tavole di Morcant: conservazione scritta.'),('463–474','Contesa dei Sette Pozzi.'),('Intorno al 990','Fondazione di Hogwarts.'),('1692','Statuto Internazionale di Segretezza.'),('1708','Concordato di Westminster Magico: Ministero britannico.'),('1752','Carta della Libertà della Bacchetta.'),('1778','Riforma Hawthorne.'),('1819','Decreto di Rappresentanza.'),('1824','Dimissioni di Lucien Barrow.'),('1841','Nascita di Alaric Wren.'),('1863','Carta della Ricerca Responsabile.'),('1871','Crisi dei Calderoni.'),('1883','Wren propone l’ipotesi del lento mutamento della magia.'),('1885','Caso Greywick.'),('14 novembre 1887','Ultima presenza confermata di Wren.'),('3 dicembre 1887','Apertura formale del Caso Wren.'),('1890','Orizzonte presente del volume: il caso resta irrisolto.')]
SECTIONS.append(['Cronologia',len(PAGES)])
for part in range(2):
    p=Leaf('Chronologia', 'Le date e i passaggi', 'Dal programma adottato · Tavola '+ROMAN[part])
    for date,description in TIMELINE[part*9:part*9+9]:p.heading(date);p.paragraph(description,11,leading=16)
    p.paragraph('Una cronologia ordina gli eventi. Il loro ordine non dimostra, da solo, il rapporto fra le cause.',10,MUTED)
    add(p,'Cronologia · '+ROMAN[part])
p=Leaf('Lexicon','Le parole dello storico','Un lessico da usare con precisione')
for label,body in [('Fonte','Testimonianza materiale, scritta o orale sulla quale si costruisce una ricerca.'),('Fatto e interpretazione','Un accadimento sostenuto dalle prove si distingue dalla spiegazione che ne viene proposta.'),('Tradizione','Racconto o pratica trasmessi nel tempo; da studiare nella loro conservazione e trasformazione.'),('Istituzione','Organizzazione di funzioni, regole e competenze riconosciute.'),('Consuetudine','Pratica condivisa che può precedere o accompagnare una norma scritta.'),('Causalità','Rapporto da dimostrare tra fenomeni: non coincide con la semplice successione delle date.'),('Incertezza','Limite della ricostruzione da dichiarare; non autorizza a scegliere una spiegazione priva di prove.')]:p.heading(label);p.paragraph(body,11,leading=16)
add(p,'Lessico essenziale');SECTIONS.append(['Lessico',len(PAGES)-1])
p=Leaf('Nota dell’edizione','I materiali e il percorso','Come sono state organizzate queste pagine')
p.heading('Il programma principale');p.paragraph('Il «Programma storia della magia» guida temi, cronologia britannica e vicende contemporanee. I quattordici nuclei del programma sono sviluppati in ventotto incontri: quattro per ciascuno dei sette anni.',11)
p.heading('Gli approfondimenti antichi');p.paragraph('Il «Manuale di SDM – BWGDR» offre spunti su origini, civiltà antiche, trasmissione del sapere e tradizioni. Gli argomenti vengono selezionati e rielaborati secondo il percorso, senza estendere l’orizzonte oltre il 1890.',11)
p.heading('Le differenze fra i materiali');p.paragraph('Per la nascita del Ministero britannico viene adottato il 1708 del programma principale. Le date e le istituzioni della cronologia seguono quel programma. Riferimenti appartenenti a tradizioni differenti non vengono sovrapposti come se fossero un’unica ricostruzione.',11)
p.heading('Documenti per imparare');p.paragraph('I fascicoli del 1732 e del 1874 e gli altri esempi dichiarati immaginari sono materiali di esercitazione. Non aggiungono avvenimenti alla storia della comunità.',11)
p.paragraph('Edizione di Theobald Ainsworth · Hogwarts · 1890',10,GOLD)
add(p,'I materiali del volume');SECTIONS.append(['Fonti',len(PAGES)-1])
p=Leaf('Finis','Ricordare è un inizio.','Comprendere è il compito.')
p.y=370;p.paragraph('Sette annualità. Quattordici settimane. Ventotto lezioni per collegare origini, istituzioni e responsabilità della memoria.',19,GREEN,True,29)
p.y+=42;p.paragraph('Theobald Ainsworth',15,GREEN);p.paragraph('Hogwarts · MDCCCXC',10,GOLD);add(p,'Finis')
name=f'page-{len(PAGES)+1:02}.svg';body='<rect width="595" height="842" fill="#17293f"/>'
for i in range(38):
    yy=i*24;body+=f'<path d="M-40 {yy} Q130 {yy-80} 298 {yy+9}T650 {yy-5}" fill="none" stroke="{["#9a8659","#6f8299","#354e69"][i%3]}" stroke-width="{1+i%4}" opacity=".5"/>'
(OUT/name).write_text(svg(body));PAGES.append(dict(image='pages/'+name,text='Controguardia posteriore marmorizzata.',title='Controguardia posteriore',folio='Controguardia',kind='endpaper'))
cover(True)

def replace_leaf(index,p):
    (OUT/f'page-{index+1:02}.svg').write_text(p.finish(f'{index+1:02}'))
    PAGES[index]['text']=BOOK_TITLE+'\n'+'\n'.join(p.plain)
for index,year in ANNUAL:
    p=Leaf('Anno '+ROMAN[year-1],'Il programma dell’anno','Due settimane · Quattro lezioni')
    for l in [l for l in DATA['lessons'] if l['year']==year]:
        if l['meeting'] in [1,3]:p.heading('Settimana '+ROMAN[l['week']-1])
        p.row(f"Lezione {l['meeting']} · {l['title']}",str(LESSON_POS[(year,l['meeting'])]))
        p.paragraph(l['subtitle'],10,MUTED,True,15)
    p.box('Traguardo',DATA['years'][year-1]['goal']);p.paragraph('Le tre pagine di ciascun incontro formano un solo percorso: spiegazione, nozioni e confronto in aula.',11)
    replace_leaf(index,p)
chapter_pages={c['title']:c['page'] for c in CHAPTERS}
p=Leaf('Tabula Materiarum','Indice del volume','Sette annualità · Ventotto lezioni')
for title in ['Prefazione','Il percorso delle due settimane','Il metodo dello storico']+['Anno '+ROMAN[i]+' · '+y['name'] for i,y in enumerate(DATA['years'])]+['Cronologia · I','Cronologia · II','Lessico essenziale','I materiali del volume','Finis']:p.row(title,str(chapter_pages[title]))
p.paragraph('L’indice ricercabile permette di trovare una singola lezione, un nome o una data. Le linguette laterali aprono le annualità e le tavole finali.',10,MUTED)
replace_leaf(2,p)
assert len(PAGES)==110,len(PAGES)
assert len(DATA['lessons'])==28
for item in PAGES:item['image']+='?v=20261121-1'
packed={'pages':PAGES,'chapters':CHAPTERS,'sections':SECTIONS}
for cover_index in (0,len(PAGES)-1):PAGES[cover_index]['image']=PAGES[cover_index]['image'].split('?')[0]+'?v=20261121-cover2'
(ROOT/'book-data.json').write_text(json.dumps(packed,ensure_ascii=False,indent=2)+'\n')
index=ROOT/'index.html'
embedded=json.dumps(packed,ensure_ascii=False).replace('</','<\\/')
index.write_text(re.sub(r'(<script id="book-data" type="application/json">).*?(</script>)',lambda m:m[1]+embedded+m[2],index.read_text(),flags=re.S))
print(f'{len(PAGES)} pagine A4, {len(DATA["lessons"])} lezioni, tutti i margini rispettati.')
